"""Evaluate all preregistered systems, separating controls and unlabelled cases."""
import argparse
import json
from pathlib import Path

from diagnostic_runner import METHODS, PRESETS
from prototype import canonical_bytes, prepare, resolve, validate_predictions

ROOT = Path(__file__).parent
MAIN = {"direct", "previous", "distant_retained", "conflicting"}


def evaluate_diagnostic(cases, request, predictions=None):
    evidence = validate_predictions(predictions, request) if predictions else {}
    by_id = {c['id']: c for c in cases['cases']}
    rows = []
    for item in request['requests']:
        case_id, window = item['requestId'].rsplit('/', 1)
        case = by_id[case_id]
        suggestions = resolve(item['candidates'], evidence.get(item['requestId']), item['caseMode'])
        top = suggestions[0]
        expected = case.get('expected')
        scored = evidence.get(item['requestId'], {})
        group = item['candidates'][0]
        lower, upper = group['variants']
        lo = scored.get((group['languageCode'], group['surfaceKey'], lower))
        up = scored.get((group['languageCode'], group['surfaceKey'], upper))
        rows.append({'caseId': case_id, 'window': window,
                     'category': case['diagnostic']['category'], 'pairId': case['diagnostic']['pairId'],
                     'top': top['surface'], 'expected': expected['surface'] if expected else None,
                     'correct': top['surface'] == expected['surface'] if expected else None,
                     'properMinusCommon': up - lo if up is not None and lo is not None else None,
                     'expectedReachable': any(s['surface'] == expected['surface'] for s in suggestions) if expected else None})
    metrics = {}
    for window in ('two_words', 'long'):
        subset = [r for r in rows if r['window'] == window]
        main = [r for r in subset if r['category'] in MAIN]
        metrics[window] = {'main': {'cases': len(main), 'correct': sum(r['correct'] for r in main),
                                  'expectedReachable': sum(r['expectedReachable'] for r in main)},
                           'byCategory': {}}
        for category in sorted({r['category'] for r in subset}):
            group = [r for r in subset if r['category'] == category]
            labelled = all(r['expected'] is not None for r in group)
            metrics[window]['byCategory'][category] = {'cases': len(group),
                 'correct': sum(r['correct'] for r in group) if labelled else None}
    paired = {}
    for category in sorted(MAIN):
        pairs = [(a, b) for a, b in zip(rows[::2], rows[1::2]) if a['category'] == category]
        paired[category] = {'fixed': sum(not a['correct'] and b['correct'] for a, b in pairs),
                            'broken': sum(a['correct'] and not b['correct'] for a, b in pairs),
                            'changedTop1': sum(a['top'] != b['top'] for a, b in pairs)}
    return {'metrics': metrics, 'paired': paired}, rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--predictions-dir', type=Path, required=True)
    args = parser.parse_args()
    cases = json.loads((ROOT/'diagnostic-cases.json').read_text())
    sidecar = json.loads((ROOT/'diagnostic-sidecar.json').read_text())
    request = prepare(cases, sidecar)
    from prototype import evaluate
    legacy_cases = json.loads((ROOT/'cases-fixture.json').read_text())
    legacy_request = prepare(legacy_cases, json.loads((ROOT/'sidecar-fixture.json').read_text()))
    baseline, baseline_rows = evaluate_diagnostic(cases, request)
    summary = {'schemaVersion': 1, 'requestSha256': request['requestSha256'],
               'fixtureKind': cases['fixtureKind'], 'baseline': baseline, 'systems': {}}
    for model in PRESETS:
        for method in METHODS:
            name = f'{model}-{method}'
            predictions = json.loads((args.predictions_dir/f'diagnostic-{name}.json').read_text())
            metrics, rows = evaluate_diagnostic(cases, request, predictions)
            (args.predictions_dir/f'decisions-{name}.json').write_bytes(canonical_bytes(rows))
            legacy = evaluate(legacy_cases, legacy_request,
                              json.loads((args.predictions_dir/f'legacy-{name}.json').read_text()))
            legacy_decisions = [{'caseId': r['caseId'], 'window': r['window'],
                                 'top': r['suggestions'][0]['surface'], 'correct': r['displayTop1Correct']}
                                for r in legacy['rows']]
            metrics['legacyMetrics'] = legacy['metrics']
            (args.predictions_dir/f'legacy-decisions-{name}.json').write_bytes(canonical_bytes(legacy_decisions))
            summary['systems'][name] = metrics
    (args.predictions_dir/'summary.json').write_bytes(canonical_bytes(summary))
    print(json.dumps({name: data['metrics'] for name, data in summary['systems'].items()},ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
