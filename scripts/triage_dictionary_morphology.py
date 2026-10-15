#!/usr/bin/env python3
"""Classify evidence already extracted from Polish dictionary sections, no paradigms."""
import json,hashlib
from pathlib import Path
from collections import Counter
ROOT=Path(__file__).resolve().parents[1];out=ROOT/'build/external-33';source=ROOT/'build/pool-review/review.jsonl';rows=[json.loads(l) for l in source.read_text().splitlines()];results=[]
for r in rows:
 if r['status']!='polish-dictionary-entry-needs-morphology-and-usage':continue
 key=r['surfaceKey'];pages=[p for p in r['dictionaryPages'] if p['polishSection'] and p['numberedDefinitions'] and not p.get('maintenanceFlags')];evidence=[]
 for p in pages:
  cells=p.get('literalInflectionCells',[]);exact=[c for c in cells if c['form']==key];caseonly=[c for c in cells if c['form']!=key and c['form'].lower()==key]
  evidence.append(dict(title=p['title'],url=p['url'],revision=p['revision'],snapshot=p['snapshot'],exactCells=exact,caseOnlyCells=caseonly,literalCellsCount=len(cells),definitionCount=p['numberedDefinitions'],qualifiers=p['qualifiers'],referenceMarkers=p.get('referenceMarkers',0),numberedExamples=p.get('numberedExamples',0)))
 if any(p['exactCells'] for p in evidence):state='exact-form-in-case-table'
 elif any(p['caseOnlyCells'] for p in evidence):state='case-difference-in-table'
 elif any(p['literalCellsCount'] for p in evidence):state='table-without-exact-candidate-cell'
 else:state='no-literal-case-cells-extracted'
 results.append(dict(surfaceKey=key,zipf=r['zipf'],state=state,evidence=evidence,sourceSenseMappingComplete=False,approvedForInstallation=False))
assert len(results)==1776
(out/'dictionary-morphology-queue.jsonl').write_text(''.join(json.dumps(x,ensure_ascii=False)+'\n' for x in results))
exact=[r for r in results if r['state']=='exact-form-in-case-table'];report=dict(total=len(results),inputSha256=hashlib.sha256(source.read_bytes()).hexdigest(),states=dict(Counter(r['state'] for r in results)),exactPositive=sum(r['zipf']>=1 for r in exact),exactBelowThreshold=sum(r['zipf']<1 for r in exact),scope='Stored literal noun-case cells only. Missing extraction is not proof that the source lacks morphology. No sense merging or installation approvals.')
(out/'dictionary-morphology-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
