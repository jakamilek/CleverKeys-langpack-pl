#!/usr/bin/env python3
"""Review all 7570 candidates without modifying v11 or creating an install pack."""
import argparse,json,re,hashlib,datetime,time,urllib.error
from pathlib import Path
from collections import Counter,defaultdict
from importlib.metadata import version,distribution
from build_practical_candidate_modules import SourceOracle,read_base,BASE_SHA,DICT_SHA,CompactPool,decode_entry,compact_entry,canonical_bytes,nodes
from build_common_forms_trial import ordinary,selected
from intake_practical_candidates import fetch
ROOT=Path(__file__).resolve().parents[1]
OBSOLETE={'daw.','przest.','hist.','gwar.'}
def labels(r):return {token.strip() for label in r.get('labels',[]) for token in label.split(',')}
def modern(r):return ordinary(r) and not any(x in OBSOLETE or x.startswith('przest.') for x in labels(r))
def exact(e,key,predicate):
 ids={p['interpretationId'] for p in e['generatedFormProofs'] if p['form']==key}
 return [r for r in e['interpretations'] if r['id'] in ids and predicate(r)]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def merge():
 new=[json.loads(l) for l in (ROOT/'build/five-modules/candidates.jsonl').read_text().splitlines()];old=[json.loads(l) for l in (ROOT/'build/practical-audit-reproduced/decisions.jsonl').read_text().splitlines()]
 pool={r['surfaceKey']:r for r in new if not r['inBase'] and r['keyShape']=='single-key'}
 for r in old:
  key=r['surfaceKey']
  if key not in pool:
   oo=[v['original'] for v in r['records']];o=oo[0]
   pool[key]=dict(surfaceKey=key,sourceSpellings=sorted({s for v in oo for s in v['sourceSpellings']}),sourceUnits=[s for v in oo for s in v.get('sourceUnits',[])],modules=sorted({v['module'] for v in r['records']}),nativeEvidence=o['nativeEvidence'],zipf=o['wordfreqZipfPl'])
  pool[key]['previousDecision']=r['state']
 assert len(pool)==7570
 return pool

def fetch_pages(pool,out):
 titles=sorted({s for k,r in pool.items() if not exact(r['nativeEvidence'],k,modern) for s in r['sourceSpellings'] if s and ':' not in s})
 src=out/'dictionary-pages';src.mkdir(parents=True,exist_ok=True);dump(src/'requested-titles.json',titles)
 lock=[]
 for start in range(0,len(titles),50):
  chunk=titles[start:start+50];path=src/f'pages-{start//50:03d}.json';params=dict(action='query',prop='revisions',rvprop='ids|timestamp|content',rvslots='main',titles='|'.join(chunk))
  if not path.exists():
   for attempt in range(3):
    try:
     time.sleep(3);raw,data,url=fetch('pl.wiktionary.org',params);path.write_bytes(raw);break
    except (urllib.error.URLError,TimeoutError) as e:
     if attempt==2:raise
     time.sleep(min(30,int(getattr(e,'headers',{}).get('Retry-After','15'))))
  data=json.loads(path.read_text());assert 'query' in data and len(data['query']['pages'])<=50
  lock.append(dict(path=path.name,sha256=digest(path),requested=chunk,revisionIds=[p['revisions'][0]['revid'] for p in data['query']['pages'] if 'revisions'in p]))
  dump(src/'lock.json',dict(complete=start+50>=len(titles),files=lock));print('dictionary pages',min(start+50,len(titles)),'/',len(titles),flush=True)

