"""Fixed synthetic form-quality probe of the byte-identical live FP32 graph.

No phone/editor data, export, training, scoring change or claimed phone latency.
Imports of ML libraries occur only after provenance/source contract verification.
"""
import argparse
import hashlib
import json
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PROTOCOL = 'herbert-form-diagnostic-v1'
INPUTS = ('input_ids', 'attention_mask', 'target_positions', 'target_ids', 'target_mask')
OUTPUTS = ('mean_log_probability', 'sum_log_probability')
TRUST = {
    'NOTICE.txt': (1653, 'b9b8af816cbed0c0a5e7565a224407399d028313b2b2ff2a089a86d67d70bc28'),
    'android-score-vectors.json': (109889, 'c9ce34814baa697aa9e6d58d9337eb5e5fd91057eb06bfeb34be4874bdc9cb6a'),
    'manifest.json': (1243, '667bd4fee413a13ca8edca75f5b7defff2c58d0450d8d87ab8e9ccef948026b0'),
    'model.onnx': (651798883, 'f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2'),
    'portable-tokenizer.json': (1468574, 'ee9b13d7732fb22dc7b28d51751daebbe5caaac484ba69d7104b80b52b32681b'),
    'tokenizer-conformance.json': (225506, 'b840d6c51df89d15f4797b0c9e06690ed530b5ef85792451a30356edfcce7f28'),
    'tokenizer.json': (3688783, '2e045c82c9ea8b5bc54162d92d5c72141492df88eff098f3e5436e499d1e29fb'),
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def verify_freeze():
    freeze = read(ROOT / 'freeze-manifest.json')
    require(freeze['protocol'] == PROTOCOL and freeze['createdBeforeInference'] is True, 'protocol freeze')
    for path, expected in freeze['files'].items():
        require(sha(ROOT / path) == expected, 'freeze mismatch: ' + path)
    return freeze


def verify_bundle(directory, trust=TRUST):
    directory = Path(directory)
    require({p.name for p in directory.iterdir()} == set(trust), 'bundle members differ')
    for name, (size, expected) in trust.items():
        path = directory / name
        require(path.is_file() and not path.is_symlink() and path.stat().st_size == size, 'bundle size/type')
        require(sha(path) == expected, 'bundle hash: ' + name)


def validate_cases(payload, source):
    require(payload['schemaVersion'] == 1 and payload['contextWords'] == 32, 'case schema/window')
    entries = {e['surfaceKey']: e for e in source['entries']}
    cases = payload['cases']
    require(len(cases) == 24 and len({c['id'] for c in cases}) == 24, 'case count/ids')
    for c in cases:
        surfaces = c['surfaces']
        require(len(surfaces) == 4 and len(set(surfaces)) == 4 and c['gold'] in surfaces, 'case surfaces/gold')
        require(c['context'].endswith(' ') and 1 <= len(c['context'].split()) <= 32 and
                len(c['context']) <= 4096 and not any(x in c['context'] for x in ['<mask>', '<s>', '</s>']), 'synthetic context')
        keys = list(dict.fromkeys(s.lower() for s in surfaces))
        require(len(keys) == 2 and all(key in entries for key in keys), 'source keys')
        identities = []
        for key in keys:
            e = entries[key]
            require(set(s for s in surfaces if s.lower() == key) ==
                    {v['surface'] for v in e['capitalization']['variants']}, 'source surfaces')
            evidence = e['metadata']['sourceEvidence']
            # Same three actual-source paths accepted by LanguageIntelligence.sourceLemmas.
            readings = [r for name in ['lexicalReadings', 'generatedFormProofs', 'interpretations']
                        for r in evidence.get(name, [])]
            identities.append({(r['lemma'], r.get('partOfSpeech') or r.get('tag', '').split(':')[0])
                               for r in readings if r.get('lemma') and (r.get('partOfSpeech') or r.get('tag'))
                               and (r.get('form', '').lower() == key or
                                    any(s.lower() == key for s in r.get('surfaces', [])))})
        require(bool(identities[0] & identities[1]), 'source lemma/POS')
    return cases


def prepare(tokenizer, special, context, surfaces):
    left = tokenizer.encode(context)
    targets = [tokenizer.encode(surface) for surface in surfaces]
    require(1 <= len(surfaces) <= 12 and len(set(surfaces)) == len(surfaces), 'batch surfaces')
    require(all(1 <= len(t) <= 32 and special['unk'] not in t for t in targets), 'target tokens')
    sequence = len(left) + max(map(len, targets)) + 2
    width = max(map(len, targets))
    require(3 <= sequence <= 512, 'sequence budget')
    result = {name: [] for name in INPUTS}
    for target in targets:
        count = len(target)
        ids = [special['cls']] + left + [special['mask']] * count + [special['sep']]
        pad = sequence - len(ids)
        result['input_ids'].append(ids + [special['pad']] * pad)
        result['attention_mask'].append([1] * len(ids) + [0] * pad)
        result['target_positions'].append(list(range(len(left) + 1, len(left) + count + 1)) + [0] * (width - count))
        result['target_ids'].append(target + [0] * (width - count))
        result['target_mask'].append([1.0] * count + [0.0] * (width - count))
    return result


def rank(surfaces, scores):
    require(set(scores) == set(surfaces) and len(set(surfaces)) == len(surfaces), 'unaligned scores')
    require(all(math.isfinite(v) for v in scores.values()), 'nonfinite scores')
    return sorted(surfaces, key=lambda s: -scores[s])  # stable: live tie contract


def check_scores(surfaces, packed, means, sums):
    require(len(means) == len(sums) == len(surfaces), 'output length')
    for i in range(len(surfaces)):
        count = sum(packed['target_mask'][i])
        require(count > 0 and math.isfinite(float(means[i])) and math.isfinite(float(sums[i])) and
                abs(float(sums[i]) / count - float(means[i])) <= .001, 'mean/sum mismatch')
    return dict(zip(surfaces, map(float, means))), dict(zip(surfaces, map(float, sums)))


def run(bundle, out):
    freeze = verify_freeze()
    cases = validate_cases(read(ROOT / 'cases.json'), read(ROOT / 'source-fixture.json'))
    verify_bundle(bundle)
    sys.path.insert(0, str(ROOT.parent / 'herbert_fp32_benchmark_v1'))
    from portable import PortableTokenizer
    import numpy as np
    import onnxruntime as ort
    from tokenizers import Tokenizer
    require(ort.__version__ == '1.21.1', 'ORT version')
    bundle, out = Path(bundle), Path(out)
    tables = read(bundle / 'portable-tokenizer.json')
    tokenizer, special = PortableTokenizer(tables), tables['specialTokenIds']
    fast = Tokenizer.from_file(str(bundle / 'tokenizer.json'))
    token_vectors = read(bundle / 'tokenizer-conformance.json')['vectors']
    require(len(token_vectors) == 2471, 'token vector count')
    for row in token_vectors:
        require(tokenizer.encode(row['text']) == row['ids'] == fast.encode(row['text'], add_special_tokens=False).ids, 'tokenizer parity')
    for c in cases:
        for s in [c['context']] + c['surfaces']:
            require(tokenizer.encode(s) == fast.encode(s, add_special_tokens=False).ids, 'new token parity')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(str(bundle / 'model.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
    require(tuple(i.name for i in session.get_inputs()) == INPUTS and tuple(o.name for o in session.get_outputs()) == OUTPUTS, 'graph signature')
    require([i.type for i in session.get_inputs()] == ['tensor(int64)'] * 4 + ['tensor(float)'] and
            all(len(i.shape) == 2 for i in session.get_inputs()) and
            all(o.type == 'tensor(float)' and len(o.shape) == 1 for o in session.get_outputs()), 'graph types/ranks')
    def score(surfaces, packed):
        feed = {k: np.asarray(v, dtype=np.float32 if k == 'target_mask' else np.int64) for k, v in packed.items()}
        means, sums = session.run(list(OUTPUTS), feed)
        return check_scores(surfaces, packed, means, sums)
    vectors = read(bundle / 'android-score-vectors.json')['vectors']
    require(len(vectors) == 232 and sum(len(v['surfaces']) for v in vectors) == 532, 'score vector count')
    maximum_error = 0.0
    for v in vectors:
        packed = prepare(tokenizer, special, v['context'], v['surfaces'])
        require(packed == v['inputs'], 'original five-input parity')
        actual, _ = score(v['surfaces'], packed)
        expected = v['onnxFloat']
        error = max(abs(actual[s] - expected[s]) for s in actual)
        maximum_error = max(maximum_error, error)
        require(error <= .001 and rank(v['surfaces'], actual) == rank(v['surfaces'], expected), 'native original score/rank parity')
    rows, maximum_single_error = [], 0.0
    for c in cases:
        surfaces = c['surfaces']
        packed = prepare(tokenizer, special, c['context'], surfaces)
        means, sums = score(surfaces, packed)
        for s in surfaces:
            single, _ = score([s], prepare(tokenizer, special, c['context'], [s]))
            error = abs(single[s] - means[s])
            maximum_single_error = max(maximum_single_error, error)
            require(error <= .001, 'single/batched parity')
        ordered = rank(surfaces, means)
        rows.append(dict(c, route='DIRECT_HOST_ONNX_NO_IME_FALLBACK', modelOrder=ordered,
                         goldRank=ordered.index(c['gold']) + 1, scores=means, sumScores=sums,
                         topGapMean=means[ordered[0]] - means[ordered[1]],
                         goldGapMean=means[c['gold']] - means[ordered[0]],
                         sumOrderDiagnosticOnly=rank(surfaces, sums),
                         targetTokenIds={s: tokenizer.encode(s) for s in surfaces},
                         inputShape=[len(surfaces), len(packed['input_ids'][0]), len(packed['target_ids'][0])],
                         inputs=packed, top1EndingCorrect=ordered[0].lower() == c['gold'].lower(),
                         top1CapitalizationCorrect=ordered[0][0].isupper() == c['gold'][0].isupper(),
                         baselineKind='SYNTHETIC_SOURCE_ORDER_NOT_PHONE_GEOMETRY',
                         baselineOrder=surfaces, baselineGoldRank=surfaces.index(c['gold']) + 1))
    strata = {}
    for r in rows:
        key = r['group'] + '/' + r['origin']
        item = strata.setdefault(key, dict(cases=0, top1=0, rawTop3=0, endingTop1=0, capitalizationTop1=0))
        item['cases'] += 1
        item['top1'] += r['goldRank'] == 1
        item['rawTop3'] += r['goldRank'] <= 3
        item['endingTop1'] += r['top1EndingCorrect']
        item['capitalizationTop1'] += r['top1CapitalizationCorrect']
    report = dict(protocol=PROTOCOL, codeCommit=os.environ.get('GITHUB_SHA', 'local-unpublished'),
                  modelSha256=TRUST['model.onnx'][1], frozenInputs=freeze,
                  originalParity=dict(tokenVectors=2471, batches=232, candidates=532, maxAbsScoreError=maximum_error),
                  newCases=len(rows), top1=sum(r['goldRank'] == 1 for r in rows),
                  top3=sum(r['goldRank'] <= 3 for r in rows),
                  endingTop1=sum(r['top1EndingCorrect'] for r in rows),
                  capitalizationTop1=sum(r['top1CapitalizationCorrect'] for r in rows),
                  maxSingleBatchScoreError=maximum_single_error, predictions=rows, strata=strata,
                  limitations=['Authored diagnostic labels, not blinded external gold',
                               'No phone swipe geometry or captured editor state',
                               'Host direct inference cannot establish whether reported phone swipe used SI or fallback',
                               'Mean score is live contract; sum is diagnostic only; no changes to live ranks',
                               'No phone timing, confidence threshold or production acceptance claim'])
    out.mkdir(parents=True, exist_ok=True)
    (out / 'scores.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# HerBERT — dobór odmiany i kapitalizacji', '',
             f"Top1 {report['top1']}/24; raw Top3 wewnątrz grupy {report['top3']}/24; właściwa forma bez rozróżnienia wielkości liter {report['endingTop1']}/24.",
             '', 'Oryginalne 2471 token vectors / 232 batches / 532 candidates: PASS.',
             'Jawne przykłady diagnostyczne. Bez dowodu ścieżki SI/fallback na telefonie i bez zmiany rankingu aplikacji.', '',
             '| ID | Kontekst | Oczekiwane | Pierwsze SI | Miejsce oczekiwanego |',
             '|---|---|---|---|---|']
    lines += [f"| {r['id']} | {r['context'].strip()} | {r['gold']} | {r['modelOrder'][0]} | {r['goldRank']} |" for r in rows]
    lines += ['', 'Pełne mean/sum scores, tokeny, pięć wejść i wszystkie cztery formy: scores.json.',
              'Sum-score ranking to analiza porównawcza, nie nowy algorytm produkcyjny.']
    (out / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"HerBERT form diagnostic: original parity PASS; {len(rows)} real ONNX requests + single checks complete")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract-only', action='store_true')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.contract_only:
        verify_freeze()
        validate_cases(read(ROOT / 'cases.json'), read(ROOT / 'source-fixture.json'))
        print('HerBERT form diagnostic: frozen 24 source-confirmed cases PASS')
    else:
        require(args.bundle is not None and args.out is not None, 'bundle/out required')
        run(args.bundle, args.out)
