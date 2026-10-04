"""Export real pinned HerBERT; compare PyTorch, ONNX float and INT8 before packaging."""
import argparse
import importlib.metadata
import json
import os
import platform
import resource
import shutil
import sys
import time
from pathlib import Path

from contract_mobile import (ROOT, VERSION, MODEL, ORT_VERSION, INPUTS, OUTPUTS,
                             FLOAT_ATOL, pack_rows, prepare, compare, verify_freeze,
                             canonical, sha)
sys.path.insert(0, str(ROOT.parent/'ai_compare_v5'))
import run_model as original

def wrapper_class(torch):
    class MaskedCandidateScorer(torch.nn.Module):
        def __init__(self, model):
            super().__init__()
            self.bert = model.bert
            self.head = model.cls.predictions

        def forward(self, input_ids, attention_mask, target_positions, target_ids, target_mask):
            hidden = self.bert(input_ids=input_ids, attention_mask=attention_mask,
                               return_dict=False)[0]
            selected = torch.gather(hidden, 1,
                                    target_positions.unsqueeze(-1).expand(-1, -1, hidden.shape[-1]))
            log_probabilities = torch.log_softmax(self.head(selected), dim=-1)
            values = torch.gather(log_probabilities, -1, target_ids.unsqueeze(-1)).squeeze(-1)
            total = (values*target_mask).sum(-1)
            return total/target_mask.sum(-1), total
    return MaskedCandidateScorer

def candidate_batch(row, tokenizer):
    if row['condition'] != 'plain' or any(c['sourceText'] for c in row['candidates']):
        raise ValueError('metadata outside mobile plain trial')
    # Same plain context for all candidates; truncate only the oldest words if needed.
    context = row['context']
    removed = 0
    while True:
        rows = []
        for c in row['candidates']:
            ids, targets, positions = original.mlm_inputs(row, context, c, tokenizer)
            rows.append({'surface':c['surface'], 'input_ids':ids,
                         'target_ids':targets, 'target_positions':positions})
        if max(len(r['input_ids']) for r in rows) <= 512:
            break
        words = context.split(maxsplit=1)
        if len(words) < 2:
            raise ValueError('target exceeds token budget')
        removed += len(context)-len(words[1])
        context = words[1]
    if removed:
        raise ValueError('conversion trial must preserve the archived untruncated context')
    return rows, pack_rows(rows, tokenizer.pad_token_id)

def ort_session(path, ort):
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.log_severity_level = 3
    session = ort.InferenceSession(str(path), sess_options=options, providers=['CPUExecutionProvider'])
    if tuple(i.name for i in session.get_inputs()) != INPUTS or tuple(o.name for o in session.get_outputs()) != OUTPUTS:
        raise ValueError('exported graph signature differs')
    if any(i.type != ('tensor(float)' if i.name == 'target_mask' else 'tensor(int64)')
           for i in session.get_inputs()):
        raise ValueError('exported input types differ')
    return session

def write(path, data):
    path.write_bytes(canonical(data)+b'\n')

