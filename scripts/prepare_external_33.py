#!/usr/bin/env python3
"""Extract factual evidence for 33 existing candidates; never invent paradigms."""
import argparse,copy,hashlib,json,re,urllib.request,datetime
from pathlib import Path
from collections import Counter
from build_practical_candidate_modules import read_base,BASE_SHA,DICT_SHA
from build_shared_metadata_trial import serialize
from shared_metadata_v2 import nodes
ROOT=Path(__file__).resolve().parents[1]
FAMILIES={'powerbank','hashtag','streaming','streamować','googlować','scrollować'}
def sha(raw):return hashlib.sha256(raw).hexdigest()
def dump(path,obj):path.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n')
def selected():return [json.loads(l) for l in (ROOT/'build/pool-review/review.jsonl').read_text().splitlines() if json.loads(l)['status']=='external-source-supported-needs-metadata']
def extract(out,fetch):
 from bs4 import BeautifulSoup
 obs={o['key']:o for o in json.loads((ROOT/'source/practical-evidence-v2/observations.json').read_text())['records'] if o['key'] in FAMILIES};rows=selected();facts=[]
 for lemma,o in sorted(obs.items()):
  private=out/'private-pages';private.mkdir(parents=True,exist_ok=True);path=private/(lemma+'.html')
  if fetch and not path.exists():
   req=urllib.request.Request(o['url'],headers={'User-Agent':'CleverKeysPL-source-audit/1.0'})
   with urllib.request.urlopen(req,timeout=25) as response:raw=response.read(3000001)
   if len(raw)>3000000:raise ValueError('response too large')
   path.write_bytes(raw)
  raw=path.read_bytes();s=BeautifulSoup(raw,'html.parser');targets={r['surfaceKey'] for r in rows if any(e['key']==lemma for e in r['externalObservations'])};provenance=dict(source=o['source'],url=o['url'],retrievedDate='2026-10-15',htmlSha256=sha(raw));found=[]
  if lemma=='powerbank':
   table=s.select_one('table.fleksja-table');assert table
   numbers=[x.get_text(' ',strip=True) for x in table.select('thead th')][1:3];assert numbers==['liczba pojedyncza','liczba mnoga']
   cells=[]
   for tr in table.select('tbody tr'):
    case=tr.select_one('th span');assert case
    for number,td in zip(numbers,tr.find_all('td')[:2]):
     for span in td.select('.forma'):cells.append(dict(surface=span.get_text(strip=True),case=case['data-tippy-content'],number=number))
   assert len(cells)==14
   for key in targets:
    matching=[c for c in cells if c['surface']==key];assert matching,key
    found.append(dict(surfaceKey=key,observedSurfaces=[key],kind='explicit-case-number-table',lemma=lemma,senseId='81432',selector='table.fleksja-table',sourceGrammar={'partOfSpeech':'rzeczownik','gender':'m3'},caseNumberCells=[{k:v for k,v in c.items() if k!='surface'} for c in matching]))
   text=s.get_text(' ',strip=True);assert 'część mowy: rzeczownik' in text and 'rodzaj gramatyczny: m3' in text
  elif lemma in {'streaming','streamować','googlować'}:
   articles=s.select('article[id^=gramatyka-]');assert len(articles)==(2 if lemma=='streamować' else 1)
   for article in articles:
    section=article.find_parent('section');sense=section['id'];grammar=article.select_one('p.ds-w-oc').get_text(' ',strip=True)
    assert grammar in ['rzeczownik rodzaj męskorzeczowy odmienny','czasownik aspekt niedokonany przechodni']
    all_forms=article.select('p.ds-forms--all-forms')
    if not all_forms:all_forms=[p for p in article.select('p') if p.select_one('.ds-forms__header')]
    assert len(all_forms)==1
    text=all_forms[0].get_text(' ',strip=True).split('formy alfabetycznie:',1)[1].split('|',1)[0]
    forms={f.strip() for f in text.split(';') if f.strip()};assert all(f.isalpha() for f in forms)
    for key in targets:
     assert key in forms,(lemma,key)
     found.append(dict(surfaceKey=key,observedSurfaces=[key],kind='explicit-form-list',lemma=lemma,senseId=sense,selector='#'+article['id'],sourceGrammarText=grammar,caseNumberCells=None))
  elif lemma=='hashtag':
   cited={p.get_text(' ',strip=True) for p in s.select('p.cytat .forma')};variants={x.get_text(' ',strip=True) for x in s.select('.forma')};assert 'hashtag' in variants and 'hashtaga' in cited
   for key in targets:
    assert key in cited or key=='hashtag'
    found.append(dict(surfaceKey=key,observedSurfaces=[key],kind='variant-or-citation-only',lemma=None,senseId='86506',selector='p.cytat .forma; variant section',sourceEntry='hasztag',sourceGrammar=None,caseNumberCells=None))
  else:
   examples=[d.select_one('.value') for d in s.select('.entry-row') if d.select_one('.title') and d.select_one('.title').get_text(strip=True)=='Przykłady użycia'];assert len(examples)==1
   cited={t.get_text(' ',strip=True) for t in examples[0].select('strong')}
   head=[d.select_one('.value').select_one('b').get_text(strip=True) for d in s.select('.entry-row') if d.select_one('.title') and d.select_one('.title').get_text(strip=True)=='Hasło'];assert head==['scrollować']
   for key in targets:
    observed=sorted({v for v in cited|set(head) if v.lower()==key});assert observed,key
    found.append(dict(surfaceKey=key,observedSurfaces=observed,kind='headword-or-citation-only',lemma=lemma,senseId='scrollowac',selector='.entry-row: Przykłady użycia strong / Hasło b',sourceGrammar=None,caseNumberCells=None,lowercaseDirectlyAttested=key in observed))
  for f in found:f['source']=provenance
  facts.extend(found)
 assert {f['surfaceKey'] for f in facts}=={r['surfaceKey'] for r in rows}
 assert len(facts)==38 # Five streamować forms retain two distinct source senses.
 dump(out/'source-facts.json',facts)

