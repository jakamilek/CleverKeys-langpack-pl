"""Frozen label-free 16/32 requests and strict complete-result evaluation, stdlib only."""
import hashlib
import json
import math
import re
import statistics
from pathlib import Path

ROOT = Path(__file__).parent
import importlib.util
_spec = importlib.util.spec_from_file_location('frozen_mlm_v1_contract', ROOT.parent / 'polish_mlm_compare_v1' / 'contract.py')
source_contract = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(source_contract)

VERSION = 'polish-mlm-compare-v2'
WINDOWS = (16, 32)
MODELS = {
    'geotrend_distil': {'id': 'Geotrend/distilbert-base-pl-cased', 'revision': '9002d311e35aac14575bf53ad4fa3d8f8b853c2b', 'license': 'Apache-2.0', 'architecture': 'distilbert', 'layers': 6, 'safetensors': True},
    'distilherbert': {'id': 'BartekK/distilHerBERT-base-cased', 'revision': '7276461b7a8fd668aaf30313c03a68bd11aad642', 'license': 'UNSPECIFIED; redistribution blocked', 'architecture': 'bert', 'layers': 6, 'safetensors': False},
}
REFERENCE_COMMIT = '769fc46579e910f50ff40f5546f0d5ae5643de5b'
REFERENCE = ROOT.parent / 'polish_mlm_compare_v1_results' / 'herbert'


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def retain(text, count):
    spans = list(re.finditer(r'\S+', text))
    return text[spans[-count].start():] if len(spans) > count else text


def cases_and_sources():
    source_contract.verify_freeze()
    return source_contract.cases_and_sources()


def baseline(c, entries):
    return source_contract.baseline(c, entries)


def prepare():
    cases, entries = cases_and_sources()
    rows = []
    for c in cases:
        surfaces = baseline(c, entries)
        if int(hashlib.sha256(c['id'].encode()).hexdigest()[:8], 16) % 2:
            surfaces = list(reversed(surfaces))
        for window in WINDOWS:
            context = retain(c['leftContext'], window)
            rows.append({'id': f"{c['id']}/{window}", 'caseId': c['id'], 'window': window,
                         'context': context, 'candidates': surfaces})
    return cases, entries, {'protocol': VERSION, 'requests': rows}


def verify_freeze():
    frozen = json.loads((ROOT / 'freeze-manifest.json').read_text())
    repo = ROOT.parents[1]
    for path, expected in frozen['files'].items():
        if hashlib.sha256((repo / path).read_bytes()).hexdigest() != expected:
            raise ValueError('frozen file changed: ' + path)
    if frozen['models'] != MODELS or frozen['requestsSha256'] != digest(prepare()[2]):
        raise ValueError('frozen models/requests changed')
    return frozen


def reference():
    result = json.loads((REFERENCE / 'predictions.json').read_text())
    original_freeze = source_contract.verify_freeze()
    if result['codeCommit'] != REFERENCE_COMMIT or result['freezeManifestSha256'] != digest(original_freeze):
        raise ValueError('wrong historical reference identity')
    report = source_contract.evaluate('herbert', result)
    if report != json.loads((REFERENCE / 'report.json').read_text()):
        raise ValueError('reference report differs from exact recomputation')
    return result, report


def quantiles(values):
    if not values or any(not math.isfinite(x) or x < 0 for x in values):
        raise ValueError('invalid times')
    values = sorted(values)
    return {'p50': statistics.median(values), 'p95': values[math.ceil(.95 * len(values)) - 1]}


