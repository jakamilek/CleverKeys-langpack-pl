#!/usr/bin/env python3
"""Keep case-table evidence attached to source sense scopes, without generating forms."""
import json,re,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build/external-33';directory=ROOT/'build/pool-review/dictionary-pages'
queue=[json.loads(l) for l in (out/'dictionary-morphology-queue.jsonl').read_text().splitlines() if json.loads(l)['state']=='exact-form-in-case-table']
lock=json.loads((directory/'lock.json').read_text());assert lock['complete'];pages={}
for meta in lock['files']:
 raw=(directory/meta['path']).read_bytes();assert hashlib.sha256(raw).hexdigest()==meta['sha256']
 for p in json.loads(raw)['query']['pages']:
  if 'revisions' in p:pages[(p['title'],p['revisions'][0]['revid'])]=p['revisions'][0]['slots']['main']['content']
def blocks(text):
 for m in re.finditer(r'\{\{odmiana-rzeczownik-polski(?=\s|\||\})',text):
  depth=0;end=None
  for tok in re.finditer(r'\{\{|\}\}',text[m.start():]):
   depth+=1 if tok.group()=='{{' else -1
   if depth==0:end=m.start()+tok.end();break
  if end is None:raise ValueError('unbalanced case table')
  before=text[:m.start()];line=before.rsplit('\n',1)[-1];scope=re.search(r'^:\s*\(([^)]+)\)',line)
  yield m.start(),end,scope.group(1) if scope else None,text[m.start():end]
result=[]
for row in queue:
 matches=[];unresolved=[]
 for e in row['evidence']:
  if not e['exactCells']:continue
  text=pages[(e['title'],e['revision'])];sections=re.split(r'(?m)^==([^=\n].*?)==\s*$',text)
  for i in range(1,len(sections),2):
   if '{{język polski}}' not in sections[i]:continue
   body=sections[i+1];m=re.search(r'\{\{odmiana\}\}(.*?)(?=\{\{przykłady\}\}|\Z)',body,re.S)
   if not m:continue
   inf=m.group(1);spans=[]
   for start,end,scope,table in blocks(inf):
    spans.append((start,end));cells=[]
    for name,value in re.findall(r'(?m)^\|\s*((?:Mianownik|Dopełniacz|Celownik|Biernik|Narzędnik|Miejscownik|Wołacz) (?:lp|lm))\s*=\s*([^\n]*)',table):
     value=value.removesuffix('}}').strip();link=re.fullmatch(r'\[\[([^\[\]|]+)\]\]',value)
     if link:value=link.group(1)
     if value==row['surfaceKey']:cells.append(dict(caseNumberSource=name,surface=value))
    if cells:
     matches.append(dict(sourceTitle=e['title'],revision=e['revision'],url=e['url'],sourceSenseScope=scope,sourceTemplate='odmiana-rzeczownik-polski',cells=cells,tableSha256=hashlib.sha256(table.encode()).hexdigest()))
     if scope is None:unresolved.append('table-without-explicit-sense-prefix')
   rest=inf
   for start,end in reversed(spans):rest=rest[:start]+rest[end:]
   other=sorted(set(re.findall(r'\{\{((?:nieodm|odmiana)[^|}\n]*)',rest)))
   if other:unresolved.append('other-morphology-templates:'+','.join(other))
 if not matches:unresolved.append('no-structured-noun-table-match')
 result.append(dict(surfaceKey=row['surfaceKey'],zipf=row['zipf'],caseTableReadings=matches,unresolved=sorted(set(unresolved)),status='explicit-sense-scoped-table-evidence' if matches and not unresolved else 'partial-table-mapping',allSensesVerified=False,approvedForInstallation=False))
assert len(result)==741
(out/'sense-scoped-case-evidence.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in result))
report=dict(total=741,statusCounts=dict(Counter(r['status'] for r in result)),positiveScoped=sum(r['zipf']>=1 and r['status']=='explicit-sense-scoped-table-evidence' for r in result),allSourceSenseScopesPreserved=True,fullEntrySemanticsClaimed=False,sourceLockSha256=hashlib.sha256((directory/'lock.json').read_bytes()).hexdigest())
(out/'sense-scoped-case-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
