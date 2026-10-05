"""Recompute both models from complete raw predictions; no pooled new/old accuracy."""
import argparse
import json
import os
from pathlib import Path
from contract import ROOT, MODELS, canonical, digest, prepare, verify_freeze, evaluate


def collect(root):
    frozen = verify_freeze()
    request = prepare()[2]
    results, reports = {}, {}
    for name in MODELS:
        matches = list(root.rglob(name + '/predictions.json'))
        if len(matches) != 1:
            raise ValueError('expected one complete model result: ' + name)
        result = json.loads(matches[0].read_text())
        if result['freezeManifestSha256'] != digest(frozen) or result['requestsSha256'] != digest(request):
            raise ValueError('freeze mismatch')
        results[name] = result
        reports[name] = evaluate(name, result)
    commits = {r['codeCommit'] for r in results.values()}
    if (len(commits) != 1 or not all(len(c) == 40 for c in commits)
            or (os.environ.get('GITHUB_SHA') and commits != {os.environ['GITHUB_SHA']})):
        raise ValueError('different/invalid producer commit')
    paired = {}
    h = {d['id']: d for d in reports['herbert']['decisions']}
    d = {d['id']: d for d in reports['distilroberta']['decisions']}
    for rid, a in h.items():
        b = d[rid]
        group = f"{a['population']}/{a['suite']}/{a['window']}"
        g = paired.setdefault(group, {'cases': 0, 'changedTop1': 0, 'repairs': 0, 'regressions': 0})
        g['cases'] += 1
        g['changedTop1'] += a['rank'][0] != b['rank'][0]
        if a['gold'] is not None:
            g['repairs'] += b['correct'] and not a['correct']
            g['regressions'] += a['correct'] and not b['correct']
    h32 = reports['herbert']['groups']['new_natural/forms/32']
    d16 = reports['distilroberta']['groups']['new_natural/forms/16']
    d32 = reports['distilroberta']['groups']['new_natural/forms/32']
    screening = {
        'caseOnlyMobileCandidate': d32['top1'] >= h32['top1'] - 1 and d32['regressions'] <= h32['regressions'] + 1,
        'context16Candidate': d16['top1'] >= d32['top1'] - 1 and d16['lowerRegressions'] <= d32['lowerRegressions'] + 1,
        'productionApproved': False,
        'criterion': 'new_natural/32 top1 >= HerBERT-1 and baseline regressions <=HerBERT+1; 16 top1 >=32-1 and lower regressions <=32+1',
        'limitations': 'Small exploratory screening, not statistical noninferiority; distance losses remain separately visible; no punctuation activation.'}
    comparison = {'protocol': request['protocol'], 'codeCommit': commits.pop(),
                  'freezeManifestSha256': digest(frozen), 'requestsSha256': digest(request),
                  'models': {name: {'model': r['model'], 'parameters': r['parameters'],
                                    'peakHostRssMiB': r['peakHostRssMiB'],
                                    'loadingInfo': r['loadingInfo'], **reports[name]} for name, r in results.items()},
                  'distilrobertaVsHerbert': paired, 'screening': screening, 'phoneMeasured': False,
                  'limitations': ['New contexts authored before inference, known lexical keys, not blind external validation.',
                                  'Distance control is deliberately constructed and reported separately.',
                                  'Two-form top3 is saturated; do not use it as evidence of AI accuracy.',
                                  'Punctuation is comma/none before a known next word only.',
                                  'Host float32 RSS/timings include runtime and differ across runners; no Android prediction.',
                                  'No quantization, model export, live IME or automatic release decision.']}
    (root / 'comparison.json').write_bytes(canonical(comparison) + b'\n')
    lines = ['# Polski MLM — HerBERT / DistilRoBERTa, 16 / 32 słowa', '',
             '| Populacja / zadanie / okno | HerBERT top1 | DistilRoBERTa top1 |',
             '|---|---:|---:|']
    for key, a in reports['herbert']['groups'].items():
        b = reports['distilroberta']['groups'][key]
        lines.append(f"| {key} | {a['top1']}/{a['labelled']} | {b['top1']}/{b['labelled']} |")
    lines += ['', '| Model | Faktyczne parametry | Szczyt RSS procesu hosta MiB |', '|---|---:|---:|']
    for name, r in results.items():
        lines.append(f"| {name} | {r['parameters']} | {r['peakHostRssMiB']:.1f} |")
    lines += ['', 'Brak pomiaru telefonu. To autorska diagnostyka ze znanymi kluczami, nie niezależny benchmark.',
              'Top3 par jest nasycone konstrukcją. Kontrola dystansu i stare regresje są osobnymi populacjami.',
              'Interpunkcja: tylko przecinek/brak znaku przed znanym słowem. Brak kwantyzacji i integracji.',
              'Pełne czasy, rankingi, naprawy/regresje i porównania sparowane są w comparison.json.']
    lines += ['', 'Wstępny screening (nie decyzja wdrożeniowa): ' + json.dumps(screening, ensure_ascii=False)]
    (root / 'COMPARISON.md').write_text('\n'.join(lines) + '\n')
    return comparison


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--root', type=Path, required=True)
    collect(parser.parse_args().root)
