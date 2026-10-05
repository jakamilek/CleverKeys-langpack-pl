"""Actual pinned CPU models. Validation finishes before scoring any labelled case."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import time
from pathlib import Path
from contract import ROOT, MODELS, canonical, digest, prepare, verify_freeze, evaluate
from mlm import encode, score, check_projection


def files_manifest(preset):
    from huggingface_hub import snapshot_download
    root = Path(snapshot_download(preset['id'], revision=preset['revision'], local_files_only=True))
    rows = []
    for p in sorted(root.rglob('*')):
        if p.is_file():
            h = hashlib.sha256()
            with p.open('rb') as stream:
                for chunk in iter(lambda: stream.read(1024 * 1024), b''):
                    h.update(chunk)
            rows.append({'path': str(p.relative_to(root)), 'bytes': p.stat().st_size, 'sha256': h.hexdigest()})
    if not any(r['path'].endswith(('.bin', '.safetensors')) for r in rows):
        raise ValueError('no actual pretrained weight file')
    return rows


def load(name):
    import torch
    from transformers import AutoModelForMaskedLM, AutoTokenizer
    torch.set_num_threads(2)
    torch.set_num_interop_threads(1)
    preset = MODELS[name]
    began = time.perf_counter()
    tokenizer = AutoTokenizer.from_pretrained(preset['id'], revision=preset['revision'],
                                             trust_remote_code=False, use_fast=True)
    if not tokenizer.is_fast or any(getattr(tokenizer, attr) is None for attr in ['mask_token_id', 'pad_token_id', 'unk_token_id']):
        raise ValueError('exact fast tokenizer/special IDs missing')
    model, info = AutoModelForMaskedLM.from_pretrained(
        preset['id'], revision=preset['revision'], trust_remote_code=False,
        use_safetensors=preset['safetensors'], torch_dtype=torch.float32, output_loading_info=True)
    for field in ['missing_keys', 'mismatched_keys', 'error_msgs']:
        if info.get(field):
            raise ValueError('incomplete pretrained head: ' + repr(info))
    unused = {'bert.pooler.dense.bias', 'bert.pooler.dense.weight',
              'cls.sso.sso_relationship.bias', 'cls.sso.sso_relationship.weight'} if name == 'herbert' else set()
    if set(info.get('unexpected_keys', [])) != unused:
        raise ValueError('unexplained pretrained weights: ' + repr(info))
    if (model.config._commit_hash != preset['revision'] or model.config.model_type != preset['architecture']
            or model.config.num_hidden_layers != preset['layers'] or model.config.hidden_size != 768):
        raise ValueError('revision/architecture mismatch')
    model.eval()
    return model, tokenizer, torch, info, time.perf_counter() - began


def run(name, output):
    output.mkdir(parents=True, exist_ok=True)
    frozen = verify_freeze()
    cases, entries, request = prepare()
    (output / 'requests.json').write_bytes(canonical(request) + b'\n')
    model, tokenizer, torch, info, load_seconds = load(name)
    preset = MODELS[name]
    model_files = files_manifest(preset)
    checks = []
    # Source case pairs must remain distinct. No uncasing adapter or tokenizer approximation.
    for entry in entries.values():
        forms = [v['surface'] for v in entry['capitalization']['variants']]
        ids = [tokenizer.encode(s, add_special_tokens=False) for s in forms]
        if len(forms) > 1 and len({tuple(x) for x in ids}) != len(forms):
            raise ValueError('tokenizer collapses source capitalization: ' + entry['surfaceKey'])
    # Exact target spans and model budget checked for every candidate before inference.
    prepared = []
    for row in request['requests']:
        encoded = [encode(row['context'], surface, tokenizer) for surface in row['candidates']]
        prepared.append((row, encoded))
    probes = [prepared[0][1], prepared[1][1],
              [encode('Zażółć gęślą jaźń. W dokumencie wpisano', 'Łódź', tokenizer),
               encode('Zażółć gęślą jaźń. W dokumencie wpisano', 'łódź', tokenizer)]]
    for probe in probes:
        checks.append(check_projection(probe, model, tokenizer, preset['architecture'], torch))
    info['projectionMaxAbsErrors'] = checks
    validation = {'model': preset, 'loadingInfo': info, 'modelFiles': model_files,
                  'sourceCasePreservation': True, 'requestsValidated': len(prepared),
                  'requestsSha256': digest(request), 'freezeManifestSha256': digest(frozen),
                  'codeCommit': os.environ['GITHUB_SHA'], 'beforeLabelledInference': True}
    (output / 'validation.json').write_bytes(canonical(validation) + b'\n')
    print('Full pretrained head, original tokenizer and projection checks PASS', name, flush=True)
    for _ in range(3):
        score(prepared[0][1], model, tokenizer, preset['architecture'], torch)
    # Alternate first window across cases instead of measuring all 16 then all 32.
    execution = []
    for i in range(0, len(prepared), 2):
        pair = prepared[i:i+2]
        execution.extend(pair if (i // 2) % 2 == 0 else reversed(pair))
    predictions = []
    began = time.perf_counter()
    for n, (row, _) in enumerate(execution):
        start = time.perf_counter()
        encoded = [encode(row['context'], s, tokenizer) for s in row['candidates']]
        ready = time.perf_counter()
        values, traces = score(encoded, model, tokenizer, preset['architecture'], torch)
        done = time.perf_counter()
        predictions.append({'id': row['id'], 'scores': dict(zip(row['candidates'], values)),
                            'prepareMs': (ready-start)*1000, 'inferenceMs': (done-ready)*1000,
                            'totalMs': (done-start)*1000, 'retainedWords': len(row['context'].split()),
                            'inputTokens': [len(e['ids']) for e in encoded], 'trace': traces})
        if (n+1) % 20 == 0:
            print(name, n+1, '/', len(prepared), flush=True)
    result = {'protocol': request['protocol'], 'model': preset, 'requestsSha256': digest(request),
              'freezeManifestSha256': digest(frozen), 'codeCommit': os.environ['GITHUB_SHA'],
              'predictions': predictions, 'loadSecondsIncludingDownload': load_seconds,
              'inferenceSeconds': time.perf_counter()-began, 'loadingInfo': info,
              'parameters': sum(p.numel() for p in model.parameters()), 'modelFiles': model_files,
              'peakHostRssMiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
              'phoneMeasured': False, 'weightsPublished': False,
              'environment': {'python': platform.python_version(), 'platform': platform.platform(),
                              'torch': torch.__version__, 'transformers': importlib.metadata.version('transformers'),
                              'dtype': 'float32', 'device': 'cpu', 'threads': [2, 1]},
              'method': 'whole appended span masked; full vocabulary mean logp; summed logp in trace; candidate batch'}
    report = evaluate(name, result)
    (output / 'predictions.json').write_bytes(canonical(result) + b'\n')
    (output / 'report.json').write_bytes(canonical(report) + b'\n')
    print(json.dumps({'model': name, 'requests': len(predictions), 'groups': report['groups']}, ensure_ascii=False), flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', choices=MODELS, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    run(args.model, args.out)