def validate_result(name, request, result):
    if (result['model'] != MODELS[name] or result['requestsSha256'] != digest(request)
            or result['protocol'] != VERSION or result['phoneMeasured'] is not False):
        raise ValueError('result identity mismatch')
    expected = {r['id']: r for r in request['requests']}
    actual = {p['id']: p for p in result['predictions']}
    if set(expected) != set(actual) or len(actual) != len(result['predictions']):
        raise ValueError('missing/duplicate result')
    for rid, p in actual.items():
        if set(p['scores']) != set(expected[rid]['candidates']) or any(not math.isfinite(v) for v in p['scores'].values()):
            raise ValueError('invalid model scores')
        quantiles([p['prepareMs'], p['inferenceMs'], p['totalMs']])
        if p['retainedWords'] != len(expected[rid]['context'].split()):
            raise ValueError('wrong retained context')
    return actual


def evaluate(name, result):
    cases, entries, request = prepare()
    predictions = validate_result(name, request, result)
    cases = {c['id']: c for c in cases}
    groups, decisions = {}, []
    for row in request['requests']:
        c, p = cases[row['caseId']], predictions[row['id']]
        b = baseline(c, entries)
        rank = sorted(row['candidates'], key=lambda s: (-p['scores'][s], b.index(s)))
        gold = c.get('goldSurface')
        if c['suite'] == 'punctuation_before_word':
            gold = (c['goldPunctuation'] + ' ' if c['goldPunctuation'] else '') + c['nextWord']
        key = f"{c['population']}/{c['suite']}/{row['window']}"
        g = groups.setdefault(key, {'cases': 0, 'labelled': 0, 'reachable': 0, 'top1': 0, 'top3': 0,
                                     'baselineTop1': 0, 'repairs': 0, 'regressions': 0,
                                     'lowerLabelled': 0, 'lowerTop1': 0, 'upperLabelled': 0, 'upperTop1': 0,
                                     'lowerRegressions': 0, 'upperRegressions': 0,
                                     'commaLabelled': 0, 'commaTop1': 0, 'noCommaLabelled': 0, 'noCommaTop1': 0,
                                     'timing': []})
        g['cases'] += 1
        g['timing'].append(p)
        if gold is not None:
            correct, base_correct = rank[0] == gold, b[0] == gold
            g['labelled'] += 1
            g['reachable'] += gold in rank
            g['top1'] += correct
            g['top3'] += gold in rank[:3]
            g['baselineTop1'] += base_correct
            g['repairs'] += correct and not base_correct
            g['regressions'] += not correct and base_correct
            if c['suite'] == 'punctuation_before_word':
                label = 'comma' if c['goldPunctuation'] else 'noComma'
            else:
                label = 'upper' if gold[0].isupper() else 'lower'
            g[label + 'Labelled'] += 1
            g[label + 'Top1'] += correct
            if label in ('lower', 'upper'):
                g[label + 'Regressions'] += not correct and base_correct
        decisions.append({'id': row['id'], 'caseId': row['caseId'], 'window': row['window'],
                          'population': c['population'], 'suite': c['suite'], 'gold': gold,
                          'rank': rank, 'baseline': b, 'correct': gold is not None and rank[0] == gold})
    for g in groups.values():
        ts = g.pop('timing')
        for field in ['prepareMs', 'inferenceMs', 'totalMs']:
            g[field] = quantiles([t[field] for t in ts])
    by_id = {d['id']: d for d in decisions}
    paired = {}
    for c in cases.values():
        a, b = by_id[c['id'] + '/16'], by_id[c['id'] + '/32']
        key = c['population'] + '/' + c['suite']
        g = paired.setdefault(key, {'cases': 0, 'changedTop1': 0, 'repairs32': 0, 'regressions32': 0})
        g['cases'] += 1
        g['changedTop1'] += a['rank'][0] != b['rank'][0]
        if a['gold'] is not None:
            g['repairs32'] += b['correct'] and not a['correct']
            g['regressions32'] += a['correct'] and not b['correct']
    return {'groups': groups, 'windowPairs': paired, 'decisions': decisions}


if __name__ == '__main__':
    verify_freeze()
    print(json.dumps({'cases': len(prepare()[0]), 'requests': len(prepare()[2]['requests']),
                      'requestsSha256': digest(prepare()[2])}))
