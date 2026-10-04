"""Bounded source projection, label-free requests and evaluation (stdlib only)."""
import hashlib
import json
import math
import statistics
from pathlib import Path

VERSION='ai-compare-v5-1'
MODELS={
 'herbert':{'id':'allegro/herbert-base-cased','revision':'50e33e0567be0c0b313832314c586e3df0dc2297','kind':'mlm','license':'CC-BY-4.0'},
 'minilm':{'id':'MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli','revision':'0a71e92a985b6e1ad1828cf67ce9c459639c1dca','kind':'nli','license':'MIT'},
 'qwen':{'id':'Qwen/Qwen3-0.6B','revision':'c1899de289a04d12100db370d81485cdf75e47ca','kind':'causal-choice','license':'Apache-2.0'},
}
PACK_SHA='aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb'
SIDECAR_SHA='5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d'
ROOT=Path(__file__).parent

def canonical(obj):
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()

def digest(obj):
    return hashlib.sha256(canonical(obj)).hexdigest()

def readings(entry):
    """Normalize both v5 compact rows and the nine preserved full-proof entries."""
    evidence=entry.get('metadata',{}).get('sourceEvidence',{})
    if 'lexicalReadings' in evidence:
        rows=evidence['lexicalReadings']
    else:
        interpretations={i['id']:i for i in evidence.get('interpretations',[])}
        groups={}
        for p in evidence.get('generatedFormProofs',[]):
            r=interpretations[p['interpretationId']]
            obj={'lemma':r['lemma'],'partOfSpeech':r['tag'].split(':')[0],
                 'nameClasses':r['nameClasses'],'labels':r['labels']}
            identity=digest(obj)
            g=groups.setdefault(identity,{**obj,'surfaces':[]})
            if p['form'] not in g['surfaces']:g['surfaces'].append(p['form'])
        rows=list(groups.values())
    allowed={v['surface'] for v in entry['capitalization']['variants']}
    for r in rows:
        if not r['surfaces'] or not set(r['surfaces'])<=allowed:
            raise ValueError('source form association outside allowed variants')
    return sorted(rows,key=lambda r:canonical(r))

def validate_sources(source):
    if source['packSha256']!=PACK_SHA or source['sidecarSha256']!=SIDECAR_SHA:
        raise ValueError('wrong v5 source')
    entries={e['surfaceKey']:e for e in source['entries']}
    if len(entries)!=len(source['entries']):raise ValueError('duplicate lexical key')
    for key,e in entries.items():
        vs=[v['surface'] for v in e['capitalization']['variants']]
        if key!=key.lower() or not vs or len(vs)!=len(set(vs)) or any(v.lower()!=key for v in vs):
            raise ValueError('invalid key/variant')
        if e['capitalization']['defaultSurface'] not in vs:raise ValueError('missing default')
        readings(e)
    return entries

def source_text(entry):
    # Shared field labels only. No authored descriptions of a specific word.
    rows=readings(entry)
    return '\n'.join(' / '.join(r['surfaces'])+': lemat='+r['lemma']+
                     '; część mowy='+r['partOfSpeech']+
                     '; klasy='+(','.join(r['nameClasses']) or 'brak klasy NAME')+
                     '; kwalifikatory='+(','.join(r['labels']) or 'brak') for r in rows)

def requests(cases,entries):
    rows=[]
    seen=set()
    for c in cases['cases']:
        if c['id'] in seen:raise ValueError('duplicate case')
        seen.add(c['id'])
        punct=c['suite']=='punctuation_before_word'
        if punct:
            if c['goldPunctuation'] not in c['options']:raise ValueError('invalid punctuation gold')
        for window in ['short','long']:
            words=c['leftContext'].split()
            context=' '.join(words[-2:]) if window=='short' else c['leftContext']
            if len(context)>4096 or len(words)>64:raise ValueError('context exceeds frozen input limit')
            for metadata in ([False] if punct else [False,True]):
                rid=c['id']+'/'+window+'/'+('metadata' if metadata else 'plain')
                candidates=[]
                if punct:
                    candidates=[{'key':c['nextWord'].lower(),'surface':(p+' ' if p else '')+c['nextWord'],
                                 'punctuation':p,'engineScore':1,'sourceText':''}
                                for p in c['options']]
                else:
                    keys=[x['key'] for x in c['candidates']]
                    if len(keys)!=len(set(keys)):raise ValueError('duplicate slate key')
                    for s in c['candidates']:
                        e=entries[s['key']]
                        vs=e['capitalization']['variants']
                        for v in sorted(vs,key=lambda v:v['surface']!=e['capitalization']['defaultSurface']):
                            candidates.append({'key':s['key'],'surface':v['surface'],
                                               'engineScore':s['engineScore'],
                                               'sourceText':source_text(e) if metadata else ''})
                # Deterministic alternating display order counters a fixed first-option bias.
                if int(hashlib.sha256(c['id'].encode()).hexdigest()[:8],16)%2:
                    candidates=list(reversed(candidates))
                row={'id':rid,'caseId':c['id'],'suite':c['suite'],'window':window,
                     'metadata':metadata,'context':context,'candidates':candidates}
                if punct:row['nextWord']=c['nextWord']
                rows.append(row)
    return {'schemaVersion':1,'protocol':VERSION,'requests':rows}

