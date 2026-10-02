#!/usr/bin/env python3
"""Frozen source-category experiment. No handwritten per-word meanings."""
import argparse
import copy
import hashlib
import json
import math
import time
from pathlib import Path

from prototype import canonical_bytes, digest, load_sidecar, prepare, resolve, validate_predictions
from plt5_adapter import check_request
from sense_experiment import MODEL_ID, MODEL_REVISION, preflight
from natural_experiment import run_mlm as shared_run_mlm
from source_category_cases import MAIN, build as build_cases

ROOT = Path(__file__).parent
SOURCE = ROOT.parent/'source_metadata_v1'/'source-metadata-audit.json'
SOURCE_SHA = '83ae7299c4781bd0cb731db6d5653cbc6f6b840c38d4b60a1797f40e894c6a4a'
VERSION = 'source-category-surface-v1'
CONDITIONS = ('source_categories','no_attributes')
# One generic rendering per source category, reused across all keys. It does
# not add fruit/boat/street/country facts or assert missing surnames.
PHRASES = {'NAME:nazwa_pospolita':'wyrazem pospolitym',
           'NAME:nazwa_geograficzna':'nazwą geograficzną',
           'NAME:imię':'imieniem osoby', 'NAME:nazwisko':'nazwiskiem osoby',
           'POS:adj':'przymiotnikiem', 'POS:adjp':'przymiotnikiem'}


def generate_sidecar():
    import importlib.metadata
    import morfeusz2
    raw=SOURCE.read_bytes()
    if hashlib.sha256(raw).hexdigest()!=SOURCE_SHA:
        raise ValueError('source audit hash mismatch')
    source=json.loads(raw)
    m=morfeusz2.Morfeusz()
    if importlib.metadata.version('morfeusz2')!='1.99.15' or m._morfeusz_obj.getDictID()!=source['morfeusz']['dictionaryId']:
        raise ValueError('morphology source version mismatch')
    entries=[]
    for example in source['selectedExamples']:
        key=example['surfaceKey']
        interpretations={}
        proofs=[]
        associations={}
        categories={}
        for rows in example['probes'].values():
            for row in rows:
                interpretation={k:row[k] for k in ('lemma','tag','nameClasses','labels')}
                rid=digest(interpretation)[:16]
                if rid in interpretations:
                    continue
                interpretations[rid]={'id':rid,**interpretation}
                pos=row['tag'].split(':')[0]
                ids=['NAME:'+n for n in row['nameClasses']] or ['POS:'+pos]
                for cid in ids:
                    if cid not in PHRASES:
                        raise ValueError('unreviewed generic category renderer: '+cid)
                    categories[cid]={'id':cid,'sourceField':'NAME' if row['nameClasses'] else 'TAG',
                                     'sourceValue':cid.split(':',1)[1]}
                matched=False
                for form,lemma,tag,names,labels in m.generate(row['lemma']):
                    if form.lower()!=key or tag.split(':')[0]!=pos or sorted(names)!=row['nameClasses']:
                        continue
                    if form not in {key,key.capitalize()}:
                        raise ValueError('unsupported generated casing')
                    matched=True
                    proof={'interpretationId':rid,'form':form,'lemma':lemma,'tag':tag,
                           'nameClasses':sorted(names),'labels':sorted(labels)}
                    if proof not in proofs:
                        proofs.append(proof)
                    associations.setdefault(form,set()).update(ids)
                if not matched:
                    raise ValueError('unassociated source interpretation: '+row['lemma'])
        variants=[{'surface':surface,'casePolicy':'lowercase' if surface==key else 'capitalized',
                   'categoryIds':sorted(associations[surface])}
                  for surface in sorted(associations,key=lambda v:(v!=key,v))]
        default=example['packCanonicalSurface']
        if default not in associations:
            raise ValueError('canonical form absent from generated forms')
        entries.append({'surfaceKey':key,'capitalization':{'defaultSurface':default,'variants':variants},
                        'categories':[categories[c] for c in sorted(categories)],
                        'interpretations':[interpretations[i] for i in sorted(interpretations)],
                        'generatedFormProofs':proofs,'sourceRecords':example['sourceRecords']})
    return {'schemaVersion':1,'languageCode':'pl','experimentExtension':VERSION,
            'provenance':{'sourceAuditSha256':SOURCE_SHA,'sourceAuditCommit':'cd03c3002e7164eac5d972a2a8b502873177ca09',
                          'morfeusz':source['morfeusz'],'artifact':source['artifact']},'entries':entries}


