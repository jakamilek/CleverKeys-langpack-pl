"""Real frozen inference. Model weights are downloaded, hashed, never uploaded."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import resource
import time
from pathlib import Path
from contract import ROOT,MODELS,canonical,digest,prepare,evaluate,validate_scores

def metadata_text(row):
    out=[];seen=set()
    for c in row['candidates']:
        if c['key'] not in seen and c['sourceText']:
            seen.add(c['key']);out.append(c['sourceText'])
    return '\n'.join(out)

def mlm_inputs(row,context,c,tokenizer):
    prefix=('Dane słownika:\n'+c['sourceText']+'\nTekst: ') if c['sourceText'] else ''
    left=tokenizer.encode(prefix+context,add_special_tokens=False)
    target=tokenizer.encode(c['surface'],add_special_tokens=False)
    if not target or tokenizer.unk_token_id in target:raise ValueError('unsupported MLM target')
    positions=list(range(len(left)+1,len(left)+1+len(target)))
    ids=[tokenizer.cls_token_id]+left+[tokenizer.mask_token_id]*len(target)+[tokenizer.sep_token_id]
    return ids,target,positions

def nli_inputs(row,context,c):
    if row['suite']=='punctuation_before_word':
        premise='Tekst przed kursorem: '+context+'. Kolejne dopisywane słowo: '+row['nextWord']+'.'
        action='wstawić przecinek' if c['punctuation'] else 'nie wstawiać znaku interpunkcyjnego'
        hypothesis='Przed dopisywanym słowem należy '+action+'.'
    else:
        premise='Tekst przed kursorem: '+context+'\nDopisywane słowo: '+c['key']
        if c['sourceText']:premise+='\nDane słownika:\n'+c['sourceText']
        hypothesis='W tym kontekście poprawną pisownią dopisywanego słowa jest „'+c['surface']+'”.'
    return premise,hypothesis

def choice_ids(row,context,candidates,tokenizer):
    if len(candidates)>26:raise ValueError('too many choices')
    if row['suite']=='punctuation_before_word':
        task='Wybierz znak przed kolejnym słowem. Kolejne słowo: '+row['nextWord']+'.'
        options=[chr(65+i)+': '+('przecinek' if c['punctuation'] else 'bez znaku')
                 for i,c in enumerate(candidates)]
    else:
        task='Wybierz słowo i jego pisownię, które najlepiej pasują do tekstu przed kursorem.'
        options=[chr(65+i)+': '+c['surface'] for i,c in enumerate(candidates)]
    user=task+'\nTekst przed kursorem:\n'+context+'\nMożliwości:\n'+'\n'.join(options)
    meta=metadata_text(row)
    if meta:user+='\nDane słownika (wszystkie dopuszczalne odczytania):\n'+meta
    messages=[{'role':'system','content':'Oceń polski tekst. Wybierz wyłącznie spośród podanych możliwości. Odpowiedz jedną literą oznaczającą wybraną możliwość.'},
              {'role':'user','content':user}]
    ids=tokenizer.apply_chat_template(messages,tokenize=True,add_generation_prompt=True,enable_thinking=False)
    labels=[tokenizer.encode(chr(65+i),add_special_tokens=False) for i in range(len(candidates))]
    if any(len(x)!=1 for x in labels):raise ValueError('choice labels must each be one token')
    return ids,[x[0] for x in labels]

def fit_context(row,metadata_row,tokenizer,kind):
    # Same retained context for the metadata/plain pair; drop only oldest context words.
    # Source metadata is never cropped. Long/short are already chosen in requests.
    context=row['context'];limit=1536 if kind=='causal-choice' else 512
    removed=0
    while True:
        lengths=[]
        for probe in [row,metadata_row]:
            if kind=='mlm':
                lengths.extend(len(mlm_inputs(probe,context,c,tokenizer)[0]) for c in probe['candidates'])
            elif kind=='nli':
                lengths.extend(len(tokenizer(*nli_inputs(probe,context,c))['input_ids']) for c in probe['candidates'])
            else:
                for choices in [probe['candidates'],list(reversed(probe['candidates']))]:
                    lengths.append(len(choice_ids(probe,context,choices,tokenizer)[0]))
        if max(lengths)<=limit:return context,removed,max(lengths),limit
        words=context.split(maxsplit=1)
        if len(words)<2:raise ValueError('source/options alone exceed model budget: '+row['id'])
        removed+=len(context)-len(words[1]);context=words[1]

def score_mlm(row,context,model,tokenizer,torch):
    scores={};trace=[]
    for c in row['candidates']:
        ids,target,positions=mlm_inputs(row,context,c,tokenizer)
        x=torch.tensor([ids],dtype=torch.long)
        with torch.inference_mode():
            hidden=model.bert(input_ids=x,attention_mask=torch.ones_like(x)).last_hidden_state
            logits=model.cls.predictions(hidden[0,positions,:])
            lp=torch.log_softmax(logits,dim=-1)
            total=sum(lp[i,t].item() for i,t in enumerate(target))
        # Frozen mean normalization prevents a pure sum-length preference.
        scores[c['surface']]=total/len(target)
        trace.append({'surface':c['surface'],'targetTokenIds':target,'inputTokens':len(ids),
                      'sumLogProbability':total,'meanLogProbability':scores[c['surface']]})
    return scores,trace

def score_nli(row,context,model,tokenizer,torch):
    pairs=[nli_inputs(row,context,c) for c in row['candidates']]
    batch=tokenizer([p[0] for p in pairs],[p[1] for p in pairs],padding=True,return_tensors='pt',truncation=False)
    with torch.inference_mode():
        logits=model(**batch).logits
        lp=torch.log_softmax(logits,dim=-1)[:,0].tolist()
    return {c['surface']:lp[i] for i,c in enumerate(row['candidates'])},[
        {'surface':c['surface'],'inputTokens':int(batch['attention_mask'][i].sum()),'entailmentLogProbability':lp[i]}
        for i,c in enumerate(row['candidates'])]

def score_choice(row,context,model,tokenizer,torch):
    scores={c['surface']:0. for c in row['candidates']};trace=[]
    for direction,choices in [('forward',row['candidates']),('reverse',list(reversed(row['candidates'])) )]:
        ids,labels=choice_ids(row,context,choices,tokenizer)
        x=torch.tensor([ids],dtype=torch.long)
        with torch.inference_mode():
            hidden=model.model(input_ids=x,attention_mask=torch.ones_like(x),use_cache=False).last_hidden_state
            logits=model.lm_head(hidden[:,-1,:]).float()
            lp=torch.log_softmax(logits,dim=-1)[0]
            values=[lp[t].item() for t in labels]
        for i,c in enumerate(choices):scores[c['surface']]+=values[i]/2
        trace.append({'direction':direction,'inputTokens':len(ids),
                      'choiceOrder':[c['surface'] for c in choices],'labelTokenIds':labels,
                      'labelLogProbabilities':values})
    return scores,trace

def load(name):
    import torch
    from transformers import AutoTokenizer,AutoModelForMaskedLM,AutoModelForSequenceClassification,AutoModelForCausalLM
    preset=MODELS[name];torch.set_num_threads(2)
    began=time.perf_counter()
    tokenizer=AutoTokenizer.from_pretrained(preset['id'],revision=preset['revision'],trust_remote_code=False,use_fast=True)
    factory={'mlm':AutoModelForMaskedLM,'nli':AutoModelForSequenceClassification,'causal-choice':AutoModelForCausalLM}[preset['kind']]
    model,info=factory.from_pretrained(preset['id'],revision=preset['revision'],trust_remote_code=False,
                                      use_safetensors=name!='herbert',torch_dtype=torch.float32,
                                      output_loading_info=True)
    for field in ['missing_keys','mismatched_keys','error_msgs']:
        if info.get(field):raise ValueError('incomplete pretrained model: '+str(info))
    allowed={'bert.pooler.dense.bias','bert.pooler.dense.weight','cls.sso.sso_relationship.bias','cls.sso.sso_relationship.weight'} if name=='herbert' else set()
    if set(info.get('unexpected_keys',[]))!=allowed:raise ValueError('unexplained weights: '+str(info))
    if model.config._commit_hash!=preset['revision']:raise ValueError('wrong model revision')
    if name=='minilm' and model.config.id2label[0].lower()!='entailment':raise ValueError('unknown NLI class mapping')
    model.eval();load_seconds=time.perf_counter()-began
    # Verify selected-position projection against the complete original pretrained forward.
    if name in {'herbert','qwen'}:
        example=tokenizer('To jest test',return_tensors='pt')
        with torch.inference_mode():
            original=model(**example).logits[:,-1,:]
            base=model.bert if name=='herbert' else model.model
            hidden=base(**example).last_hidden_state[:,-1,:]
            optimized=model.cls.predictions(hidden) if name=='herbert' else model.lm_head(hidden)
            err=(original-optimized).abs().max().item()
            if not torch.allclose(original,optimized,atol=1e-4,rtol=1e-5):raise ValueError('projection parity failure')
        info['projectionMaxAbsError']=err
    return model,tokenizer,torch,info,load_seconds

def files_manifest(preset):
    from huggingface_hub import snapshot_download
    root=Path(snapshot_download(preset['id'],revision=preset['revision'],local_files_only=True))
    rows=[]
    for p in sorted(root.rglob('*')):
        if p.is_file():
            h=hashlib.sha256()
            with p.open('rb') as f:
                for chunk in iter(lambda:f.read(1024*1024),b''):h.update(chunk)
            rows.append({'path':str(p.relative_to(root)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
    if not any(p['path'].endswith(('.bin','.safetensors')) for p in rows):raise ValueError('no weight files in manifest')
    return rows

def run(name,out):
    out.mkdir(parents=True,exist_ok=True)
    source,entries,cases,request=prepare()
    frozen=json.loads((ROOT/'freeze-manifest.json').read_text())
    for p,h in frozen['files'].items():
        if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h:raise ValueError('freeze file mismatch: '+p)
    workflow=ROOT.parents[1]/'.github/workflows/ai-compare-v5.yml'
    if hashlib.sha256(workflow.read_bytes()).hexdigest()!=frozen['workflowSha256']:
        raise ValueError('workflow freeze mismatch')
    if frozen['requestPayloadSha256']!=digest(request):raise ValueError('request freeze mismatch')
    (out/'requests.json').write_bytes(canonical(request)+b'\n')
    model,tokenizer,torch,info,load_seconds=load(name)
    preset=MODELS[name];by_id={r['id']:r for r in request['requests']}
    prepared=[]
    # All tokenization/budgets validated before scoring the first request.
    for row in request['requests']:
        other=by_id.get(row['id'].replace('/plain','/metadata'),row)
        prepared.append((row,*fit_context(row,other,tokenizer,preset['kind'])))
    predictions=[]
    began=time.perf_counter()
    scorer={'mlm':score_mlm,'nli':score_nli,'causal-choice':score_choice}[preset['kind']]
    for n,(row,context,removed,max_tokens,limit) in enumerate(prepared):
        t=time.perf_counter()
        scores,trace=scorer(row,context,model,tokenizer,torch)
        elapsed=(time.perf_counter()-t)*1000
        predictions.append({'id':row['id'],'scores':scores,'inferenceMs':elapsed,
                            'contextCharactersRemoved':removed,'maxInputTokens':max_tokens,
                            'tokenLimit':limit,'trace':trace})
        if (n+1)%20==0:print(name,n+1,'/',len(prepared),flush=True)
    result={'protocol':request['protocol'],'model':preset,'requestsSha256':digest(request),
            'codeCommit':os.environ.get('GITHUB_SHA'),
            'freezeManifestSha256':hashlib.sha256((ROOT/'freeze-manifest.json').read_bytes()).hexdigest(),
            'sourceSnapshotSha256':hashlib.sha256((ROOT/'source-snapshot.json').read_bytes()).hexdigest(),
            'predictions':predictions,'loadSecondsIncludingDownload':load_seconds,
            'inferenceSeconds':time.perf_counter()-began,
            'peakHostRssMiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024,
            'loadingInfo':info,'parameters':sum(p.numel() for p in model.parameters()),
            'modelFiles':files_manifest(preset),'weightsPublished':False,
            'environment':{'python':platform.python_version(),'platform':platform.platform(),
                           'torch':torch.__version__,'transformers':importlib.metadata.version('transformers'),
                           'threads':torch.get_num_threads(),'dtype':'float32','device':'cpu',
                           'phoneMeasured':False},
            'method':{'herbert':'WWM mean log probability (sum also in trace)',
                      'minilm':'literal spelling NLI entailment with optional source fields in premise',
                      'qwen':'non-thinking constrained single-token choices, averaged forward/reverse order'}[name]}
    validate_scores(request,result)
    report=evaluate(cases,entries,request,result)
    (out/'predictions.json').write_bytes(canonical(result)+b'\n')
    (out/'report.json').write_bytes(canonical(report)+b'\n')
    print(json.dumps({'model':name,'requests':len(predictions),'groups':report['groups']},ensure_ascii=False),flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--model',choices=MODELS,required=True)
    p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.model,a.out)
