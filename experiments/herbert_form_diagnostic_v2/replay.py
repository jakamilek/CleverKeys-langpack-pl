"""Preservation probe: live mean versus diagnostic sum on immutable old requests.

This is not a production scorer switch. V1 inputs/code/workflow remain immutable.
"""
import argparse
import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT.parent / 'herbert_form_diagnostic_v1'))
import diagnose as v1


def verify_freeze():
    freeze = v1.read(ROOT / 'freeze-manifest.json')
    v1.require(freeze['protocol'] == 'herbert-form-diagnostic-v2-history' and
               freeze['createdBeforeInference'] is True, 'v2 freeze protocol')
    for path, expected in freeze['files'].items():
        v1.require(v1.sha(ROOT / path) == expected, 'v2 freeze mismatch: ' + path)
    v1.verify_freeze()
    return freeze


def compare(rows):
    """Retain every paired outcome; report missing/unlabelled gold separately."""
    v1.require(len({r['id'] for r in rows}) == len(rows) and bool(rows), 'duplicate/empty requests')
    groups, changes = {}, []
    for r in rows:
        surfaces, gold = r['surfaces'], r['gold']
        before, after = v1.rank(surfaces, r['meanScores']), v1.rank(surfaces, r['sumScores'])
        key = '/'.join([r['suite'], r['population'], r['window']])
        g = groups.setdefault(key, dict(requests=0, labelled=0, missingGold=0, meanTop1=0,
                                       sumTop1=0, meanTop3=0, sumTop3=0,
                                       repairs=0, regressions=0, top3Regressions=0, rankChanges=0))
        g['requests'] += 1
        g['rankChanges'] += before != after
        if gold is not None:
            g['labelled'] += 1
            g['missingGold'] += gold not in surfaces
            g['meanTop1'] += before[0] == gold
            g['sumTop1'] += after[0] == gold
            g['meanTop3'] += gold in before[:3]
            g['sumTop3'] += gold in after[:3]
            g['repairs'] += before[0] != gold and after[0] == gold
            g['regressions'] += before[0] == gold and after[0] != gold
            g['top3Regressions'] += gold in before[:3] and gold not in after[:3]
        if before != after:
            changes.append(dict(id=r['id'], gold=gold, group=key, meanOrder=before,
                                sumOrder=after, meanScores=r['meanScores'], sumScores=r['sumScores']))
    return dict(groups=groups, changes=changes,
                preservationPassed=all(g['regressions'] == g['top3Regressions'] == 0 for g in groups.values()))