def validate_sidecar(sidecar):
    _,entries=load_sidecar(sidecar)
    if sidecar.get('experimentExtension')!=VERSION:
        raise ValueError('wrong source extension')
    for entry in entries.values():
        categories=entry['categories']
        ids={c['id'] for c in categories}
        if len(ids)!=len(categories) or not ids<=PHRASES.keys():
            raise ValueError('invalid categories')
        used=set()
        for variant in entry['capitalization']['variants']:
            refs=variant['categoryIds']
            if not refs or len(refs)!=len(set(refs)) or not set(refs)<=ids:
                raise ValueError('dangling category association')
            used.update(refs)
            if not any(p['form']==variant['surface'] for p in entry['generatedFormProofs']):
                raise ValueError('variant lacks generated source proof')
        if used!=ids:
            raise ValueError('orphan source category')
        raw_ids={r['id'] for r in entry['interpretations']}
        linked={p['interpretationId'] for p in entry['generatedFormProofs']}
        if raw_ids!=linked:
            raise ValueError('lost or invented interpretation')
        raw={r['id']:r for r in entry['interpretations']}
        expected={v['surface']:set() for v in entry['capitalization']['variants']}
        for proof in entry['generatedFormProofs']:
            origin=raw[proof['interpretationId']]
            if proof['form'] not in expected or proof['form'].lower()!=entry['surfaceKey']:
                raise ValueError('proof belongs to wrong form')
            if proof['lemma']!=origin['lemma'] or proof['nameClasses']!=origin['nameClasses'] or proof['tag'].split(':')[0]!=origin['tag'].split(':')[0]:
                raise ValueError('proof changes source interpretation')
            refs=['NAME:'+n for n in proof['nameClasses']] or ['POS:'+proof['tag'].split(':')[0]]
            expected[proof['form']].update(refs)
        for variant in entry['capitalization']['variants']:
            if set(variant['categoryIds'])!=expected[variant['surface']]:
                raise ValueError('category association differs from generated source proofs')
    return entries


def prepare_requests(cases,sidecar):
    entries=validate_sidecar(sidecar)
    request=prepare(cases,sidecar)
    for row in request['requests']:
        for group in row['candidates']:
            if group['languageCode']=='pl' and group['surfaceKey'] in entries:
                entry=entries[group['surfaceKey']]
                group['categories']=copy.deepcopy(entry['categories'])
                group['variantCategoryIds']={v['surface']:v['categoryIds'] for v in entry['capitalization']['variants']}
                group['interpretations']=copy.deepcopy(entry['interpretations'])
    request['experimentExtension']=VERSION
    del request['requestSha256'];request['requestSha256']=digest(request)
    return request


def hypothesis(key,cid):
    return f'W tym kontekście ostatnie dopisywane słowo „{key}” jest {PHRASES[cid]}.'


def associated_scores(group,values):
    ids={c['id'] for c in group['categories']}
    if set(values)!=ids or any(not math.isfinite(v) for v in values.values()):
        raise ValueError('invalid category scores')
    return {v:max(values[c] for c in group['variantCategoryIds'][v]) for v in group['variants']}


def validate_category_predictions(prediction,request):
    evidence=validate_predictions(prediction,request)
    requests={r['requestId']:r for r in request['requests']}
    for result in prediction['results']:
        values=result.get('categoryScores',[])
        if prediction.get('condition')!='source_categories':
            if values:raise ValueError('unexpected category scores')
            continue
        groups={g['surfaceKey']:g for g in requests[result['requestId']]['candidates'] if g.get('categories')}
        allowed={(g['languageCode'],g['surfaceKey'],c['id']) for g in groups.values() for c in g['categories']}
        scored={(s['languageCode'],s['surfaceKey'],s['categoryId']):s['score'] for s in values}
        if len(scored)!=len(values) or set(scored)!=allowed:
            raise ValueError('category score inventory differs')
        for g in groups.values():
            mapped=associated_scores(g,{c['id']:scored[g['languageCode'],g['surfaceKey'],c['id']] for c in g['categories']})
            for variant,score in mapped.items():
                if evidence[result['requestId']][g['languageCode'],g['surfaceKey'],variant]!=score:
                    raise ValueError('category-to-variant scores differ')
    return evidence


def nli_pairs(context,group,tokenizer):
    premise=context+('' if not context or context[-1].isspace() else ' ')+group['surfaceKey']
    premise_ids=tokenizer.encode(premise,add_special_tokens=False)
    texts={('source_categories',c['id']):hypothesis(group['surfaceKey'],c['id']) for c in group['categories']}
    texts.update({('no_attributes',v):f'W tym kontekście poprawną pisownią dopisywanego słowa jest „{v}”.' for v in group['variants']})
    encoded={k:tokenizer.encode(t,add_special_tokens=False) for k,t in texts.items()}
    if any(tokenizer.unk_token_id in ids for ids in [premise_ids]+list(encoded.values())):
        raise ValueError('unknown token')
    budget=512-tokenizer.num_special_tokens_to_add(pair=True)-max(map(len,encoded.values()))
    if budget<1:raise ValueError('invalid token budget')
    suffix=premise_ids[-budget:]
    pairs={k:tokenizer.build_inputs_with_special_tokens(suffix,ids) for k,ids in encoded.items()}
    if any(len(ids)>512 for ids in pairs.values()):raise ValueError('pair exceeds budget')
    return pairs,{'tokenTruncated':len(suffix)!=len(premise_ids),'premiseTokens':len(suffix),'premiseTokenSha256':digest(suffix)}


