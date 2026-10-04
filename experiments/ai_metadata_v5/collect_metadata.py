"""Recompute reports from actual predictions with every experiment identity checked."""
import argparse
import hashlib
import json
import os
from pathlib import Path
from contract_meta import ROOT,BASE,MODELS,CONDITIONS,prepare,verify_freeze,evaluate,canonical,digest

def collect(root):
    verify_freeze();source,entries,cases,request=prepare();reports={};missing=[];hosts={}
    for name in MODELS:
        paths=list(root.rglob(name+'/predictions.json'))
        if len(paths)!=1:missing.append(name);continue
        result=json.loads(paths[0].read_text())
        if result['model']!=MODELS[name]:raise ValueError('wrong model preset')
        if result['codeCommit']!=os.environ.get('GITHUB_SHA'):raise ValueError('wrong inference commit')
        if result['freezeManifestSha256']!=hashlib.sha256((ROOT/'freeze-manifest.json').read_bytes()).hexdigest():raise ValueError('wrong freeze')
        if result['sourceSnapshotSha256']!=hashlib.sha256((BASE/'source-snapshot.json').read_bytes()).hexdigest():raise ValueError('wrong source')
        reports[name]=evaluate(cases,entries,request,result)
        hosts[name]={k:result[k] for k in ['parameters','loadingInfo','environment','inferenceSeconds',
                                          'loadSecondsIncludingDownload','peakHostRssMiB']}
    summary={'protocol':request['protocol'],'complete':not missing,'missingModels':missing,
             'requestsSha256':digest(request),'reports':reports,'hostMeasurements':hosts,
             'productionModelSelected':False}
    rows=['# Objaśnienia i instrukcja metadanych v5','',
          'Pełne porównanie: '+('TAK' if not missing else 'NIE; brak '+', '.join(missing)),'']
    for population,n in [('new',32),('reused',64)]:
        rows+=['## Formy — '+population+', długi kontekst','',
               '| Model | Warunek | Top 1 | Top 3 | Naprawy / regresje wobec defaultu |',
               '|---|---|---:|---:|---:|']
        for name,r in reports.items():
            for condition in CONDITIONS:
                g=r['groups']['forms/'+population+'/long/'+condition]
                rows.append(f"| {name} | {condition} | {g['top1']}/{n} | {g['top3']}/{n} | {g['repairs']} / {g['regressions']} |")
        rows+=['','Top 3 jest nasycone dwoma wariantami także bez SI.','']
    rows+=['## Oddzielne efekty formatu i instrukcji — nowe 32 konteksty','',
           '| Model | Zmiana | Naprawy | Regresje |','|---|---|---:|---:|']
    for name,r in reports.items():
        for before,after in [('plain','raw'),('raw','explained'),('explained','guided'),
                             ('plain','plain_guided'),('plain_guided','guided')]:
            g=r['pairedConditions']['forms/new/long/'+before+'->'+after]
            rows.append(f"| {name} | {before} → {after} | {g['repairs']} | {g['regressions']} |")
    rows+=['','## Historyczne rankingi — długi kontekst','',
           '| Model | Warunek | Dokładna forma top 1 | Top 3 |','|---|---|---:|---:|']
    for name,r in reports.items():
        for condition in CONDITIONS:
            g=r['groups']['recorded_replay/reused/long/'+condition]
            rows.append(f"| {name} | {condition} | {g['top1']}/8 | {g['top3']}/8 |")
    rows+=['','Próba ma 84 powtórzone i 32 nowe ręcznie napisane przypadki; nie jest ślepym korpusem.',
           'Opisy są generowane z lemma/POS/NAME/labels/surfaces; nie dodano znaczeń per słowo.',
           'MLM/NLI nie były uczone wykonywania tych instrukcji; guided jest eksperymentalnym tekstem.',
           'Reranking replay nie jest kalibrowany z geometrią. Interpunkcja i telefon są poza zakresem.']
    (root/'comparison.json').write_bytes(canonical(summary)+b'\n')
    (root/'COMPARISON.md').write_text('\n'.join(rows)+'\n');print('\n'.join(rows))
    if missing:raise ValueError('comparison incomplete')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args();collect(a.root)