def run(out):
    import numpy as np
    import onnx
    import onnxruntime as ort
    from onnxruntime.quantization import quantize_dynamic, QuantType
    from onnxruntime.quantization.shape_inference import quant_pre_process
    if ort.__version__ != ORT_VERSION:
        raise ValueError('ORT must match verified Android runtime')
    frozen = verify_freeze()
    cases, entries, requests, archived = prepare()
    out.mkdir(parents=True, exist_ok=False)
    report_dir = out/'reports'
    report_dir.mkdir()
    working = out/'working'
    working.mkdir()
    model, tokenizer, torch, loading, load_seconds = original.load('herbert')
    if not tokenizer.is_fast:
        raise ValueError('fast tokenizer required')
    weight_manifest = original.files_manifest(MODEL)
    # Explicit attention implementation for portable ops. Archived scores gate this change too.
    model.set_attn_implementation('eager')
    wrapper = wrapper_class(torch)(model).eval()
    prepared = [(r, *candidate_batch(r, tokenizer)) for r in requests]
    sample = prepared[0][2]
    tensors = tuple(torch.tensor(sample[name], dtype=torch.float32 if name == 'target_mask' else torch.long)
                    for name in INPUTS)
    float_path = working/'herbert-wwm-fp32.onnx'
    int8_path = working/'herbert-wwm-int8.onnx'
    dynamic = {name:{0:'candidates', 1:'targets' if name.startswith('target_') else 'sequence'}
               for name in INPUTS}
    dynamic.update({name:{0:'candidates'} for name in OUTPUTS})
    with torch.inference_mode():
        torch.onnx.export(wrapper, tensors, str(float_path), input_names=list(INPUTS),
                          output_names=list(OUTPUTS), dynamic_axes=dynamic,
                          opset_version=17, dynamo=False, do_constant_folding=True)
    onnx.checker.check_model(str(float_path), full_check=True)
    graph = onnx.load(str(float_path), load_external_data=False)
    if any(t.data_location == onnx.TensorProto.EXTERNAL for t in graph.graph.initializer):
        raise ValueError('single-file model required')
    del graph
    processed = working/'herbert-wwm-preprocessed.onnx'
    quant_pre_process(str(float_path), str(processed), skip_optimization=True,
                     skip_symbolic_shape=True)
    quantize_dynamic(str(processed), str(int8_path), per_channel=True, reduce_range=False,
                     weight_type=QuantType.QInt8, op_types_to_quantize=['MatMul', 'Gemm'],
                     extra_options={'MatMulConstBOnly':True})
    onnx.checker.check_model(str(int8_path), full_check=True)
    quant_graph = onnx.load(str(int8_path), load_external_data=False)
    quantized_weights = sum(t.data_type == onnx.TensorProto.INT8 for t in quant_graph.graph.initializer)
    if quantized_weights == 0:
        raise ValueError('quantization did not change any weight')
    del quant_graph
    float_session = ort_session(float_path, ort)
    quant_session = ort_session(int8_path, ort)
    scores = {'torchBatched':{}, 'onnxFloat':{}, 'onnxInt8':{}}
    latencies = {'torchBatched':[], 'onnxFloat':[], 'onnxInt8':[]}
    vectors = []
    for row, candidates, packed in prepared:
        tx = tuple(torch.tensor(packed[name], dtype=torch.float32 if name == 'target_mask' else torch.long)
                   for name in INPUTS)
        nx = {name:np.asarray(packed[name], dtype=np.float32 if name == 'target_mask' else np.int64)
              for name in INPUTS}
        for name, session in [('torchBatched', None), ('onnxFloat', float_session), ('onnxInt8', quant_session)]:
            began = time.perf_counter()
            if session is None:
                with torch.inference_mode():
                    means, sums = wrapper(*tx)
                means, sums = means.tolist(), sums.tolist()
            else:
                means, sums = session.run(list(OUTPUTS), nx)
                means, sums = means.tolist(), sums.tolist()
            latencies[name].append((time.perf_counter()-began)*1000)
            if len(means) != len(candidates) or len(sums) != len(candidates):
                raise ValueError('wrong result cardinality')
            for i, c in enumerate(candidates):
                if not np.isfinite(means[i]) or not np.isfinite(sums[i]):
                    raise ValueError('nonfinite result')
                if abs(sums[i]/len(c['target_ids'])-means[i]) > FLOAT_ATOL:
                    raise ValueError('mean/sum mismatch')
            scores[name][row['id']] = {c['surface']:means[i] for i,c in enumerate(candidates)}
        # Real-token fixtures let the Android adapter verify its exact feed and output.
        vectors.append({'id':row['id'], 'surfaces':[c['surface'] for c in candidates],
                        'inputs':packed, 'onnxFloat':scores['onnxFloat'][row['id']],
                        'onnxInt8':scores['onnxInt8'][row['id']]})
    comparisons = {name:compare(requests, cases, entries, archived, values)
                   for name, values in scores.items()}
    parity = comparisons['torchBatched']['floatParityPassed'] and comparisons['onnxFloat']['floatParityPassed']
    quant_ok = comparisons['onnxInt8']['quantizationPreservationPassed']
    tokenizer_path = working/'tokenizer.json'
    tokenizer.backend_tokenizer.save(str(tokenizer_path))
    backend = json.loads(tokenizer_path.read_text())
    strings = {'' , 'łódź', 'Łódź', 'łodzi', 'Łodzi', 'malina', 'Malina', 'warszawska',
               'Warszawska', '3. Ale lub tutaj', 'zażółć gęślą jaźń', 'a\u0301',
               'A\tB\nC', 'a\u00a0b', 'a\u200bb', '🚤 🏙️', '中 文',
               'foo-bar „Łódź”', 'a\x00b', '<mask> <s> </s> <unk> <pad>'}
    strings.update(r['context'] for r in requests)
    strings.update(c['surface'] for r in requests for c in r['candidates'])
    token_vectors = [{'text':s, 'ids':tokenizer.encode(s, add_special_tokens=False)} for s in sorted(strings)]
    write(report_dir/'tokenizer-conformance.json', {'schemaVersion':1, 'model':MODEL, 'vectors':token_vectors})
    write(report_dir/'android-score-vectors.json', {'schemaVersion':1, 'protocol':VERSION, 'vectors':vectors})
    import statistics
    timing = {name:{'p50Ms':statistics.median(v), 'p95Ms':sorted(v)[max(0, int(len(v)*.95+.999)-1)]}
              for name,v in latencies.items()}
    report = {'protocol':VERSION, 'codeCommit':os.environ.get('GITHUB_SHA', 'local-uncommitted'),
              'freezeSha256':sha(ROOT/'freeze-manifest.json'), 'model':MODEL,
              'modelFiles':weight_manifest, 'loadingInfo':loading, 'loadSeconds':load_seconds,
              'requests':len(requests), 'requestPayloadSha256':frozen['requestPayloadSha256'],
              'comparisons':comparisons, 'hostLatenciesIncludingFeedPreparationExcluded':timing,
              'peakHostRssMiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
              'quantizedWeightTensors':quantized_weights,
              'models':{name:{'bytes':p.stat().st_size,'sha256':sha(p)} for name,p in
                        [('float',float_path),('int8',int8_path)]},
              'environment':{'python':sys.version,'platform':platform.platform(),
                             'packages':{p:importlib.metadata.version(p) for p in
                                         ['torch','transformers','tokenizers','numpy','onnx','onnxruntime']}},
              'floatParityPassed':parity, 'quantizationPreservationPassed':quant_ok,
              'candidateBundleCreated':parity and quant_ok, 'phoneReady':False,
              'independentQualityValidated':False}
    write(report_dir/'conversion-report.json', report)
    write(report_dir/'scores.json', scores)
    if parity and quant_ok:
        bundle = out/'candidate-bundle'
        bundle.mkdir()
        shutil.copy2(int8_path, bundle/'model.onnx')
        shutil.copy2(tokenizer_path, bundle/'tokenizer.json')
        shutil.copy2(ROOT/'NOTICE.txt', bundle/'NOTICE.txt')
        shutil.copy2(report_dir/'android-score-vectors.json', bundle/'android-score-vectors.json')
        shutil.copy2(report_dir/'tokenizer-conformance.json', bundle/'tokenizer-conformance.json')
        write(bundle/'manifest.json', {'schemaVersion':1, 'protocol':VERSION, 'model':MODEL,
              'onnxRuntimeVersion':ORT_VERSION, 'scoring':'whole-word-mask-mean-log-probability',
              'inputNames':list(INPUTS), 'outputNames':list(OUTPUTS), 'maxSequence':512,
              'maxCandidates':12, 'maxTargetTokens':32,
              'normalizer':backend.get('normalizer'), 'preTokenizer':backend.get('pre_tokenizer'),
              'specialTokenIds':{'cls':tokenizer.cls_token_id,'sep':tokenizer.sep_token_id,
                                 'mask':tokenizer.mask_token_id,'pad':tokenizer.pad_token_id,
                                 'unk':tokenizer.unk_token_id},
              'floatParityPassed':True,'quantizationPreservationPassed':True,'phoneReady':False,
              'files':{p.name:{'bytes':p.stat().st_size,'sha256':sha(p)} for p in sorted(bundle.iterdir())}})
    lines = ['# HerBERT mobile conversion v1', '',
             f'Float parity: {parity}; INT8 preservation: {quant_ok}; phone ready: false.', '',
             f'Requests: {len(requests)}. ORT {ORT_VERSION}; CPU two threads.', '',
             'All group counts and paired changes: conversion-report.json. No new independent quality claim.', '',
             '| Graph | Size MiB | Host p50 / p95 ms |', '|---|---:|---:|']
    for name,path,measure in [('FP32',float_path,'onnxFloat'),('INT8',int8_path,'onnxInt8')]:
        lines.append(f"| {name} | {path.stat().st_size/1024**2:.1f} | {timing[measure]['p50Ms']:.1f} / {timing[measure]['p95Ms']:.1f} |")
    (report_dir/'SUMMARY.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))
    if not parity:
        raise RuntimeError('FP32/batching parity gate failed; reports retained, bundle not created')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, required=True)
    run(parser.parse_args().out)