def validate_scores(request,result):
    if result['requestsSha256']!=digest(request):raise ValueError('request hash mismatch')
    expected={r['id']:r for r in request['requests']}
    actual={r['id']:r for r in result['predictions']}
    if len(actual)!=len(result['predictions']) or set(actual)!=set(expected):
        raise ValueError('incomplete or duplicate predictions')
    for rid,p in actual.items():
        surfaces=[c['surface'] for c in expected[rid]['candidates']]
        if set(p['scores'])!=set(surfaces) or any(not math.isfinite(x) for x in p['scores'].values()):
            raise ValueError('invalid candidate scores')
    return actual

def baseline(c,entries):
    if c['suite']=='punctuation_before_word':return [c['nextWord']]
    out=[]
    for s in c['candidates']:
        e=entries[s['key']]
        out+=sorted([v['surface'] for v in e['capitalization']['variants']],
                    key=lambda v:v!=e['capitalization']['defaultSurface'])
    return out

def evaluate(cases,entries,request,result):
    predictions=validate_scores(request,result)
    by_id={c['id']:c for c in cases['cases']}
    groups={};decisions=[]
    for r in request['requests']:
        c=by_id[r['caseId']];p=predictions[r['id']]
        # Replay tests all candidates without calibrated blending of engine and LM scores.
        # Form tests have one key. Stable engine score/default order resolves exact ties.
        b=baseline(c,entries)
        options=[x['surface'] for x in r['candidates']]
        rank=sorted(options,key=lambda s:(-p['scores'][s], b.index(s) if s in b else 999))
        gold=c.get('goldSurface')
        if r['suite']=='punctuation_before_word':
            gold=(c['goldPunctuation']+' ' if c['goldPunctuation'] else '')+c['nextWord']
        group=f"{r['suite']}/{r['window']}/{'metadata' if r['metadata'] else 'plain'}"
        g=groups.setdefault(group,{'cases':0,'scoredCases':0,'top1':0,'top3':0,
                                    'baselineTop1':0,'baselineTop3':0,'repairs':0,'regressions':0,
                                    'keyTop1':0,'keyTop3':0,'baselineKeyTop1':0,'baselineKeyTop3':0,
                                    'keyMetricApplicable':r['suite']!='punctuation_before_word',
                                    'reachable':0,'latenciesMs':[]})
        g['cases']+=1;g['latenciesMs'].append(p['inferenceMs'])
        if gold is not None:
            g['scoredCases']+=1;g['reachable']+=gold in options
            g['top1']+=rank[0]==gold;g['top3']+=gold in rank[:3]
            g['baselineTop1']+=b[0]==gold;g['baselineTop3']+=gold in b[:3]
            g['repairs']+=rank[0]==gold and b[0]!=gold
            g['regressions']+=rank[0]!=gold and b[0]==gold
            if g['keyMetricApplicable']:
                key=gold.lower()
                g['keyTop1']+=rank[0].lower()==key
                g['keyTop3']+=key in [s.lower() for s in rank[:3]]
                g['baselineKeyTop1']+=b[0].lower()==key
                g['baselineKeyTop3']+=key in [s.lower() for s in b[:3]]
        decisions.append({'requestId':r['id'],'rank':rank,'gold':gold,'baseline':b,
                          'scoreGap':p['scores'][rank[0]]-p['scores'][rank[1]] if len(rank)>1 else None})
    for g in groups.values():
        ls=sorted(g.pop('latenciesMs'));g['hostLatencyP50Ms']=statistics.median(ls)
        g['hostLatencyP95Ms']=ls[max(0,math.ceil(len(ls)*.95)-1)]
    paired={}
    ds={d['requestId']:d for d in decisions}
    for r in request['requests']:
        if not r['metadata']:continue
        plain=ds[r['id'].replace('/metadata','/plain')];meta=ds[r['id']]
        k=r['suite']+'/'+r['window'];g=paired.setdefault(k,{'cases':0,'changedTop1':0,'repairs':0,'regressions':0})
        g['cases']+=1;g['changedTop1']+=plain['rank'][0]!=meta['rank'][0]
        if meta['gold'] is not None:
            g['repairs']+=meta['rank'][0]==meta['gold'] and plain['rank'][0]!=meta['gold']
            g['regressions']+=meta['rank'][0]!=meta['gold'] and plain['rank'][0]==meta['gold']
    return {'model':result['model'],'requestsSha256':digest(request),'groups':groups,
            'metadataVsPlain':paired,'decisions':decisions,
            'limitations':['Authored diagnostic contexts, not a blind external benchmark.',
                           'Forms top3 is structurally saturated by two available variants.',
                           'Recorded slates are historical top5 excerpts, not fresh v5 gestures.',
                           'Replay ranks are unblended experimental model scores, not calibrated production ranks.',
                           'Host timing and RSS do not measure the Nubia phone.',
                           'Punctuation test covers comma/none BEFORE the next word only.']}

def prepare():
    source=json.loads((ROOT/'source-snapshot.json').read_text())
    entries=validate_sources(source)
    cases=json.loads((ROOT/'cases.json').read_text())
    request=requests(cases,entries)
    return source,entries,cases,request

if __name__=='__main__':
    _,_,cases,request=prepare()
    (ROOT/'requests.json').write_bytes(canonical(request)+b'\n')
    print(len(cases['cases']),len(request['requests']),digest(request))
