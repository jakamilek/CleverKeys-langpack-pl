#!/usr/bin/env python3
"""Bridge eight source-attested forms for candidate review, never build a pack."""
import json,copy,hashlib,sys
from pathlib import Path
from build_practical_candidate_modules import read_base,BASE_SHA,DICT_SHA,CompactPool,decode_entry
from build_shared_metadata_trial import serialize
from shared_metadata_v2 import nodes
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build/selection-review';out.mkdir(exist_ok=True,parents=True)
rows=[json.loads(l) for l in (ROOT/'build/external-33/metadata-drafts.jsonl').read_text().splitlines()];selected=[r for r in rows if r['status']=='dictionary-form-link-confirmed' and r['zipf']>=1];assert len(selected)==8
members,manifest,doc,words,_,_=read_base(Path(sys.argv[1]).read_bytes(),BASE_SHA,DICT_SHA,11,3);cp=CompactPool(doc);baseline=serialize(doc);full=[];packed=[]
for r in selected:
 e=copy.deepcopy(r['metadataDraft']);lex=[];links=[]
 for i,f in enumerate(e['metadata']['externalLexicalEvidence']):
  grammar=f.get('sourceGrammar',{}).get('partOfSpeech') or f.get('sourceGrammarText','').split()[0]
  assert grammar in {'rzeczownik','czasownik'} and f['lemma']
  lex.append(dict(lemma=f['lemma'],partOfSpeech=grammar,surfaces=[r['surfaceKey']]))
  links.append(dict(lexicalReadingIndex=i,externalEvidenceIndex=i))
 e['metadata']['sourceEvidence']={'lexicalReadings':lex};e['metadata']['externalReadingLinks']=links
 e['metadata']['partOfSpeechNotation']='source Polish category; not an SGJP tag'
 p=cp.encode(e);assert decode_entry(cp,p)==e
 full.append(e);packed.append(p)
assert len(full[0]['metadata']['externalReadingLinks'])>=1
(out/'external-bridge-full.json').write_text(json.dumps(full,ensure_ascii=False,indent=2)+'\n');(out/'external-bridge-compact.json').write_text(json.dumps(packed,ensure_ascii=False,indent=2)+'\n')
sim=copy.deepcopy(doc);sim['entries']=sorted(sim['entries']+packed,key=lambda x:x['surfaceKey']);before={e['surfaceKey']:e for e in doc['entries']};after={e['surfaceKey']:e for e in sim['entries']};assert len(after)==len(before)+8;assert all(after[k]==v for k,v in before.items());encoded=serialize(sim)
# Temporary standalone consumer fixture: no dictionary, manifest or installable ZIP.
(out/'consumer-simulation.json').write_bytes(encoded);(out/'base-metadata-keys.txt').write_text(''.join(k+'\n' for k in before))
report=dict(entries=8,bytes=len(encoded)-len(baseline),nodes=nodes(sim)-nodes(doc),baseSha256=BASE_SHA,sourceTablesUnchanged=True,sourcePOSNotSGJP=True,meaningRecordsNotMerged=True,installationApproved=False)
(out/'bridge-cost.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
