"""Mobile graph contract and conversion gates. No ML imports; frozen before CI."""
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT.parent / 'ai_metadata_v5'))
import contract_meta as previous

VERSION = 'herbert-mobile-v1'
ORT_VERSION = '1.21.1'  # verified Android + JVM dependencies, not the outdated README
MODEL = previous.MODELS['herbert']
INPUTS = ('input_ids', 'attention_mask', 'target_positions', 'target_ids', 'target_mask')
OUTPUTS = ('mean_log_probability', 'sum_log_probability')
FLOAT_ATOL = 1e-3
MAX_SEQUENCE = 512
MAX_CANDIDATES = 12
MAX_TARGET = 32

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def canonical(obj):
    return previous.canonical(obj)

def prepare():
    previous.verify_freeze()
    source, entries, cases, all_requests = previous.prepare()
    requests = [r for r in all_requests['requests']
                if r['condition'] == 'plain' and r['candidates']]
    reference_file = ROOT.parent / 'ai_metadata_v5_results/herbert/predictions.json'
    reference = json.loads(reference_file.read_text())
    previous.validate_result(all_requests, reference)
    if reference['model'] != MODEL:
        raise ValueError('reference model differs')
    expected = {p['id']: p for p in reference['predictions']}
    return cases, entries, requests, expected

def pack_rows(rows, pad_id):
    """Pad candidate rows, never mask targets one at a time (WWM is unchanged)."""
    if not 1 <= len(rows) <= MAX_CANDIDATES:
        raise ValueError('candidate limit')
    seq = max(len(r['input_ids']) for r in rows)
    targets = max(len(r['target_ids']) for r in rows)
    if not 3 <= seq <= MAX_SEQUENCE or not 1 <= targets <= MAX_TARGET:
        raise ValueError('token budget')
    out = {name: [] for name in INPUTS}
    for row in rows:
        ids, target, positions = row['input_ids'], row['target_ids'], row['target_positions']
        if not target or len(target) != len(positions):
            raise ValueError('invalid targets')
        if len(set(positions)) != len(positions) or any(p <= 0 or p >= len(ids)-1 for p in positions):
            raise ValueError('invalid positions')
        if any(type(t) is not int or t < 0 for t in ids+target+positions):
            raise ValueError('invalid token')
        out['input_ids'].append(ids+[pad_id]*(seq-len(ids)))
        out['attention_mask'].append([1]*len(ids)+[0]*(seq-len(ids)))
        out['target_positions'].append(positions+[0]*(targets-len(target)))
        out['target_ids'].append(target+[0]*(targets-len(target)))
        out['target_mask'].append([1.0]*len(target)+[0.0]*(targets-len(target)))
    return out

def rank(scores, order):
    if set(scores) != set(order) or len(order) != len(set(order)):
        raise ValueError('wrong surfaces')
    if any(not isinstance(v, (float, int)) or not math.isfinite(v) for v in scores.values()):
        raise ValueError('invalid score')
    return sorted(order, key=lambda s: (-scores[s], order.index(s)))

def compare(requests, cases, entries, reference, actual):
    """Every paired change retained. No pooling new/reused or short/long."""
    if set(actual) != {r['id'] for r in requests}:
        raise ValueError('incomplete conversion scores')
    case_by_id = {c['id']: c for c in cases['cases']}
    groups, changes = {}, []
    max_error = 0.0
    for r in requests:
        c = case_by_id[r['caseId']]
        order = previous.legacy.baseline(c, entries)
        before = rank(reference[r['id']]['scores'], order)
        after = rank(actual[r['id']], order)
        error = max(abs(actual[r['id']][s]-reference[r['id']]['scores'][s]) for s in order)
        max_error = max(max_error, error)
        gold = c['goldSurface']
        key = '/'.join([c['suite'], c['population'], r['window']])
        g = groups.setdefault(key, {'cases':0, 'scored':0, 'referenceTop1':0, 'top1':0,
                                   'referenceTop3':0, 'top3':0, 'repairs':0, 'regressions':0,
                                   'top3Regressions':0, 'rankChanges':0})
        g['cases'] += 1
        g['rankChanges'] += before != after
        if gold is not None:
            g['scored'] += 1
            g['referenceTop1'] += before[0] == gold
            g['top1'] += after[0] == gold
            g['referenceTop3'] += gold in before[:3]
            g['top3'] += gold in after[:3]
            g['repairs'] += before[0] != gold and after[0] == gold
            g['regressions'] += before[0] == gold and after[0] != gold
            g['top3Regressions'] += gold in before[:3] and gold not in after[:3]
        if before != after:
            changes.append({'requestId':r['id'], 'gold':gold, 'before':before, 'after':after,
                            'referenceScores':reference[r['id']]['scores'], 'scores':actual[r['id']]})
    # Strict preservation gate, not an accuracy claim or a phone readiness gate.
    preserve = all(g['regressions'] == 0 and g['top3Regressions'] == 0 for g in groups.values())
    return {'groups':groups, 'changes':changes, 'maxAbsScoreError':max_error,
            'floatParityPassed':max_error <= FLOAT_ATOL and not changes,
            'quantizationPreservationPassed':preserve}

def verify_freeze():
    frozen = json.loads((ROOT/'freeze-manifest.json').read_text())
    for path, expected in frozen['files'].items():
        if sha(ROOT/path) != expected:
            raise ValueError('mobile freeze mismatch: '+path)
    workflow = ROOT.parents[1]/'.github/workflows/herbert-mobile-v1.yml'
    if sha(workflow) != frozen['workflowSha256']:
        raise ValueError('mobile workflow mismatch')
    _, _, rows, _ = prepare()
    if previous.digest(rows) != frozen['requestPayloadSha256']:
        raise ValueError('mobile request mismatch')
    if frozen['model'] != MODEL or frozen['onnxRuntimeVersion'] != ORT_VERSION:
        raise ValueError('mobile preset mismatch')
    return frozen

if __name__ == '__main__':
    frozen = verify_freeze()
    print(json.dumps({'protocol':VERSION, 'requestsSha256':frozen['requestPayloadSha256'],
                      'model':MODEL, 'onnxRuntimeVersion':ORT_VERSION}, ensure_ascii=False))
