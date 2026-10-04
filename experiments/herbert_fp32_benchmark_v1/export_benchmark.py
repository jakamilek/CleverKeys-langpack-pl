"""Explicit FP32 benchmark stage; leaves the previous failed INT8 gate unchanged."""
import argparse
import importlib.metadata
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT.parent/'herbert_mobile_v1'))
from contract_mobile import (MODEL, ORT_VERSION, INPUTS, OUTPUTS, prepare, compare,
                             verify_freeze, canonical, sha)
from export_validate import wrapper_class, candidate_batch, ort_session, write, original
from portable import VERSION, FP32_SHA, MODEL_BYTES, export_tables, PortableTokenizer, conformance_strings

def run(out):
    import numpy as np
    import onnx
    import onnxruntime as ort
    if ort.__version__ != ORT_VERSION or importlib.metadata.version('tokenizers') != '0.22.2':
        raise ValueError('runtime identity differs')
    stage = json.loads((ROOT/'freeze-manifest.json').read_text())
    for name, identity in stage['files'].items():
        if sha(ROOT.parent.parent/name) != identity:
            raise ValueError('benchmark source freeze mismatch: '+name)
    frozen = verify_freeze()
    cases, entries, requests, archived = prepare()
    out.mkdir(parents=True, exist_ok=False)
    reports, bundle = out/'reports', out/'bundle'
    reports.mkdir(); bundle.mkdir()
    model, tokenizer, torch, loading, load_seconds = original.load('herbert')
    if not tokenizer.is_fast:
        raise ValueError('original fast tokenizer required')
    model.set_attn_implementation('eager')
    wrapper = wrapper_class(torch)(model).eval()
    prepared = [(r,*candidate_batch(r,tokenizer)) for r in requests]
    sample = prepared[0][2]
    tensors = tuple(torch.tensor(sample[name], dtype=torch.float32 if name == 'target_mask' else torch.long)
                    for name in INPUTS)
    path = bundle/'model.onnx'
    dynamic = {name:{0:'candidates',1:'targets' if name.startswith('target_') else 'sequence'} for name in INPUTS}
    dynamic.update({name:{0:'candidates'} for name in OUTPUTS})
    with torch.inference_mode():
        torch.onnx.export(wrapper,tensors,str(path),input_names=list(INPUTS),output_names=list(OUTPUTS),
                          dynamic_axes=dynamic,opset_version=17,dynamo=False,do_constant_folding=True)
    onnx.checker.check_model(str(path),full_check=True)
    if path.stat().st_size != MODEL_BYTES or sha(path) != FP32_SHA:
        raise ValueError('FP32 differs from previously verified graph; do not silently repin')
    graph = onnx.load(str(path),load_external_data=False)
    if any(t.data_location == onnx.TensorProto.EXTERNAL for t in graph.graph.initializer):
        raise ValueError('single-file model required')
    del graph
    session = ort_session(path,ort)
    scores, vectors = {}, []
    for row,candidates,packed in prepared:
        feeds = {name:np.asarray(packed[name],dtype=np.float32 if name == 'target_mask' else np.int64)
                 for name in INPUTS}
        means,sums = session.run(list(OUTPUTS),feeds)
        if not np.isfinite(means).all() or not np.isfinite(sums).all():
            raise ValueError('nonfinite result')
        for i,c in enumerate(candidates):
            if abs(sums[i]/len(c['target_ids'])-means[i]) > .001:
                raise ValueError('mean/sum mismatch')
        scores[row['id']] = {c['surface']:float(means[i]) for i,c in enumerate(candidates)}
        vectors.append(dict(id=row['id'],context=row['context'],surfaces=[c['surface'] for c in candidates],
                            inputs=packed,onnxFloat=scores[row['id']]))
    comparison = compare(requests,cases,entries,archived,scores)
    write(reports/'float-comparison.json',comparison)
    if not comparison['floatParityPassed']:
        raise ValueError('FP32 archived ranking/score parity failed')
    tokenizer.backend_tokenizer.save(str(bundle/'tokenizer.json'))
    tables = export_tables(tokenizer)
    portable = PortableTokenizer(tables)
    strings = set(conformance_strings(requests))
    for first,last,_ in tables['unicodeRanges']:
        for cp in {first,last,first-1,last+1}:
            if 0 <= cp < 0x110000 and not 0xd800 <= cp <= 0xdfff:
                strings.add('a'+chr(cp)+'Ł')
    token_vectors = []
    for text in sorted(strings):
        expected = tokenizer.encode(text,add_special_tokens=False)
        if portable.encode(text) != expected:
            raise ValueError(f'portable tokenizer differs: {text!r}')
        token_vectors.append(dict(text=text,ids=expected))
    # Exhaustive scalar-block comparison is host-only to keep phone fixtures small.
    exhaustive = 0
    for start in range(0,0x110000,256):
        text = 'a'+''.join(chr(cp) for cp in range(start,min(start+256,0x110000))
                          if not 0xd800 <= cp <= 0xdfff)+'Ł'
        if portable.encode(text) != tokenizer.encode(text,add_special_tokens=False):
            raise ValueError(f'exhaustive tokenizer mismatch U+{start:04X}')
        exhaustive += 1
    write(bundle/'portable-tokenizer.json',tables)
    write(bundle/'tokenizer-conformance.json',dict(schemaVersion=1,model=MODEL,vectors=token_vectors))
    write(bundle/'android-score-vectors.json',dict(schemaVersion=1,protocol=VERSION,vectors=vectors))
    shutil.copy2(ROOT/'NOTICE.txt',bundle/'NOTICE.txt')
    manifest = dict(schemaVersion=1,protocol=VERSION,model=MODEL,onnxRuntimeVersion=ORT_VERSION,
                    scoring='whole-word-mask-mean-log-probability',inputNames=list(INPUTS),outputNames=list(OUTPUTS),
                    maxSequence=512,maxCandidates=12,maxTargetTokens=32,benchmarkOnly=True,
                    floatParityPassed=True,phoneReady=False,
                    files={p.name:dict(bytes=p.stat().st_size,sha256=sha(p)) for p in sorted(bundle.iterdir())})
    write(bundle/'manifest.json',manifest)
    for p in bundle.iterdir():
        if p.name != 'model.onnx':
            shutil.copy2(p,reports/p.name)
    report = dict(protocol=VERSION,codeCommit=os.environ.get('GITHUB_SHA','local-uncommitted'),model=MODEL,
                  previousFreezeSha256=frozen and sha(ROOT.parent/'herbert_mobile_v1/freeze-manifest.json'),
                  requestPayloadSha256=frozen['requestPayloadSha256'],requests=len(requests),
                  tokenVectors=len(token_vectors),exhaustiveScalarBlocks=exhaustive,
                  originalFastTokenizerParityPassed=True,floatParityPassed=True,benchmarkBundleCreated=True,
                  phoneReady=False,independentQualityValidated=False,loadingInfo=loading,loadSeconds=load_seconds,
                  packages={p:importlib.metadata.version(p) for p in
                            ['torch','transformers','tokenizers','numpy','onnx','onnxruntime']})
    write(reports/'benchmark-report.json',report)
    summary = (f'# HerBERT FP32 benchmark package v1\n\nFP32 identity and archived parity: PASS. '
               f'Portable reference vs original fast tokenizer: PASS ({len(token_vectors)} saved vectors; '
               f'{exhaustive} exhaustive scalar blocks).\n\n'
               'This is a benchmark package, not live IME integration or a phone performance result. '
               'The prior INT8 gate remains FAIL. Android/Kotlin conformance is a separate required gate.\n')
    (reports/'SUMMARY.md').write_text(summary)
    print(summary)

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,required=True)
    run(parser.parse_args().out)