def run(bundle, out):
    freeze = verify_freeze()
    out, bundle = Path(out), Path(bundle)
    v1.run(bundle, out / 'fresh24')  # mandatory full actual graph/token/feed checks first
    fresh = v1.read(out / 'fresh24/scores.json')
    archived24 = v1.read(ROOT.parent / 'herbert_form_diagnostic_results/2026-10-10-v1/scores.json')
    a, b = {r['id']: r for r in archived24['predictions']}, {r['id']: r for r in fresh['predictions']}
    v1.require(set(a) == set(b) and len(a) == 24, 'fresh24 completeness')
    for key in a:
        for name in ['scores', 'sumScores']:
            v1.require(set(a[key][name]) == set(b[key][name]) and
                       max(abs(a[key][name][s] - b[key][name][s]) for s in a[key][name]) <= .001, 'v1 reproduction scores')
        for name in ['modelOrder', 'sumOrderDiagnosticOnly']:
            v1.require(a[key][name] == b[key][name], 'v1 reproduction ranks')
    sys.path.insert(0, str(ROOT.parent / 'herbert_mobile_v1'))
    from contract_mobile import prepare, verify_freeze as verify_original
    verify_original()
    cases, _, requests, _ = prepare()
    cases_by_id = {c['id']: c for c in cases['cases']}
    vectors = v1.read(bundle / 'android-score-vectors.json')['vectors']
    vectors_by_id = {v['id']: v for v in vectors}
    v1.require(len(requests) == len(vectors_by_id) == 232 and
               {r['id'] for r in requests} == set(vectors_by_id), 'original request identities')
    import numpy as np
    import onnxruntime as ort
    v1.require(ort.__version__ == '1.21.1', 'ORT version')
    options = ort.SessionOptions()
    options.intra_op_num_threads = 2
    options.inter_op_num_threads = 1
    options.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL
    session = ort.InferenceSession(str(bundle / 'model.onnx'), sess_options=options, providers=['CPUExecutionProvider'])
    v1.require(tuple(i.name for i in session.get_inputs()) == v1.INPUTS and
               tuple(o.name for o in session.get_outputs()) == v1.OUTPUTS, 'graph signature')
    rows = []
    for request in requests:
        vector, case = vectors_by_id[request['id']], cases_by_id[request['caseId']]
        surfaces, packed = vector['surfaces'], vector['inputs']
        v1.require(surfaces == [c['surface'] for c in request['candidates']] and
                   vector['context'] == request['context'], 'archived surfaces/context')
        feed = {k: np.asarray(v, dtype=np.float32 if k == 'target_mask' else np.int64) for k, v in packed.items()}
        means, sums = session.run(list(v1.OUTPUTS), feed)
        mean_scores, sum_scores = v1.check_scores(surfaces, packed, means, sums)
        v1.require(max(abs(mean_scores[s] - vector['onnxFloat'][s]) for s in surfaces) <= .001 and
                   v1.rank(surfaces, mean_scores) == v1.rank(surfaces, vector['onnxFloat']), 'archived native parity')
        rows.append(dict(id=request['id'], caseId=request['caseId'], context=vector['context'],
                         suite=case['suite'], population=case['population'], window=request['window'],
                         surfaces=surfaces, gold=case['goldSurface'], meanScores=mean_scores,
                         sumScores=sum_scores, targetTokenCounts=[int(sum(mask)) for mask in packed['target_mask']]))
    history = compare(rows)
    fresh_rows = [dict(id=r['id'], suite='authored24', population=r['origin'], window=r['group'],
                      surfaces=r['surfaces'], gold=r['gold'], meanScores=r['scores'], sumScores=r['sumScores'])
                  for r in fresh['predictions']]
    report = dict(protocol='herbert-form-diagnostic-v2-history', codeCommit=os.environ.get('GITHUB_SHA', 'local-unpublished'),
                  frozenInputs=freeze, originalModelSha256=v1.TRUST['model.onnx'][1],
                  historicalRequests=len(rows), historicalCases=len({r['caseId'] for r in rows}),
                  historical=history, fresh24=compare(fresh_rows), predictions=rows,
                  limitations=['Frozen historical labels are not new blinded evaluation',
                               'Sum remains diagnostic only; no APK/live scorer change',
                               'Original short/long and suite/population metrics kept separate',
                               'No phone swipe geometry, route confirmation or latency claim'])
    (out / 'scores.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# HerBERT mean/sum — zachowanie wcześniejszych wyników', '',
             f"232 historyczne żądania; preservationPassed={history['preservationPassed']}. To wynik diagnostyczny, nie zmiana klawiatury.", '',
             '| Zbiór / populacja / okno | Oceniane | Mean Top1 | Sum Top1 | Naprawy | Regresje Top1 | Regresje Top3 |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for name, data in [('history', history), ('fresh24', report['fresh24'])]:
        for key, g in data['groups'].items():
            lines.append(f"| {name}/{key} | {g['labelled']} | {g['meanTop1']} | {g['sumTop1']} | {g['repairs']} | {g['regressions']} | {g['top3Regressions']} |")
    lines += ['', 'Wszystkie zmiany, mean/sum scores, liczba tokenów i konteksty w scores.json.',
              'Brak regressions w tej próbie nie oznacza niezależnej trafności produkcyjnej.']
    (out / 'SUMMARY.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print('HerBERT history diagnostic: original parity PASS; 232 native paired requests and fresh24 replay complete')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--contract-only', action='store_true')
    parser.add_argument('--bundle', type=Path)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    if args.contract_only:
        verify_freeze()
        print('HerBERT history diagnostic: frozen v1/v2 chain PASS')
    else:
        v1.require(args.bundle is not None and args.out is not None, 'bundle/out required')
        run(args.bundle, args.out)
