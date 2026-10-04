"""Compare only complete verified results; do not select a model from missing jobs."""
import argparse
import json
import hashlib
import os
from pathlib import Path
from contract import ROOT,MODELS,canonical,prepare,evaluate,validate_scores,digest

def collect(root):
    source,entries,cases,request=prepare()
    reports={};missing=[];environments={}
    for name in MODELS:
        paths=list(root.rglob(name+'/predictions.json'))
        if len(paths)!=1:missing.append(name);continue
        result=json.loads(paths[0].read_text())
        if result['model']!=MODELS[name]:raise ValueError('wrong model preset')
        if result['codeCommit']!=os.environ.get('GITHUB_SHA'):raise ValueError('wrong inference commit')
        if result['freezeManifestSha256']!=hashlib.sha256((ROOT/'freeze-manifest.json').read_bytes()).hexdigest():
            raise ValueError('wrong frozen experiment')
        if result['sourceSnapshotSha256']!=hashlib.sha256((ROOT/'source-snapshot.json').read_bytes()).hexdigest():
            raise ValueError('wrong source snapshot')
        reports[name]=evaluate(cases,entries,request,result)
        environments[name]={k:result[k] for k in ['environment','parameters','loadSecondsIncludingDownload',
                                                  'inferenceSeconds','peakHostRssMiB','loadingInfo','method']}
    summary={'protocol':request['protocol'],'requestsSha256':digest(request),
             'complete':not missing,'missingModels':missing,'reports':reports,
             'hostMeasurements':environments,'productionModelSelected':False}
    rows=['# Porównanie SI — v5','',
          'Pełne porównanie: '+('TAK' if not missing else 'NIE; brak '+', '.join(missing)),
          '', '## Pisownia: nowe 64 konteksty, długie okno', '',
          '| System | Top 1 | Top 3 | Naprawy / regresje względem defaultu |',
          '|---|---:|---:|---:|', '| Default v5 | 32/64 | 64/64 | — |']
    for name,report in reports.items():
        for condition in ['plain','metadata']:
            g=report['groups']['forms/long/'+condition]
            rows.append(f"| {name} / {condition} | {g['top1']}/64 | {g['top3']}/64 | {g['repairs']} / {g['regressions']} |")
    rows+=['','Top 3 w tej części jest nasycone konstrukcją dwóch wariantów. Nie dowodzi przewagi SI.',
           '', '## Historyczne rankingi: 8 nowych kontekstów', '',
           '| System | Top 1 | Top 3 | Default top 1 / top 3 |','|---|---:|---:|---:|']
    for name,report in reports.items():
        for condition in ['plain','metadata']:
            g=report['groups']['recorded_replay/long/'+condition]
            rows.append(f"| {name} / {condition} | {g['top1']}/8 | {g['top3']}/8 | {g['baselineTop1']}/8 / {g['baselineTop3']}/8 |")
    rows+=['','Te rankingi to historyczne top 5 z logu; modelowe sortowanie jest niekalibrowane i nie trafia do klawiatury.',
           '', '## Przecinek przed kolejnym słowem: 20 przypadków', '',
           '| System | Trafienia | Default bez przecinka |','|---|---:|---:|']
    for name,report in reports.items():
        g=report['groups']['punctuation_before_word/long/plain']
        rows.append(f"| {name} | {g['top1']}/20 | {g['baselineTop1']}/20 |")
    rows+=['','Nie jest to pełny test interpunkcji: tylko przecinek/brak znaku przed znanym kolejnym słowem.',
           '', '## Granice wniosku', '',
           'Konteksty są ręczną diagnostyką, a nie ślepą próbą korpusową. Nie dobrano modelu ani promptu po wynikach.',
           'Hostowe float32 RSS i czasy nie określają działania na Nubia Z60 Ultra LV 12/512 GB.',
           'Pomiary kwantyzacji, telefonu i szersze rzeczywiste maźnięcia pozostają przed wyborem produkcyjnym.']
    (root/'comparison.json').write_bytes(canonical(summary)+b'\n')
    (root/'COMPARISON.md').write_text('\n'.join(rows)+'\n')
    print('\n'.join(rows))
    if missing:raise ValueError('comparison incomplete')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();collect(a.root)
