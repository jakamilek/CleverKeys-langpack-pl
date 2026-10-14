#!/usr/bin/env python3
"""Broad source-surface intake; no inflection invention or installable output."""
import argparse,json,hashlib,datetime,unicodedata
from pathlib import Path
from collections import defaultdict,Counter
from concurrent.futures import ThreadPoolExecutor
import urllib.parse,time
from importlib.metadata import distribution,version
from intake_practical_candidates import fetch
from build_practical_candidate_modules import (link_targets,key_shape,read_base,BASE_SHA,DICT_SHA,SourceOracle,lexical_matches,compact_entry,CompactPool,canonical_bytes,nodes,read_snapshot,source_candidates,MORFEUSZ_VERSION,DICTIONARY_ID,WORDFREQ_COMMIT)
SCOPE={
 'communication':['Podstawowe zwroty','Zwroty grzecznościowe','Rodzina','Słowa potoczne','Najpopularniejsze słowa 1-2000'],
 'digital':['Informatyka','Technika','Slang','Gry komputerowe'],
 'home':['Dom','Jedzenie','Kulinaria','Sklepy','Napoje','Warzywa','Owoce','Kosmetyka','Ubrania'],
 'work':['Ekonomia','Prawo','Przybory szkolne','Zawody','Slang handlowców'],
 'roads':['Architektura','Transport','Motoryzacja']}
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def main():
 p=argparse.ArgumentParser();p.add_argument('--base',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--fetch',action='store_true');a=p.parse_args();root=Path(__file__).resolve().parents[1];a.out.mkdir(parents=True,exist_ok=True);src=a.out/'sources';src.mkdir(exist_ok=True)
 titles=sorted({'Indeks:Polski - '+t for ts in SCOPE.values() for t in ts})
 if a.fetch:
  def get(item):
   i,title=item;name=f'index-{i}.json';path=src/name
   params=dict(action='query',prop='revisions',rvprop='ids|timestamp|content',rvslots='main',titles=title)
   url='https://pl.wiktionary.org/w/api.php?'+urllib.parse.urlencode(dict(format='json',formatversion=2,**params))
   if path.exists():raw=path.read_bytes();data=json.loads(raw)
   else:
    time.sleep(3);raw,data,url=fetch('pl.wiktionary.org',params);path.write_bytes(raw)
   page=data['query']['pages'][0];assert page['title']==title;rev=page['revisions'][0]
   return dict(path=name,sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),title=title,url=url,revision=rev['revid'],timestamp=rev['timestamp'])
  with ThreadPoolExecutor(max_workers=1) as ex: lock=list(ex.map(get,enumerate(titles)))
  dump(src/'lock.json',dict(retrieved=datetime.datetime.now(datetime.timezone.utc).isoformat(),files=lock))
 lock=json.loads((src/'lock.json').read_text());inputs={};grouped=defaultdict(list)
 def add(surface,module,unit):
  surface=unicodedata.normalize('NFC',surface.strip())
  if surface:grouped[surface.lower()].append(dict(surface=surface,module=module,**unit))
 for meta in lock['files']:
  raw=(src/meta['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==meta['sha256'];inputs['sources/'+meta['path']]=meta['sha256'];page=json.loads(raw)['query']['pages'][0];rev=page['revisions'][0]
  for m,ts in SCOPE.items():
   if meta['title'] in ['Indeks:Polski - '+t for t in ts]:
    for surface in link_targets(rev['slots']['main']['content']):add(surface,m,dict(kind='index-discovery-only',title=meta['title'],revision=rev['revid'],url='https://pl.wiktionary.org/w/index.php?oldid='+str(rev['revid'])))
 for m,paths in {'communication':[root/'source/core_words.dic',root/'source/colloquial.dic'],'digital':[root/'source/tech.dic'],'roads':sorted((root/'source/specialized').glob('*.dic'))}.items():
  for path in paths:
   raw=path.read_bytes();inputs[str(path.relative_to(root))]=hashlib.sha256(raw).hexdigest()
   for line in raw.decode().splitlines():
    if line.strip() and not line.lstrip().startswith('#'):add(line,m,dict(kind='repository-list-unverified',path=str(path.relative_to(root))))
 _,files,_=read_snapshot(root/'source/practical-candidates-v1');terms,apps=source_candidates(files)
 for key,units in apps.items():
  for u in units:add(u['surface'],'digital',dict(kind='archived-app-identity-needs-current-verification',source=u))
 observations_path=root/'source/practical-evidence-v2/observations.json'
 observations=json.loads(observations_path.read_text())['records'];inputs[str(observations_path.relative_to(root))]=hashlib.sha256(observations_path.read_bytes()).hexdigest()
 for obs in observations:
  for form in sorted(set([obs['spelling']]+obs['attestedForms'])):add(form,'digital',dict(kind='previous-source-observation-not-newly-revalidated',source=obs))
 previous=[json.loads(l) for l in (root/'build/practical-audit-reproduced/decisions.jsonl').read_text().splitlines()];previous_keys={r['surfaceKey'] for r in previous}|{o['key'] for o in observations}
 import morfeusz2,wordfreq
 assert str(morfeusz2.__version__)==MORFEUSZ_VERSION
 native=morfeusz2.Morfeusz(case_handling=morfeusz2.CONDITIONALLY_CASE_SENSITIVE);assert native.dict_id()==DICTIONARY_ID
 assert version('wordfreq')=='3.2.0';assert json.loads(distribution('wordfreq').read_text('direct_url.json'))['vcs_info']['commit_id']==WORDFREQ_COMMIT
 members,manifest,doc,words,_,_=read_base(a.base.read_bytes(),BASE_SHA,DICT_SHA,11,3);base={w.lower():w for w,_ in words};pool=CompactPool(doc);oracle=SourceOracle(native);rows=[]
 for i,(key,units) in enumerate(sorted(grouped.items())):
  shape=key_shape(key);present=key in base;old=key in previous_keys;evidence=None;proposal=None;cost=None;z=wordfreq.zipf_frequency(key,'pl') if shape=='single-key' else None
  if present:status='already-in-v11'
  elif shape!='single-key':status='separate-phrase-or-punctuation'
  else:
   evidence=oracle.evidence(key);matches=lexical_matches(key,evidence);spellings={u['surface'] for u in units};brand=any((u['kind']=='archived-app-identity-needs-current-verification' or u.get('source',{}).get('kind') in {'brand','initialism','retired-service','orthographic-gap'}) for u in units)
   if matches and key in spellings and not brand:
    proposal=pool.encode(compact_entry(key,evidence));cost=dict(bytes=len(canonical_bytes(proposal)),nodes=nodes(proposal));status='lexically-confirmed-frequency-positive' if z>=1 else 'lexically-confirmed-frequency-unresolved'
   else:status='needs-spelling-capitalization-or-identity-evidence'
  rows.append(dict(surfaceKey=key,modules=sorted({u['module'] for u in units}),sourceSpellings=sorted({u['surface'] for u in units}),sourceUnits=units,keyShape=shape,inBase=present,baseSpelling=base.get(key),inPreviousPool=old,status=status,zipf=z,nativeEvidence=evidence,metadataProposal=proposal,runtimeEstimate=cost))
  if i%1000==0:print('checked',i,'/',len(grouped),flush=True)
 def stats(rs):
  new=[r for r in rs if not r['inBase'] and r['keyShape']=='single-key'];extra=[r for r in new if not r['inPreviousPool']];return dict(sourceKeys=len(rs),inBase=sum(r['inBase'] for r in rs),newSingleKeys=len(new),overlapPrevious=len(new)-len(extra),additionalSingleKeys=len(extra),separate=sum(not r['inBase'] and r['keyShape']!='single-key' for r in rs),status=dict(Counter(r['status'] for r in extra)))
 report=dict(baseSha256=BASE_SHA,baseWords=len(base),baseMetadata=len(doc['entries']),scope=SCOPE,sourceInputs=inputs,versions=dict(morfeusz=MORFEUSZ_VERSION,sgjp=DICTIONARY_ID,wordfreq='3.2.0',wordfreqCommit=WORDFREQ_COMMIT),totals=stats(rows),modules={m:stats([r for r in rows if m in r['modules']]) for m in SCOPE},originalPool=len(previous),previousPoolIncludingSupplement=len(previous_keys),combinedSinglePool=len(previous_keys|{r['surfaceKey'] for r in rows if not r['inBase'] and r['keyShape']=='single-key'}),approvedAdditions=0,limitations=['Source-surface census, not all possible inflections; no generated expansions.','Index category is a broad discovery scope, not proof of usefulness or meaning.','Positive frequency confirms spelling frequency, not current intended sense.','Archived app identities not freshly confirmed.','No capacity filtering; unknown costs remain unknown.','No new installation package; existing v11 untouched.'])
 estimated=[r for r in rows if not r['inBase'] and not r['inPreviousPool'] and r['runtimeEstimate']];report['additionalLexicalEstimate']=dict(entries=len(estimated),bytes=sum(r['runtimeEstimate']['bytes'] for r in estimated),nodes=sum(r['runtimeEstimate']['nodes'] for r in estimated),includesProvenance=False,approved=False)
 (a.out/'candidates.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows));dump(a.out/'report.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