def inspect_pages(out):
 src=out/'dictionary-pages';lock=json.loads((src/'lock.json').read_text());assert lock['complete'];result={}
 for meta in lock['files']:
  path=src/meta['path'];assert digest(path)==meta['sha256']
  for page in json.loads(path.read_text())['query']['pages']:
   title=page['title'];rec=dict(title=title,snapshot=meta['path'],missing=page.get('missing',False),polishSection=False,numberedDefinitions=0,redirect=False,qualifiers=[])
   if 'revisions' in page:
    rev=page['revisions'][0];text=rev['slots']['main']['content'];rec.update(revision=rev['revid'],timestamp=rev['timestamp'],url='https://pl.wiktionary.org/w/index.php?oldid='+str(rev['revid']));rec['redirect']=bool(re.match(r'\s*#(?:REDIRECT|PATRZ|PRZEKIERUJ)',text,re.I))
    sections=re.split(r'(?m)^==([^=\n].*?)==\s*$',text)
    for i in range(1,len(sections),2):
     if re.search(r'\{\{język polski\}\}',sections[i]):
      body=sections[i+1];rec['polishSection']=True
      meanings=re.search(r'\{\{znaczenia\}\}(.*?)(?=\{\{(?:odmiana|przykłady|składnia|kolokacje)\}\}|\Z)',body,re.S)
      defs=meanings.group(1) if meanings else ''
      rec['numberedDefinitions']=len(re.findall(r'(?m)^:\s*\(\d+\.\d+\)',defs));rec['qualifiers']=sorted(set(re.findall(r'\{\{(daw|przest|hist|gwara|reg|wulg|pot|obraź|pejor|slang|rzad)(?:\||\}\})',defs)))
      rec['maintenanceFlags']=sorted(set(re.findall(r'\{\{(do weryfikacji|dopracować|brak źródeł|nieudokumentowane)(?:\||\}\})',body,re.I)))
      rec['qualifiers']=sorted(set(re.findall(r'\{\{(daw|przest|hist|gw-pl|gwara|reg|wulg|pot|obraź|pejor|slang|rzad|żart)(?:\||\}\})',defs)))
      rec['crossReferenceDefinitions']=len(re.findall(r'\{\{(?:zob|zobacz|forma)(?:\||\}\})',defs))
      rec['inflectionSectionPresent']='{{odmiana}}' in body
      inflection=re.search(r'\{\{odmiana\}\}(.*?)(?=\{\{przykłady\}\}|\Z)',body,re.S)
      cells=[]
      if inflection:
       for cell,value in re.findall(r'(?m)^\|\s*((?:Mianownik|Dopełniacz|Celownik|Biernik|Narzędnik|Miejscownik|Wołacz) (?:lp|lm))\s*=\s*([^\n]*)',inflection.group(1)):
        value=value.strip();literal=re.fullmatch(r'\[\[([^\[\]|]+)\]\]',value)
        if literal:value=literal.group(1)
        if value and all(c.isalpha() for c in value):cells.append(dict(cell=cell,form=value))
      rec['literalInflectionCells']=cells
      rec['completeParadigmClaimed']=False
      example=re.search(r'\{\{przykłady\}\}(.*?)(?=\{\{(?:składnia|kolokacje|synonimy)\}\}|\Z)',body,re.S)
      rec['numberedExamples']=len(re.findall(r'(?m)^:\s*\(\d+\.\d+\)',example.group(1))) if example else 0
      rec['referenceMarkers']=len(re.findall(r'<ref(?:\s|>)',body))
   result[title]=rec
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,required=True);p.add_argument('--base',type=Path,required=True);p.add_argument('--fetch',action='store_true');a=p.parse_args();a.out.mkdir(parents=True,exist_ok=True);pool=merge()
 if a.fetch:fetch_pages(pool,a.out)
 pages=inspect_pages(a.out)
 import wordfreq
 assert version('wordfreq')=='3.2.0'
 assert json.loads(distribution('wordfreq').read_text('direct_url.json'))['vcs_info']['commit_id']=='912caf64b657478d1dff1138efdc078947d54bb1'
 members,manifest,doc,words,_,_=read_base(a.base.read_bytes(),BASE_SHA,DICT_SHA,11,3);cp=CompactPool(doc);anchors={}
 for e in doc['entries']:
  f=wordfreq.zipf_frequency(e['surfaceKey'],'pl')
  if f<2.5:continue
  for r in decode_entry(cp,e).get('metadata',{}).get('sourceEvidence',{}).get('lexicalReadings',[]):
   if e['surfaceKey'] in r['surfaces'] and modern(dict(tag=r['partOfSpeech'],nameClasses=r.get('nameClasses',[]),labels=r.get('labels',[]))):
    if f>anchors.get(r['lemma'],{}).get('zipf',0):anchors[r['lemma']]=dict(key=e['surfaceKey'],zipf=f)
 results=[]
 for key,r in sorted(pool.items()):
  evidence=r['nativeEvidence'];matches=exact(evidence,key,modern);old_matches=exact(evidence,key,ordinary);frequency=r['zipf'];spellings=r['sourceSpellings'];source_pages=[pages[s] for s in spellings if s in pages];brand=any(u.get('kind')=='archived-app-identity-needs-current-verification' or u.get('source',{}).get('kind') in {'brand','retired-service','initialism','orthographic-gap'} for u in r.get('sourceUnits',[])) or 'apps-and-services' in r['modules']
  family={x['lemma']:anchors[x['lemma']] for x in matches if x['lemma'] in anchors};family_zipf=max((v['zipf'] for v in family.values()),default=0);flags=sorted({v for x in matches for v in labels(x)});lexical=bool(matches) and key in spellings and not brand
  external=[u['source'] for u in r.get('sourceUnits',[]) if u.get('kind')=='previous-source-observation-not-newly-revalidated' and u.get('source',{}).get('spellingSupported') and any(f.lower()==key for f in u['source'].get('attestedForms',[]))]
  external=list({json.dumps(o,sort_keys=True):o for o in external}.values())
  if lexical:state='meets-original-frequency-policy' if selected(frequency,family_zipf) else 'lower-frequency-working-pool' if frequency>=1 else 'lexical-proof-frequency-unresolved'
  elif brand:state='name-or-brand-needs-identity-review'
  elif matches:state='source-capitalization-needs-review'
  elif external:state='external-source-supported-needs-metadata'
  elif exact(evidence,key,lambda x:True):state='excluded-by-lexical-profile'
  elif any(p['polishSection'] and p['numberedDefinitions']>0 and not p.get('maintenanceFlags') for p in source_pages):state='polish-dictionary-entry-needs-morphology-and-usage'
  elif any(p['polishSection'] and p['numberedDefinitions']>0 for p in source_pages):state='dictionary-entry-flagged-for-verification'
  elif any(p['redirect'] for p in source_pages):state='redirect-needs-target-review'
  elif any(not p['missing'] for p in source_pages):state='page-without-parsed-polish-definition'
  else:state='no-lexical-proof-yet'
  encoded=cp.encode(compact_entry(key,evidence)) if lexical else None
  profile_reasons=sorted({reason for x in exact(evidence,key,lambda x:True) for reason in (['proper-name'] if any(n!='nazwa_pospolita' for n in x['nameClasses']) else [])+(['obsolete-or-regional-label'] if any(t in OBSOLETE or t.startswith('przest.') for t in labels(x)) else [])+(['nonlexical-part-of-speech'] if x['tag'].split(':')[0] in {'ign','interp','brev','romandig','frag'} else [])})
  results.append(dict(externalObservations=external,profileReasons=profile_reasons,surfaceKey=key,sourceSpellings=spellings,modules=r['modules'],previousDecision=r.get('previousDecision'),status=state,zipf=frequency,familyAnchors=family,usageLabels=flags,allReadingLabels=sorted({v for x in evidence['interpretations'] for v in labels(x)}),compoundObsoleteFilterChanged=bool(old_matches and not matches),dictionaryPages=source_pages,lexicalReadings=matches,metadataProposal=encoded,runtimeEstimate=dict(bytes=len(canonical_bytes(encoded)),nodes=nodes(encoded)) if encoded else None,approvedForInstallation=False))
 (a.out/'review.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in results));report=dict(total=len(results),statusCounts=dict(Counter(r['status'] for r in results)),compoundObsoleteFilterChanged=[r['surfaceKey'] for r in results if r['compoundObsoleteFilterChanged']],pages=dict(total=len(pages),missing=sum(p['missing'] for p in pages.values()),withPolishDefinitions=sum(p['polishSection'] and p['numberedDefinitions']>0 for p in pages.values()),redirects=sum(p['redirect'] for p in pages.values())),inputHashes={str(p.relative_to(ROOT)):digest(p) for p in [ROOT/'build/five-modules/candidates.jsonl',ROOT/'build/practical-audit-reproduced/decisions.jsonl']},baseSha256=BASE_SHA,approvedAdditions=0)
 dump(a.out/'report.json',report);print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
