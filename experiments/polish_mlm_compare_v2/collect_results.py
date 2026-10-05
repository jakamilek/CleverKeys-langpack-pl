"""Complete current models + hash-bound, exactly recomputed historical HerBERT."""
import argparse
import json
import math
import os
import re
from pathlib import Path
from contract import ROOT, MODELS, canonical, digest, prepare, verify_freeze, evaluate, reference, REFERENCE_COMMIT


def paired(reference_report, candidate_report):
    a = {d['id']: d for d in reference_report['decisions']}
    b = {d['id']: d for d in candidate_report['decisions']}
    if set(a) != set(b):
        raise ValueError('paired request IDs differ')
    groups = {}
    for rid, original in a.items():
        current = b[rid]
        if any(original[k] != current[k] for k in ['gold', 'population', 'suite', 'window', 'baseline']):
            raise ValueError('paired source/labels differ')
        key = f"{original['population']}/{original['suite']}/{original['window']}"
        g = groups.setdefault(key, {'cases': 0, 'changedTop1': 0, 'repairs': 0, 'regressions': 0})
        g['cases'] += 1
        g['changedTop1'] += original['rank'][0] != current['rank'][0]
        if original['gold'] is not None:
            g['repairs'] += current['correct'] and not original['correct']
            g['regressions'] += original['correct'] and not current['correct']
    return groups


def screening(report, historical):
    h32 = historical['groups']['new_natural/forms/32']
    c32 = report['groups']['new_natural/forms/32']
    return {'caseOnlyMobileCandidate': c32['top1'] >= h32['top1']-1 and c32['regressions'] <= h32['regressions']+1,
            'identicalShortInputsCheck': report['windowPairs']['new_natural/forms']['changedTop1'] == 0,
            'productionApproved': False,
            'limitations': 'Known diagnostic data; natural contexts <=14 words have identical 16/32 inputs. No default-window decision; artificial distance/punctuation separate.'}


def collect(root):
    frozen, request = verify_freeze(), prepare()[2]
    original, historical = reference()
    results, reports = {}, {}
    for name, preset in MODELS.items():
        matches = list(root.rglob(name + '/predictions.json'))
        if len(matches) != 1:
            raise ValueError('expected one complete result: ' + name)
        path = matches[0]
        result = json.loads(path.read_text())
        if (result['freezeManifestSha256'] != digest(frozen) or result['requestsSha256'] != digest(request)
                or result['weightsPublished'] is not False):
            raise ValueError('result freeze/publication mismatch')
        info = result['loadingInfo']
        errors = info['projectionMaxAbsErrors']
        if any(info.get(f) for f in ['missing_keys', 'mismatched_keys', 'error_msgs', 'unexpected_keys']):
            raise ValueError('incomplete original head')
        if len(errors) != 3 or any(not math.isfinite(e) or e < 0 for e in errors):
            raise ValueError('missing valid original-forward parity checks')
        validation = json.loads((path.parent / 'validation.json').read_text())
        preflight = json.loads((path.parent / 'tokenizer-validation.json').read_text())
        screen = json.loads((ROOT.parent / 'polish_mlm_screen_v2' / 'results' / (preset['id'].replace('/', '--') + '.json')).read_text())
        for verified in [result, validation, preflight]:
            if (verified['model'] != preset or verified['codeCommit'] != result['codeCommit']
                    or verified['freezeManifestSha256'] != digest(frozen)
                    or verified['requestsSha256'] != digest(request)
                    or verified['tokenizerBackendSha256'] != screen['backendSha256']):
                raise ValueError('model/tokenizer/validation identity mismatch')
        if (validation['loadingInfo'] != info or validation['modelFiles'] != result['modelFiles']
                or validation['beforeLabelledInference'] is not True
                or preflight['beforeWeightsLoad'] is not True
                or any(v['requestsValidated'] != 384 for v in [validation, preflight])):
            raise ValueError('mandatory validation differs')
        results[name], reports[name] = result, evaluate(name, result)
    commits = {r['codeCommit'] for r in results.values()}
    if (len(commits) != 1 or any(not re.fullmatch('[0-9a-f]{40}', c) for c in commits)
            or (os.environ.get('GITHUB_SHA') and commits != {os.environ['GITHUB_SHA']})):
        raise ValueError('different/invalid current commit')
    comparison = {'protocol': request['protocol'], 'codeCommit': next(iter(commits)),
                  'freezeManifestSha256': digest(frozen), 'requestsSha256': digest(request),
                  'reference': {'codeCommit': REFERENCE_COMMIT, 'model': original['model'],
                                'parameters': original['parameters'], 'report': historical},
                  'models': {name: {'model': r['model'], 'parameters': r['parameters'],
                                    'peakHostRssMiB': r['peakHostRssMiB'], 'loadingInfo': r['loadingInfo'],
                                    **reports[name]} for name, r in results.items()},
                  'vsHistoricalHerbert': {name: paired(historical, report) for name, report in reports.items()},
                  'screening': {name: screening(report, historical) for name, report in reports.items()},
                  'phoneMeasured': False, 'productionApproved': False,
                  'distilherbertRedistributionApproved': False,
                  'limitations': ['Same known authored v1 data; not blind or newly independent.',
                                  'Reference intentionally historical pinned code; quality paired, host performance not paired.',
                                  'Two-form top3 structurally saturated; no AI benefit claim.',
                                  'Natural <=14 words: no evidence for truncating real longer context.',
                                  'Comma/none before known next word, no punctuation activation.',
                                  'No weights published, no export, Android/live setting or release.']}
    (root / 'comparison.json').write_bytes(canonical(comparison)+b'\n')
    lines = ['# Polski MLM v2 — Geotrend / distilHerBERT / historyczny HerBERT', '',
             '| Populacja/zadanie/okno | HerBERT (referencja v1) | Geotrend Distil | distilHerBERT |', '|---|---:|---:|---:|']
    for key, h in historical['groups'].items():
        cells = [f"{r['groups'][key]['top1']}/{r['groups'][key]['labelled']}" for r in reports.values()]
        lines.append(f"| {key} | {h['top1']}/{h['labelled']} | " + ' | '.join(cells) + ' |')
    lines += ['', 'Autorska diagnostyka znanych kluczy, historyczna referencja; brak niezależnego benchmarku.',
              'Top3 par nasycone z konstrukcji; naturalne 16/32 mają identyczne wejście.',
              'Pełne rankingi, naprawy/regresje i osobny dystans/interpunkcja w comparison.json.',
              'Brak pomiaru telefonu, aktywacji SI i redystrybucji wag. Licencja distilHerBERT niewyjaśniona.',
              '', json.dumps(comparison['screening'], ensure_ascii=False)]
    (root / 'COMPARISON.md').write_text('\n'.join(lines)+'\n', encoding='utf-8')
    return comparison


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', required=True, type=Path)
    collect(parser.parse_args().root)
