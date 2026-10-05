"""Require both complete current-commit models; separate fresh strata and regression."""
import argparse
import json
import math
import os
import re
from pathlib import Path
from contract import ROOT, MODELS, canonical, digest, prepare, verify_freeze, evaluate


def paired(a, b):
    left={x['id']:x for x in a['decisions']};right={x['id']:x for x in b['decisions']}
    if set(left)!=set(right):raise ValueError('unpaired decisions')
    groups={}
    for rid,x in left.items():
        y=right[rid]
        if any(x[k]!=y[k] for k in ['gold','population','suite','window','baseline']):
            raise ValueError('unpaired source/gold')
        key=f"{x['population']}/{x['suite']}/{x['window']}"
        g=groups.setdefault(key,dict(cases=0,changedTop1=0,repairs=0,regressions=0))
        g['cases']+=1;g['changedTop1']+=x['rank'][0]!=y['rank'][0]
        g['repairs']+=y['correct'] and not x['correct']
        g['regressions']+=x['correct'] and not y['correct']
    return groups


def screening(candidate, reference):
    # Explicitly exploratory; every stratum must pass. Never aggregate away regressions.
    rows={}
    for key,c in candidate['groups'].items():
        if not key.startswith('fresh_') or not key.endswith('/32'):continue
        h=reference['groups'][key]
        rows[key]={'top1AtLeastReferenceMinusOne':c['top1']>=h['top1']-1,
                   'baselineRegressionsAtMostReferencePlusOne':c['regressions']<=h['regressions']+1,
                   'candidateTop1':c['top1'],'referenceTop1':h['top1']}
    # Original 64 historical forms remain a distinct regression gate.
    c=candidate['groups']['regression_v5/forms/32'];h=reference['groups']['regression_v5/forms/32']
    old={'top1AtLeastReferenceMinusOne':c['top1']>=h['top1']-1,
         'candidateTop1':c['top1'],'referenceTop1':h['top1']}
    return {'freshStrata':rows,'knownRegression':old,
            'exploratoryCaseCandidate':all(x['top1AtLeastReferenceMinusOne'] and x['baselineRegressionsAtMostReferencePlusOne'] for x in rows.values()) and old['top1AtLeastReferenceMinusOne'],
            'productionApproved':False,'default16Approved':False}


