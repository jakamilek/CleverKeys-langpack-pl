"""Paired metadata format/instruction study, using frozen v5 source extraction."""
import copy
import hashlib
import json
import math
import statistics
import sys
from pathlib import Path
ROOT=Path(__file__).parent
BASE=ROOT.parent/'ai_compare_v5'
sys.path.insert(0,str(BASE))
import contract as legacy
from render_metadata import explained_text,GUIDANCE
MODELS=legacy.MODELS
canonical=legacy.canonical
digest=legacy.digest
VERSION='ai-metadata-v5-1'
CONDITIONS=('plain','raw','explained','guided','plain_guided')

def requests(cases,entries):
    out=[]
    ids=[c['id'] for c in cases['cases']]
    if len(ids)!=len(set(ids)):raise ValueError('duplicate case')
    for c in cases['cases']:
        if c['suite']=='punctuation_before_word':raise ValueError('punctuation outside this study')
        old=legacy.requests({'cases':[c]},entries)['requests']
        for window in ['short','long']:
            for condition in CONDITIONS:
                probe=next(r for r in old if r['window']==window and r['metadata']==(condition not in {'plain','plain_guided'}))
                r=copy.deepcopy(probe)
                r['id']=c['id']+'/'+window+'/'+condition
                r['condition']=condition
                r['instruction']=GUIDANCE if condition in {'guided','plain_guided'} else ''
                if condition in {'explained','guided'}:
                    for candidate in r['candidates']:
                        candidate['sourceText']=explained_text(legacy.readings(entries[candidate['key']]))
                out.append(r)
    return {'schemaVersion':1,'protocol':VERSION,'requests':out}

def prepare():
    source=json.loads((BASE/'source-snapshot.json').read_text())
    entries=legacy.validate_sources(source)
    cases=json.loads((ROOT/'cases.json').read_text())
    for c in cases['cases']:
        if c['population'] not in {'new','reused'}:raise ValueError('unknown population')
        if c['suite']!='missing_key' and c['goldSurface'] is not None:
            if c['goldSurface'] not in legacy.baseline(c,entries):raise ValueError('unreachable gold')
    return source,entries,cases,requests(cases,entries)

def verify_freeze():
    frozen=json.loads((ROOT/'freeze-manifest.json').read_text())
    for p,h in frozen['files'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('freeze mismatch: '+p)
    workflow=ROOT.parents[1]/'.github/workflows/ai-metadata-v5.yml'
    if hashlib.sha256(workflow.read_bytes()).hexdigest()!=frozen['workflowSha256']:
        raise ValueError('workflow mismatch')
    if digest(prepare()[3])!=frozen['requestPayloadSha256']:raise ValueError('request mismatch')
    if frozen['modelPresets']!=MODELS:raise ValueError('model preset mismatch')
    return frozen

def validate_result(request,result):
    if result['protocol']!=VERSION:raise ValueError('protocol mismatch')
    actual=legacy.validate_scores(request,result)
    for p in actual.values():
        if not math.isfinite(p['inferenceMs']) or p['inferenceMs']<0:raise ValueError('invalid latency')
    return actual

def evaluate(cases,entries,request,result):
    predictions=validate_result(request,result)
    by_id={c['id']:c for c in cases['cases']};groups={};decisions=[]
    for r in request['requests']:
        c=by_id[r['caseId']];p=predictions[r['id']];b=legacy.baseline(c,entries)
        options=[x['surface'] for x in r['candidates']]
        rank=sorted(options,key=lambda s:(-p['scores'][s],b.index(s)))
        gold=c['goldSurface'];key='/'.join([c['suite'],c['population'],r['window'],r['condition']])
        g=groups.setdefault(key,{'cases':0,'scoredCases':0,'top1':0,'top3':0,'baselineTop1':0,
                                'baselineTop3':0,'repairs':0,'regressions':0,'keyTop1':0,
                                'keyTop3':0,'reachable':0,'latencies':[]})
        g['cases']+=1;g['latencies'].append(p['inferenceMs'])
        if gold is not None:
            g['scoredCases']+=1;g['reachable']+=gold in options
            g['top1']+=rank[0]==gold;g['top3']+=gold in rank[:3]
            g['baselineTop1']+=b[0]==gold;g['baselineTop3']+=gold in b[:3]
            g['repairs']+=rank[0]==gold and b[0]!=gold
            g['regressions']+=rank[0]!=gold and b[0]==gold
            g['keyTop1']+=rank[0].lower()==gold.lower()
            g['keyTop3']+=gold.lower() in [x.lower() for x in rank[:3]]
        decisions.append({'requestId':r['id'],'rank':rank,'gold':gold,'baseline':b,
                          'population':c['population'],'scores':p['scores']})
    for g in groups.values():
        ls=sorted(g.pop('latencies'));g['hostLatencyP50Ms']=statistics.median(ls)
        g['hostLatencyP95Ms']=ls[max(0,math.ceil(len(ls)*.95)-1)]
    ds={d['requestId']:d for d in decisions};paired={}
    for c in cases['cases']:
        for window in ['short','long']:
            for before,after in [('plain','raw'),('raw','explained'),('explained','guided'),
                                 ('plain','plain_guided'),('plain_guided','guided')]:
                a=ds[c['id']+'/'+window+'/'+before];b=ds[c['id']+'/'+window+'/'+after]
                key='/'.join([c['suite'],c['population'],window,before+'->'+after])
                g=paired.setdefault(key,{'cases':0,'scoredCases':0,'changedTop1':0,'repairs':0,'regressions':0})
                g['cases']+=1;g['changedTop1']+=a['rank'][0]!=b['rank'][0]
                if b['gold'] is not None:
                    g['scoredCases']+=1
                    g['repairs']+=b['rank'][0]==b['gold'] and a['rank'][0]!=a['gold']
                    g['regressions']+=b['rank'][0]!=b['gold'] and a['rank'][0]==a['gold']
    return {'model':result['model'],'groups':groups,'pairedConditions':paired,'decisions':decisions,
            'requestsSha256':digest(request),'productionModelSelected':False,
            'limitations':['Previously evaluated cases reported separately from 32 new authored contexts.',
                           'New contexts use known keys and are not a blind external corpus.',
                           'Two-form top3 is structurally saturated, including baseline.',
                           'Metadata is morphology/name classes, not complete lexical meanings.',
                           'Instruction-following is not guaranteed for MLM/NLI.',
                           'Historical slates and unblended scores are not a production ranking.',
                           'No punctuation, quantization, mobile or training results in this study.']}

if __name__=='__main__':
    source,entries,cases,request=prepare()
    print(json.dumps({'cases':len(cases['cases']),'requests':len(request['requests']),
                      'payloadSha256':digest(request),'freezeVerified':bool(verify_freeze())}))