def build(out,base):
 rows=selected();assert len(rows)==33;facts=json.loads((out/'source-facts.json').read_text());members,manifest,doc,words,_,_=read_base(base.read_bytes(),BASE_SHA,DICT_SHA,11,3);basekeys={w.lower() for w,_ in words};before=serialize(doc);result=[]
 for row in rows:
  key=row['surfaceKey'];assert key not in basekeys;fs=[f for f in facts if f['surfaceKey']==key];assert fs
  formal=all(f['kind'] in {'explicit-case-number-table','explicit-form-list'} for f in fs)
  proposal=dict(surfaceKey=key,metadata=dict(externalLexicalEvidence=copy.deepcopy(fs)))
  result.append(dict(surfaceKey=key,zipf=row['zipf'],status='dictionary-form-link-confirmed' if formal else 'citation-supported-partial-morphology',metadataDraft=proposal,typedSGJPLemmaRelation=False,fullMorphologicalTagsClaimed=False,completeParadigmClaimed=False,approvedForInstallation=False))
 full=[r['metadataDraft'] for r in result if r['status']=='dictionary-form-link-confirmed'];positive=[r['metadataDraft'] for r in result if r['status']=='dictionary-form-link-confirmed' and r['zipf']>=1]
 scenarios={}
 for name,entries in [('formal27',full),('formalPositive',positive),('all33Drafts',[r['metadataDraft'] for r in result])]:
  simulation=copy.deepcopy(doc);simulation['entries']=sorted(simulation['entries']+entries,key=lambda x:x['surfaceKey']);assert len({e['surfaceKey'] for e in simulation['entries']})==len(simulation['entries']);encoded=serialize(simulation);decoded=json.loads(encoded);bykey={e['surfaceKey']:e for e in decoded['entries']}
  assert all(bykey[e['surfaceKey']]==e for e in entries)
  assert all(bykey[e['surfaceKey']]==e for e in doc['entries'])
  scenarios[name]=dict(entries=len(entries),bytes=len(encoded)-len(before),nodes=nodes(simulation)-nodes(doc),includesPerEntrySourceProvenance=True,includesStageProvenance=False)
 assert len(full)==27 and len(positive)==8
 sf=[f for f in facts if f['lemma']=='streamować'];assert len({f['senseId'] for f in sf})==2
 assert all('caseNumberCells' in f and f['caseNumberCells'] is None for f in facts if f['lemma']=='streaming')
 (out/'metadata-drafts.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in result))
 report=dict(baseSha256=BASE_SHA,inputReviewSha256=sha((ROOT/'build/pool-review/review.jsonl').read_bytes()),sourceFactsSha256=sha((out/'source-facts.json').read_bytes()),total=33,families=6,sourceReadings=38,states=dict(Counter(r['status'] for r in result)),formalPositive=8,formalLowFrequency=19,partialPositive=sum(r['zipf']>=1 and r['status']=='citation-supported-partial-morphology' for r in result),scenarios=scenarios,consumerCodeCommit='0b94e323789e96c44a77f762a6f83fa11e285699',consumerInspection='metadataJson retains opaque JSON; typed sourceLemmas reads only sourceEvidence; externalLexicalEvidence not interpreted',consumerRuntimeTestPerformed=False,installationApproved=0)
 dump(out/'report.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--extract',action='store_true');p.add_argument('--fetch',action='store_true');a=p.parse_args();a.out.mkdir(exist_ok=True,parents=True)
 if a.extract:extract(a.out,a.fetch)
 elif not (a.out/'source-facts.json').exists():
  (a.out/'source-facts.json').write_bytes((ROOT/'source/external-evidence-v3/source-facts.json').read_bytes())
 build(a.out,a.base)
if __name__=='__main__':main()