def infer_nli(request,out):
    check_request(request)
    model,tokenizer,torch,info=preflight()
    cache={};results={c:[] for c in CONDITIONS};trace=[];began=time.perf_counter()
    for index,row in enumerate(request['requests']):
        variant_rows={c:[] for c in CONDITIONS};category_rows=[]
        for group in row['candidates']:
            if not group.get('categories'):continue
            pairs,detail=nli_pairs(row['context']['text'],group,tokenizer)
            missing=list(dict.fromkeys(tuple(ids) for ids in pairs.values() if tuple(ids) not in cache))
            for start in range(0,len(missing),8):
                batch=missing[start:start+8]
                inputs=torch.full((len(batch),max(map(len,batch))),tokenizer.pad_token_id,dtype=torch.long)
                attention=torch.zeros_like(inputs)
                for i,ids in enumerate(batch):
                    inputs[i,:len(ids)]=torch.tensor(ids);attention[i,:len(ids)]=1
                with torch.inference_mode():
                    scores=torch.log_softmax(model(input_ids=inputs,attention_mask=attention).logits,dim=-1)[:,0]
                if not torch.isfinite(scores).all():raise ValueError('nonfinite score')
                cache.update({ids:scores[i].item() for i,ids in enumerate(batch)})
            values={c['id']:cache[tuple(pairs['source_categories',c['id']])] for c in group['categories']}
            category_rows.extend({'languageCode':group['languageCode'],'surfaceKey':group['surfaceKey'],
                                  'categoryId':cid,'score':v} for cid,v in values.items())
            allvalues={'source_categories':associated_scores(group,values),
                       'no_attributes':{v:cache[tuple(pairs['no_attributes',v])] for v in group['variants']}}
            for condition,variant_values in allvalues.items():
                variant_rows[condition].extend({'languageCode':group['languageCode'],'surfaceKey':group['surfaceKey'],
                                               'surface':v,'score':score} for v,score in variant_values.items())
            trace.append({'requestId':row['requestId'],'surfaceKey':group['surfaceKey'],**detail})
        for c in CONDITIONS:
            results[c].append({'requestId':row['requestId'],'variantScores':variant_rows[c],
                               'categoryScores':category_rows if c=='source_categories' else []})
        if index%32==0:print(f'NLI {index+1}/{len(request["requests"])}',flush=True)
    out.mkdir(parents=True,exist_ok=True)
    for c in CONDITIONS:
        prediction={'schemaVersion':1,'requestSha256':request['requestSha256'],
                    'source':{'kind':'model','name':MODEL_ID,'revision':MODEL_REVISION+'/'+VERSION+'/'+c},
                    'condition':c,'results':results[c]}
        validate_category_predictions(prediction,request)
        (out/f'nli-{c}.json').write_bytes(canonical_bytes(prediction))
    metadata={'modelId':MODEL_ID,'modelRevision':MODEL_REVISION,'loadingInfo':info,
              'requestSha256':request['requestSha256'],'runnerSha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'sharedLoaderSha256':hashlib.sha256((ROOT/'sense_experiment.py').read_bytes()).hexdigest(),
              'parameters':sum(p.numel() for p in model.parameters()),'device':'cpu','dtype':'float32',
              'threads':2,'batchSize':8,'uniquePairs':len(cache),'inferenceSeconds':time.perf_counter()-began,
              'timingIsPhoneBenchmark':False,'trace':trace}
    (out/'nli-metadata.json').write_bytes(canonical_bytes(metadata))


