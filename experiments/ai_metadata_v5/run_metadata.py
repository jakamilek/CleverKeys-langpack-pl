"""Frozen original model/scorers; only the input representation changes."""
import argparse
import copy
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import time
from pathlib import Path
from contract_meta import ROOT,BASE,MODELS,prepare,canonical,digest,verify_freeze,evaluate,validate_result
import run_model as engine

ORIGINAL_MLM=engine.mlm_inputs
ORIGINAL_NLI=engine.nli_inputs
ORIGINAL_CHOICE=engine.choice_ids

def guided_candidate(row,c):
    out=copy.deepcopy(c)
    if row['instruction']:out['sourceText']=row['instruction']+'\n'+out['sourceText']
    return out

def mlm_inputs(row,context,c,tokenizer):
    return ORIGINAL_MLM(row,context,guided_candidate(row,c),tokenizer)

def nli_inputs(row,context,c):
    return ORIGINAL_NLI(row,context,guided_candidate(row,c))

def choice_ids(row,context,candidates,tokenizer):
    if not row['instruction']:return ORIGINAL_CHOICE(row,context,candidates,tokenizer)
    # All conditions share the original system task; only this instruction changes.
    class GuidedTokenizer:
        def encode(self,*args,**kwargs):return tokenizer.encode(*args,**kwargs)
        def apply_chat_template(self,messages,**kwargs):
            messages=copy.deepcopy(messages)
            messages[1]['content']=row['instruction']+'\n'+messages[1]['content']
            return tokenizer.apply_chat_template(messages,**kwargs)
    return ORIGINAL_CHOICE(row,context,candidates,GuidedTokenizer())

def input_lengths(row,context,tokenizer,kind):
    if kind=='mlm':return [len(mlm_inputs(row,context,c,tokenizer)[0]) for c in row['candidates']]
    if kind=='nli':return [len(tokenizer(*nli_inputs(row,context,c))['input_ids']) for c in row['candidates']]
    return [len(choice_ids(row,context,cs,tokenizer)[0])
            for cs in [row['candidates'],list(reversed(row['candidates']))]]

def fit_context(rows,tokenizer,kind):
    # Fit every condition together, preventing instruction/metadata budget confounds.
    if len({r['context'] for r in rows})!=1:raise ValueError('unpaired context')
    context=rows[0]['context'];removed=0;limit=1536 if kind=='causal-choice' else 512
    while True:
        lengths=[n for row in rows for n in input_lengths(row,context,tokenizer,kind)]
        if max(lengths)<=limit:return context,removed,max(lengths),limit
        words=context.split(maxsplit=1)
        if len(words)<2:raise ValueError('source/instruction/options exceed budget: '+rows[0]['id'])
        removed+=len(context)-len(words[1]);context=words[1]

def run(name,out):
    verify_freeze();out.mkdir(parents=True,exist_ok=True)
    source,entries,cases,request=prepare()
    (out/'requests.json').write_bytes(canonical(request)+b'\n')
    model,tokenizer,torch,info,load_seconds=engine.load(name)
    engine.mlm_inputs=mlm_inputs;engine.nli_inputs=nli_inputs;engine.choice_ids=choice_ids
    preset=MODELS[name];pairs={}
    for row in request['requests']:pairs.setdefault((row['caseId'],row['window']),[]).append(row)
    fitted={key:fit_context(rows,tokenizer,preset['kind']) for key,rows in pairs.items()}
    # Validate all budgets before any request is scored; never omit a failed case.
    scorer={'mlm':engine.score_mlm,'nli':engine.score_nli,'causal-choice':engine.score_choice}[preset['kind']]
    predictions=[];began=time.perf_counter()
    for n,row in enumerate(request['requests']):
        context,removed,max_tokens,limit=fitted[(row['caseId'],row['window'])]
        t=time.perf_counter();scores,trace=scorer(row,context,model,tokenizer,torch)
        predictions.append({'id':row['id'],'scores':scores,'inferenceMs':(time.perf_counter()-t)*1000,
                            'contextCharactersRemoved':removed,'maxInputTokens':max_tokens,
                            'tokenLimit':limit,'trace':trace})
        if (n+1)%20==0:print(name,n+1,'/',len(request['requests']),flush=True)
    result={'protocol':request['protocol'],'model':preset,'requestsSha256':digest(request),
            'codeCommit':os.environ.get('GITHUB_SHA'),
            'freezeManifestSha256':hashlib.sha256((ROOT/'freeze-manifest.json').read_bytes()).hexdigest(),
            'sourceSnapshotSha256':hashlib.sha256((BASE/'source-snapshot.json').read_bytes()).hexdigest(),
            'predictions':predictions,'loadingInfo':info,'parameters':sum(p.numel() for p in model.parameters()),
            'modelFiles':engine.files_manifest(preset),'weightsPublished':False,
            'loadSecondsIncludingDownload':load_seconds,'inferenceSeconds':time.perf_counter()-began,
            'peakHostRssMiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
            'environment':{'python':platform.python_version(),'platform':platform.platform(),
                           'torch':torch.__version__,'transformers':importlib.metadata.version('transformers'),
                           'threads':torch.get_num_threads(),'dtype':'float32','device':'cpu','phoneMeasured':False},
            'method':{'scoringUnchanged':True,'conditions':['plain','raw','explained','guided','plain_guided'],
                      'guidedIsTextNotTraining':True}}
    validate_result(request,result);report=evaluate(cases,entries,request,result)
    (out/'predictions.json').write_bytes(canonical(result)+b'\n')
    (out/'report.json').write_bytes(canonical(report)+b'\n')
    print(json.dumps({'model':name,'requests':len(predictions),'groups':report['groups']},ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',choices=MODELS,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.model,a.out)
