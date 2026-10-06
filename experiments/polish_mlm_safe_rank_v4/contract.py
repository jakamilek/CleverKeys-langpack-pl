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

VERSION = 'polish-mlm-safe-rank-v4'
WINDOWS = (16, 32)
MODELS = {
    'herbert': {'id': 'allegro/herbert-base-cased', 'revision': '50e33e0567be0c0b313832314c586e3df0dc2297', 'license': 'CC-BY-4.0', 'architecture': 'bert', 'layers': 12, 'safetensors': False},
    'distilherbert': {'id': 'BartekK/distilHerBERT-base-cased', 'revision': '7276461b7a8fd668aaf30313c03a68bd11aad642', 'license': 'UNSPECIFIED; review deferred by maintainer, not a license grant', 'architecture': 'bert', 'layers': 6, 'safetensors': False},
}


def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(',', ':')).encode()


def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()


def retain(text, count):
    spans = list(re.finditer(r'\S+', text))
    return text[spans[-count].start():] if len(spans) > count else text


def cases_and_sources():
    source_contract.verify_freeze()
    source = json.loads((ROOT/'source-snapshot.json').read_text())
    entries = source_contract.legacy.validate_sources(source)
    cases = json.loads((ROOT/'cases.json').read_text())['cases']
    if len(cases)!=128 or len({c['id'] for c in cases})!=128:
        raise ValueError('wrong/duplicate frozen cases')
    historic = source_contract.cases_and_sources()[0]
    old_contexts = {c['leftContext'] for c in historic}
    previous = json.loads((ROOT.parent/'polish_mlm_fresh_v3/cases.json').read_text())['cases']
    old_contexts |= {c['leftContext'] for c in previous}
    old_keys = {c['candidates'][0]['key'] for c in historic if c['population']=='new_natural'}
    groups = {}
    for c in cases:
        text, slate = c['leftContext'], c['candidates']
        if not text or len(text)>4096 or len(text.split())>64 or c['suite']!='forms' or len(slate)!=1:
            raise ValueError('invalid case/context')
        key=slate[0]['key']
        if key not in entries or len(baseline(c,entries))!=2 or c['goldSurface'] not in baseline(c,entries):
            raise ValueError('unattested gold or case pair')
        if c['population'].startswith('fresh_'):
            if text in old_contexts:
                raise ValueError('fresh context overlaps historical evaluation')
            short=c['population'].startswith('fresh_short_')
            if (short and len(text.split())>16) or (not short and not 17<=len(text.split())<=32):
                raise ValueError('wrong natural length stratum')
            if c['population'].endswith('known_key') != (key in old_keys):
                raise ValueError('wrong source-key holdout stratum')
        group=groups.setdefault(c['population'],[0,0,0])
        group[0]+=1;group[1]+=c['goldSurface'][0].islower();group[2]+=c['goldSurface'][0].isupper()
    expected={f'fresh_{length}_{keys}':[16,8,8] for length in ['short','long'] for keys in ['known_key','new_key']}
    expected['regression_v5']=[64,32,32]
    if groups!=expected:
        raise ValueError('incomplete or unbalanced populations: '+repr(groups))
    old_forms=[{**c,'id':'regression/'+c['id'],'population':'regression_v5'}
               for c in json.loads((ROOT.parent/'ai_compare_v5/cases.json').read_text())['cases'] if c['suite']=='forms']
    if [c for c in cases if c['population']=='regression_v5']!=old_forms:
        raise ValueError('known regression set changed')
    return cases,entries


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
    from calibrate import calculate
    if json.loads((ROOT/'calibration.json').read_text()) != calculate():
        raise ValueError('development calibration changed')
    if frozen['models'] != MODELS or frozen['requestsSha256'] != digest(prepare()[2]):
        raise ValueError('frozen models/requests changed')
    return frozen


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
    out = {'groups': groups, 'windowPairs': paired, 'decisions': decisions,
           'populationRoles': {key: ('developmentReplay' if key.startswith('regression_v5/')
                                     else 'newAuthoredContextValidation') for key in groups}}
    if name == 'distilherbert':
        from safe_evaluation import evaluate_policy
        out['gated'] = evaluate_policy(list(cases.values()), entries, request, predictions, json.loads((ROOT/'calibration.json').read_text())['threshold'])
    return out


if __name__ == '__main__':
    verify_freeze()
    print(json.dumps({'cases': len(prepare()[0]), 'requests': len(prepare()[2]['requests']),
                      'requestsSha256': digest(prepare()[2])}))