def evaluate(cases,request,prediction=None):
    evidence=validate_category_predictions(prediction,request) if prediction else {}
    semantic={r['requestId']:r.get('categoryScores',[]) for r in prediction['results']} if prediction else {}
    by_id={c['id']:c for c in cases['cases']};rows=[]
    for row in request['requests']:
        cid,window=row['requestId'].rsplit('/',1);case=by_id[cid]
        suggestions=resolve(row['candidates'],evidence.get(row['requestId']),row['caseMode'])
        expected=case.get('expected');rank=None;picked=None;category_correct=None
        if expected:
            identity=(expected['languageCode'],expected['surfaceKey'],expected['surface'])
            rank=next((i+1 for i,s in enumerate(suggestions) if (s['languageCode'],s['surfaceKey'],s['surface'])==identity),None)
            values=[s for s in semantic.get(row['requestId'],[]) if (s['languageCode'],s['surfaceKey'])==identity[:2]]
            if values:
                group=next(g for g in row['candidates'] if (g['languageCode'],g['surfaceKey'])==identity[:2])
                value_map={s['categoryId']:s['score'] for s in values}
                if len(value_map)!=len(values):raise ValueError('duplicate category scores')
                mapped=associated_scores(group,value_map)
                if any(evidence[row['requestId']][(*identity[:2],v)]!=score for v,score in mapped.items()):
                    raise ValueError('category-to-variant scores differ')
                picked=max(values,key=lambda s:s['score'])['categoryId']
                if case.get('expectedCategoryIds'):category_correct=picked in case['expectedCategoryIds']
        # Cross-key order and engine scores are invariants of the existing resolver.
        ordered=list(dict.fromkeys(s['surfaceKey'] for s in suggestions))
        if ordered!=[g['surfaceKey'] for g in row['candidates']]:raise ValueError('lexical order changed')
        for s in suggestions:
            g=next(g for g in row['candidates'] if g['surfaceKey']==s['surfaceKey'])
            if s['engineScore']!=g['engineScore']:raise ValueError('engine score changed')
        rows.append({'caseId':cid,'window':window,'category':case['diagnostic']['category'],
                     'surfaceKey':expected['surfaceKey'] if expected else row['candidates'][0]['surfaceKey'],
                     'expected':expected['surface'] if expected else None,'expectedRank':rank,
                     'top1':rank==1 if expected else None,'top3':rank is not None and rank<=3 if expected else None,
                     'reachable':rank is not None if expected else None,'chosenCategoryId':picked,
                     'categoryCorrect':category_correct,'suggestions':suggestions})
    def metrics(items):
        labelled=[r for r in items if r['expected'] is not None];semantic=[r for r in items if r['categoryCorrect'] is not None]
        return {'cases':len(items),'labelled':len(labelled),
                **{k:sum(r[k] for r in labelled) if labelled else None for k in ('top1','top3','reachable')},
                'categoryCases':len(semantic),'categoryTop1':sum(r['categoryCorrect'] for r in semantic) if semantic else None}
    result={}
    for window in ['two_words','long']:
        subset=[r for r in rows if r['window']==window]
        result[window]={'main':metrics([r for r in subset if r['category'] in MAIN]),
                        'byCategory':{c:metrics([r for r in subset if r['category']==c]) for c in sorted({r['category'] for r in subset})},
                        'byKey':{k:metrics([r for r in subset if r['surfaceKey']==k and r['category'] in MAIN]) for k in sorted({r['surfaceKey'] for r in subset if r['category'] in MAIN})}}
    return {'requestSha256':request['requestSha256'],'primaryMetric':'top3','metrics':result,'rows':rows,
            'source':prediction['source'] if prediction else {'kind':'neutral_baseline'}}


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('command',choices=['prepare','nli','polbert','herbert','evaluate'])
    ap.add_argument('--output-dir',type=Path,default=ROOT/'source-category-results-2026-10-02')
    args=ap.parse_args()
    if args.command=='prepare':
        sidecar=generate_sidecar();cases=build_cases(sidecar);request=prepare_requests(cases,sidecar)
        for name,data in [('source-category-sidecar.json',sidecar),('source-category-cases.json',cases),('source-category-requests.json',request)]:
            (ROOT/name).write_bytes(canonical_bytes(data))
        print(json.dumps({'cases':len(cases['cases']),'requests':len(request['requests']),'requestSha256':request['requestSha256']}));return
    request=json.loads((ROOT/'source-category-requests.json').read_text())
    if args.command=='nli':infer_nli(request,args.output_dir)
    elif args.command in ['polbert','herbert']:
        shared_run_mlm(request,args.command,args.output_dir)
    else:
        cases=json.loads((ROOT/'source-category-cases.json').read_text())
        systems={'neutral':evaluate(cases,request)}
        for name in ['nli-source_categories','nli-no_attributes','polbert-wwm','herbert-wwm']:
            systems[name]=evaluate(cases,request,json.loads((args.output_dir/(name+'.json')).read_text()))
        for name,data in systems.items():(args.output_dir/f'decisions-{name}.json').write_bytes(canonical_bytes(data))
        summary={'requestSha256':request['requestSha256'],'primaryMetric':'top3',
                 'systems':{name:data['metrics'] for name,data in systems.items()}}
        (args.output_dir/'summary.json').write_bytes(canonical_bytes(summary))
        print(json.dumps({n:s['long']['main'] for n,s in summary['systems'].items()},ensure_ascii=False,indent=2))


if __name__=='__main__':main()
