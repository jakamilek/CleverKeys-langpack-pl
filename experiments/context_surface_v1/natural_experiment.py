#!/usr/bin/env python3
"""Frozen new-context comparison: NLI meanings and pretrained MLM spelling."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import time
from pathlib import Path

from diagnostic_runner import PRESETS, load_model, score_tasks
from mlm_adapter import shared_context_suffix
from natural_cases import VERSION, build
from plt5_adapter import check_request
from prototype import canonical_bytes, digest, load_sidecar, prepare, resolve, validate_predictions
from sense_experiment import MODEL_ID, MODEL_REVISION, hypotheses as old_hypotheses, preflight

ROOT = Path(__file__).parent
MAIN = {"natural_direct", "natural_history", "natural_switch", "natural_negation"}
CONDITIONS = ("global_attributes", "current_attributes", "no_attributes")
KINDS = {"common_noun", "proper_name", "adjective"}


def validate_sidecar(sidecar):
    _, entries = load_sidecar(sidecar)
    if sidecar.get("experimentExtension") != VERSION:
        raise ValueError("wrong experimental extension")
    for entry in entries.values():
        ids = set()
        for sense in entry.get("senses", []):
            sid = sense.get("id")
            if not isinstance(sid, str) or not sid.strip() or sid in ids:
                raise ValueError("invalid sense id")
            if sense.get("kind") not in KINDS or not isinstance(sense.get("descriptionPl"), str) or not sense['descriptionPl'].strip():
                raise ValueError("invalid sense descriptor/kind")
            ids.add(sid)
        if not ids:
            raise ValueError("missing sense inventory")
        used = set()
        for variant in entry['capitalization']['variants']:
            refs = variant.get('senseIds')
            if not isinstance(refs, list) or not refs or any(not isinstance(s, str) for s in refs):
                raise ValueError("missing association")
            if len(set(refs)) != len(refs) or not set(refs) <= ids:
                raise ValueError("duplicate/dangling association")
            used.update(refs)
        if used != ids:
            raise ValueError("orphan sense")
    return entries


def prepare_requests(cases, sidecar):
    entries = validate_sidecar(sidecar)
    request = prepare(cases, sidecar)
    for row in request['requests']:
        for group in row['candidates']:
            entry = entries.get(group['surfaceKey']) if group['languageCode'] == sidecar['languageCode'] else None
            if entry:
                group['senses'] = copy.deepcopy(entry['senses'])
                group['variantSenseIds'] = {v['surface']: list(v['senseIds'])
                                           for v in entry['capitalization']['variants']}
    request['experimentExtension'] = VERSION
    del request['requestSha256']
    request['requestSha256'] = digest(request)
    return request


def sense_hypothesis(key, description, condition):
    if condition == 'global_attributes':
        return f'W tym kontekście słowo „{key}” oznacza {description}.'
    if condition == 'current_attributes':
        return f'Ostatnie dopisywane słowo „{key}” w aktualnym zdaniu oznacza {description}.'
    raise ValueError('condition has no sense hypothesis')


def nli_pairs(context, group, tokenizer):
    premise = context + ('' if not context or context[-1].isspace() else ' ') + group['surfaceKey']
    premise_ids = tokenizer.encode(premise, add_special_tokens=False)
    encoded = {}
    for condition in CONDITIONS[:2]:
        for sense in group['senses']:
            encoded[condition, sense['id']] = tokenizer.encode(
                sense_hypothesis(group['surfaceKey'], sense['descriptionPl'], condition), add_special_tokens=False)
    for surface, texts in old_hypotheses(group, 'no_attributes').items():
        encoded['no_attributes', surface] = tokenizer.encode(texts[0], add_special_tokens=False)
    if any(tokenizer.unk_token_id in ids for ids in [premise_ids] + list(encoded.values())):
        raise ValueError('unknown token in NLI pair')
    budget = 512 - tokenizer.num_special_tokens_to_add(pair=True) - max(map(len, encoded.values()))
    if budget < 1:
        raise ValueError('hypothesis exceeds budget')
    suffix = premise_ids[-budget:]
    pairs = {identity: tokenizer.build_inputs_with_special_tokens(suffix, hypothesis)
             for identity, hypothesis in encoded.items()}
    if any(len(ids) > 512 for ids in pairs.values()):
        raise ValueError('NLI pair budget failure')
    return pairs, {'premiseTokens': len(suffix), 'tokenTruncated': len(suffix) != len(premise_ids),
                   'premiseTokenSha256': digest(suffix)}


def associated_scores(group, sense_scores):
    ids = {s['id'] for s in group['senses']}
    if sense_scores.keys() != ids:
        raise ValueError('sense inventory differs from scores')
    return {surface: max(sense_scores[sid] for sid in group['variantSenseIds'][surface])
            for surface in group['variants']}


def run_nli(request, output_dir):
    check_request(request)
    model, tokenizer, torch, info = preflight()
    cache, trace = {}, []
    results = {c: [] for c in CONDITIONS}
    began = time.perf_counter()
    for index, row in enumerate(request['requests']):
        variant_rows = {c: [] for c in CONDITIONS}
        sense_rows = {c: [] for c in CONDITIONS}
        for group in row['candidates']:
            if not group.get('senses'):
                continue
            pairs, detail = nli_pairs(row['context']['text'], group, tokenizer)
            missing = list(dict.fromkeys(tuple(ids) for ids in pairs.values() if tuple(ids) not in cache))
            for start in range(0, len(missing), 8):
                batch = missing[start:start+8]
                inputs = torch.full((len(batch), max(map(len, batch))), tokenizer.pad_token_id, dtype=torch.long)
                attention = torch.zeros_like(inputs)
                for i, ids in enumerate(batch):
                    inputs[i, :len(ids)] = torch.tensor(ids)
                    attention[i, :len(ids)] = 1
                with torch.inference_mode():
                    scores = torch.log_softmax(model(input_ids=inputs, attention_mask=attention).logits, dim=-1)[:, 0]
                if not torch.isfinite(scores).all():
                    raise ValueError('nonfinite score')
                cache.update({ids: scores[i].item() for i, ids in enumerate(batch)})
            for condition in CONDITIONS:
                if condition == 'no_attributes':
                    values = {surface: cache[tuple(pairs[condition, surface])] for surface in group['variants']}
                else:
                    semantic = {sense['id']: cache[tuple(pairs[condition, sense['id']])] for sense in group['senses']}
                    values = associated_scores(group, semantic)
                    sense_rows[condition].extend({'languageCode': group['languageCode'], 'surfaceKey': group['surfaceKey'],
                                                   'senseId': sid, 'score': value} for sid, value in semantic.items())
                variant_rows[condition].extend({'languageCode': group['languageCode'], 'surfaceKey': group['surfaceKey'],
                                                'surface': surface, 'score': value} for surface, value in values.items())
            trace.append({'requestId': row['requestId'], 'surfaceKey': group['surfaceKey'], **detail})
        for condition in CONDITIONS:
            results[condition].append({'requestId': row['requestId'], 'variantScores': variant_rows[condition],
                                       'senseScores': sense_rows[condition]})
        if index % 32 == 0:
            print(f'NLI {index+1}/{len(request["requests"])}', flush=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    for condition in CONDITIONS:
        prediction = {'schemaVersion': 1, 'requestSha256': request['requestSha256'],
                      'source': {'kind': 'model', 'name': MODEL_ID,
                                 'revision': MODEL_REVISION+'/'+VERSION+'/'+condition},
                      'condition': condition, 'results': results[condition]}
        validate_predictions(prediction, request)
        (output_dir/f'nli-{condition}.json').write_bytes(canonical_bytes(prediction))
    metadata = {'modelId': MODEL_ID, 'modelRevision': MODEL_REVISION, 'loadingInfo': info,
                'requestSha256': request['requestSha256'], 'runnerSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'sharedNliLoaderSha256': hashlib.sha256((ROOT/'sense_experiment.py').read_bytes()).hexdigest(),
                'parameters': sum(p.numel() for p in model.parameters()), 'device': 'cpu', 'dtype': 'float32',
                'threads': 2, 'batchSize': 8, 'uniquePairs': len(cache), 'inferenceSeconds': time.perf_counter()-began,
                'timingIsPhoneBenchmark': False, 'trace': trace}
    (output_dir/'nli-metadata.json').write_bytes(canonical_bytes(metadata))


def run_mlm(request, model_name, output_dir):
    check_request(request)
    preset = PRESETS[model_name]
    model, tokenizer, torch, info = load_model(preset)
    cache, results, trace = {}, [], []
    began = time.perf_counter()
    for index, row in enumerate(request['requests']):
        context_ids = tokenizer.encode(row['context']['text'], add_special_tokens=False)
        if any(t in tokenizer.all_special_ids for t in context_ids):
            raise ValueError('special/unknown context token')
        tasks, task_identities = [], []
        for group in row['candidates']:
            if len(group['variants']) < 2:
                continue
            targets = [tokenizer.encode(v, add_special_tokens=False) for v in group['variants']]
            if len({tuple(ids) for ids in targets}) != len(targets) or any(t in tokenizer.all_special_ids for ids in targets for t in ids):
                raise ValueError('collapsed or unknown variant token')
            suffix, truncated = shared_context_suffix(context_ids, list(map(len, targets)))
            for surface, ids in zip(group['variants'], targets):
                positions = list(range(len(suffix)+1, len(suffix)+1+len(ids)))
                inputs = [tokenizer.cls_token_id]+suffix+[tokenizer.mask_token_id]*len(ids)+[tokenizer.sep_token_id]
                identity = (tuple(inputs), tuple(positions), tuple(ids))
                if identity not in cache and identity not in task_identities:
                    task_identities.append(identity)
                    tasks.append((inputs, positions, ids, len(task_identities)-1))
            trace.append({'requestId': row['requestId'], 'surfaceKey': group['surfaceKey'],
                          'contextTokens': len(suffix), 'variantTokens': list(map(len, targets)), 'tokenTruncated': truncated})
        contributions = score_tasks(model, tokenizer, tasks, torch)
        for task_index, value in contributions:
            cache[task_identities[task_index]] = value
        scores = []
        for group in row['candidates']:
            if len(group['variants']) < 2:
                continue
            targets = [tokenizer.encode(v, add_special_tokens=False) for v in group['variants']]
            suffix, _ = shared_context_suffix(context_ids, list(map(len, targets)))
            for surface, ids in zip(group['variants'], targets):
                identity = (tuple([tokenizer.cls_token_id]+suffix+[tokenizer.mask_token_id]*len(ids)+[tokenizer.sep_token_id]),
                            tuple(range(len(suffix)+1, len(suffix)+1+len(ids))), tuple(ids))
                scores.append({'languageCode': group['languageCode'], 'surfaceKey': group['surfaceKey'],
                               'surface': surface, 'score': cache[identity]})
        results.append({'requestId': row['requestId'], 'variantScores': scores})
        if index % 32 == 0:
            print(f'{model_name} {index+1}/{len(request["requests"])}', flush=True)
    output_dir.mkdir(parents=True, exist_ok=True)
    prediction = {'schemaVersion': 1, 'requestSha256': request['requestSha256'],
                  'source': {'kind': 'model', 'name': preset['id'], 'revision': preset['revision']+'/'+VERSION+'/wwm'},
                  'method': 'wwm', 'results': results}
    validate_predictions(prediction, request)
    (output_dir/f'{model_name}-wwm.json').write_bytes(canonical_bytes(prediction))
    metadata = {'modelId': preset['id'], 'modelRevision': preset['revision'], 'loadingInfo': info,
                'requestSha256': request['requestSha256'], 'runnerSha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                'sharedMlmLoaderSha256': hashlib.sha256((ROOT/'diagnostic_runner.py').read_bytes()).hexdigest(),
                'parameters': sum(p.numel() for p in model.parameters()), 'device': 'cpu', 'dtype': 'float32',
                'threads': 2, 'batchSize': 8, 'uniqueTasks': len(cache), 'inferenceSeconds': time.perf_counter()-began,
                'timingIsPhoneBenchmark': False, 'trace': trace}
    (output_dir/f'{model_name}-metadata.json').write_bytes(canonical_bytes(metadata))


def evaluate(cases, request, prediction=None):
    evidence = validate_predictions(prediction, request) if prediction else {}
    semantic = {r['requestId']: r.get('senseScores', []) for r in prediction['results']} if prediction else {}
    by_id = {c['id']: c for c in cases['cases']}
    rows = []
    for row in request['requests']:
        cid, window = row['requestId'].rsplit('/', 1)
        case = by_id[cid]
        suggestions = resolve(row['candidates'], evidence.get(row['requestId']), row['caseMode'])
        expected = case.get('expected')
        rank = None
        picked_sense, sense_correct = None, None
        if expected:
            identity = (expected['languageCode'], expected['surfaceKey'], expected['surface'])
            rank = next((i+1 for i,s in enumerate(suggestions)
                         if (s['languageCode'], s['surfaceKey'], s['surface']) == identity), None)
            senses = [s for s in semantic.get(row['requestId'], [])
                      if (s['languageCode'], s['surfaceKey']) == identity[:2]]
            if senses:
                group = next(g for g in row['candidates'] if (g['languageCode'],g['surfaceKey']) == identity[:2])
                if {s['senseId'] for s in senses} != {s['id'] for s in group['senses']} or len(senses) != len(group['senses']):
                    raise ValueError('incomplete/invalid semantic scores')
                picked_sense = max(senses, key=lambda s:s['score'])['senseId']
                sense_correct = picked_sense in case['expectedSenseIds']
        rows.append({'caseId': cid, 'window': window, 'category': case['diagnostic']['category'],
                     'surfaceKey': expected['surfaceKey'] if expected else row['candidates'][0]['surfaceKey'],
                     'expected': expected['surface'] if expected else None, 'expectedRank': rank,
                     'top1': rank==1 if expected else None, 'top3': rank is not None and rank<=3 if expected else None,
                     'reachable': rank is not None if expected else None,
                     'chosenSenseId': picked_sense, 'senseCorrect': sense_correct,
                     'suggestions': [{k:s[k] for k in ('surfaceKey','surface','variantSurface','engineScore','variantScore')}
                                     for s in suggestions]})
    def metrics(items):
        labelled = [r for r in items if r['expected'] is not None]
        meanings = [r for r in items if r['senseCorrect'] is not None]
        return {'cases':len(items), 'labelled':len(labelled),
                **{k:sum(r[k] for r in labelled) if labelled else None for k in ('top1','top3','reachable')},
                'meaningCases':len(meanings),'meaningTop1':sum(r['senseCorrect'] for r in meanings) if meanings else None}
    result = {}
    for window in ('two_words','long'):
        subset = [r for r in rows if r['window']==window]
        result[window] = {'main':metrics([r for r in subset if r['category'] in MAIN]),
                          'byCategory':{c:metrics([r for r in subset if r['category']==c]) for c in sorted({r['category'] for r in subset})},
                          'byKey':{k:metrics([r for r in subset if r['surfaceKey']==k and r['category'] in MAIN])
                                   for k in sorted({r['surfaceKey'] for r in subset if r['category'] in MAIN})}}
    return {'requestSha256':request['requestSha256'], 'primaryMetric':'top3',
            'source':prediction['source'] if prediction else {'kind':'neutral_baseline'}, 'metrics':result,'rows':rows}


def evaluate_all(cases, request, output_dir):
    systems = {'neutral':evaluate(cases,request)}
    for name in ['nli-'+c for c in CONDITIONS]+['polbert-wwm','herbert-wwm']:
        prediction = json.loads((output_dir/(name+'.json')).read_text(encoding='utf-8'))
        systems[name] = evaluate(cases,request,prediction)
    summary = {'requestSha256':request['requestSha256'],'primaryMetric':'top3','fixtureKind':cases['fixtureKind'],
               'systems':{name:s['metrics'] for name,s in systems.items()}}
    for name,system in systems.items():
        (output_dir/f'decisions-{name}.json').write_bytes(canonical_bytes(system))
    (output_dir/'summary.json').write_bytes(canonical_bytes(summary))
    print(json.dumps({name:{'main':s['long']['main'],'probe':s['long']['byCategory']['top3_probe'],
                           'warszawska':s['long']['byKey']['warszawska']} for name,s in summary['systems'].items()},ensure_ascii=False,indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command',choices=('prepare','nli','polbert','herbert','evaluate'))
    parser.add_argument('--output-dir',type=Path,default=ROOT/'natural-results-2026-10-02')
    args=parser.parse_args()
    if args.command=='prepare':
        cases,sidecar=build(); request=prepare_requests(cases,sidecar)
        for name,data in [('natural-cases.json',cases),('natural-sidecar.json',sidecar),('natural-requests.json',request)]:
            (ROOT/name).write_bytes(canonical_bytes(data))
        print(json.dumps({'cases':len(cases['cases']),'requests':len(request['requests']),'requestSha256':request['requestSha256']}))
        return
    request=json.loads((ROOT/'natural-requests.json').read_text(encoding='utf-8'))
    if args.command=='nli':run_nli(request,args.output_dir)
    elif args.command in PRESETS:run_mlm(request,args.command,args.output_dir)
    else:evaluate_all(json.loads((ROOT/'natural-cases.json').read_text(encoding='utf-8')),request,args.output_dir)


if __name__=='__main__':
    main()