def collect(root):
    frozen=verify_freeze();request=prepare()[2];count=len(request['requests'])
    reports={};results={}
    for name,preset in MODELS.items():
        paths=list(root.rglob(name+'/predictions.json'))
        if len(paths)!=1:raise ValueError('one complete result required: '+name)
        path=paths[0];r=json.loads(path.read_text())
        v=json.loads((path.parent/'validation.json').read_text());p=json.loads((path.parent/'tokenizer-validation.json').read_text())
        for doc in [r,v,p]:
            if doc['model']!=preset or doc['requestsSha256']!=digest(request) or doc['freezeManifestSha256']!=digest(frozen) or doc['codeCommit']!=r['codeCommit'] or doc['tokenizerBackendSha256']!=r['tokenizerBackendSha256']:
                raise ValueError('different pinned model/freeze/tokenizer/commit')
        if not re.fullmatch('[0-9a-f]{64}',r['tokenizerBackendSha256']):raise ValueError('bad tokenizer identity')
        if name=='distilherbert':
            screen=json.loads((ROOT.parent/'polish_mlm_screen_v2/results/BartekK--distilHerBERT-base-cased.json').read_text())
            if r['tokenizerBackendSha256']!=screen['backendSha256']:raise ValueError('changed original tokenizer')
        info=r['loadingInfo'];errors=info['projectionMaxAbsErrors']
        if any(info.get(k) for k in ['missing_keys','mismatched_keys','unexpected_keys','error_msgs']):raise ValueError('incomplete head')
        if len(errors)!=3 or any(not math.isfinite(e) or not 0<=e<=.001 for e in errors):raise ValueError('bad original-forward parity')
        if (v['loadingInfo']!=info or v['modelFiles']!=r['modelFiles'] or v['sourceCasePreservation'] is not True or v['beforeLabelledInference'] is not True or p['beforeWeightsLoad'] is not True or any(d['requestsValidated']!=count for d in [v,p])):raise ValueError('mandatory preflight differs')
        if r['weightsPublished'] is not False or r['phoneMeasured'] is not False:raise ValueError('wrong experiment scope')
        weights=[f for f in r['modelFiles'] if f['path'].endswith(('.bin','.safetensors'))]
        if not weights or any(f['bytes']<=0 or not re.fullmatch('[0-9a-f]{64}',f['sha256']) for f in weights):raise ValueError('missing hashed original weights')
        if r['parameters']<=0 or not math.isfinite(r['peakHostRssMiB']) or r['peakHostRssMiB']<=0:raise ValueError('invalid cost metadata')
        reports[name]=evaluate(name,r);results[name]=r
        by_id={x['id']:x for x in request['requests']}
        for pred in r['predictions']:
            row=by_id[pred['id']]
            if len(pred['trace'])!=len(row['candidates']) or len(pred['inputTokens'])!=len(row['candidates']):
                raise ValueError('missing per-candidate token evidence')
            for surface,trace,tokens in zip(row['candidates'],pred['trace'],pred['inputTokens']):
                positions=trace['targetPositions'];targets=trace['targetTokenIds']
                if not positions or len(positions)!=len(targets) or positions!=list(range(positions[0],positions[-1]+1)) or any(type(p) is not int or not 0<=p<tokens for p in positions) or any(type(t) is not int or t<0 for t in targets) or not 0<tokens<=512 or trace['inputTokens']!=tokens:
                    raise ValueError('invalid target token trace')
                mean,total=trace['meanLogProbability'],trace['sumLogProbability']
                if not math.isfinite(mean) or not math.isfinite(total) or abs(mean-pred['scores'][surface])>1e-6 or abs(total/len(targets)-mean)>1e-6:
                    raise ValueError('score and original target trace differ')
        if reports[name]!=json.loads((path.parent/'report.json').read_text()):raise ValueError('raw report recomputation differs')
    commits={r['codeCommit'] for r in results.values()}
    if len(commits)!=1 or any(not re.fullmatch('[0-9a-f]{40}',c) for c in commits) or (os.environ.get('GITHUB_SHA') and commits!={os.environ['GITHUB_SHA']}):raise ValueError('stale/different run commit')
    out={'protocol':request['protocol'],'codeCommit':next(iter(commits)),
         'freezeManifestSha256':digest(frozen),'requestsSha256':digest(request),
         'models':{name:{'model':r['model'],'parameters':r['parameters'],'peakHostRssMiB':r['peakHostRssMiB'],**reports[name]} for name,r in results.items()},
         'vsCurrentHerbert':paired(reports['herbert'],reports['distilherbert']),
         'screening':screening(reports['distilherbert'],reports['herbert']),
         'inputs':{'equalWindows':sum(x['context']==request['requests'][i+1]['context'] for i,x in enumerate(request['requests']) if i%2==0),
                   'differentWindows':sum(x['context']!=request['requests'][i+1]['context'] for i,x in enumerate(request['requests']) if i%2==0)},
         'productionApproved':False,'phoneMeasured':False,'licenseReviewDeferred':True,
         'limitations':['Fresh authored diagnostic contexts, not externally independent or human-reviewed blind gold.',
                        'Long natural contexts 21-26 words, not representative private conversations or >32 word evaluation.',
                        'Both current models rerun; host jobs are not controlled Android RAM/energy/latency evidence.',
                        'No punctuation scoring, live SI, default-window decision, APK, export or weights redistribution.',
                        'Top3 of a two-form pair is structurally saturated without AI; only top1 informs this diagnostic.']}
    (root/'comparison.json').write_bytes(canonical(out)+b'\n')
    lines=['# Polski MLM — świeże konteksty v3','','| Populacja/okno | HerBERT | distilHerBERT |','|---|---:|---:|']
    for key,h in reports['herbert']['groups'].items():
        c=reports['distilherbert']['groups'][key]
        lines.append(f"| {key} | {h['top1']}/{h['labelled']} | {c['top1']}/{c['labelled']} |")
    lines+=['','Świeże autorskie konteksty; nie niezależny benchmark. Pełne regresje i limity okien w JSON.',
            'Brak aktywacji SI, zmiany domyślnego kontekstu, pomiaru telefonu i publikacji wag.','',json.dumps(out['screening'],ensure_ascii=False)]
    (root/'COMPARISON.md').write_text('\n'.join(lines)+'\n');return out


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);collect(p.parse_args().root)
