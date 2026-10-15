#!/usr/bin/env python3
"""Conservative ambiguity flags, not estimates of sense frequencies. Offline audit."""
import sys,json,copy,hashlib
from pathlib import Path
from collections import Counter
from review_candidate_pool import merge,modern,exact
from build_practical_candidate_modules import read_base,BASE_SHA,DICT_SHA,CompactPool,decode_entry
from build_shared_metadata_trial import serialize
from shared_metadata_v2 import nodes
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'build/frequency-ambiguity';OUT.mkdir(parents=True,exist_ok=True)
def read(p):return [json.loads(l) for l in p.read_text().splitlines()]
def dump(n,v):(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2)+'\n')
pool=merge();review={r['surfaceKey']:r for r in read(ROOT/'build/pool-review/review.jsonl')};selection=read(ROOT/'build/selection-review/selection.jsonl')
_,_,doc,words,_,_=read_base(Path(sys.argv[1]).read_bytes(),BASE_SHA,DICT_SHA,11,3);cp=CompactPool(doc);base={r['surfaceKey']:r for r in doc['entries']}
bridge={r['surfaceKey']:r for r in json.loads((ROOT/'build/selection-review/external-bridge-compact.json').read_text())}
def proper(r):return any(n!='nazwa_pospolita' for n in r.get('nameClasses',[]))
def summarize(e,k):
 proofs=[p for p in e['generatedFormProofs'] if p['form'].lower()==k.lower()]
 ids={p['interpretationId'] for p in proofs};rr=[r for r in e['interpretations'] if r['id'] in ids]
 return dict(properReadings=[r for r in rr if proper(r)],commonLemmas=sorted({r['lemma'] for r in exact(e,k,modern)}),sourceForms=sorted({p['form'] for p in proofs}))
def anchor(k):
 if k not in base:return dict(key=k,available=False)
 e=decode_entry(cp,base[k]);rr=e.get('metadata',{}).get('sourceEvidence',{}).get('lexicalReadings',[])
 rr=[r for r in rr if any(s.lower()==k.lower() for s in r.get('surfaces',[]))]
 return dict(key=k,available=True,properReadings=[r for r in rr if proper(r)],lemmas=sorted({r['lemma'] for r in rr}),readings=rr)
# Search all existing base forms: the previous highest-frequency anchor may be ambiguous.
import wordfreq
from importlib.metadata import version,distribution
assert version('wordfreq')=='3.2.0'
assert json.loads(distribution('wordfreq').read_text('direct_url.json'))['vcs_info']['commit_id']=='912caf64b657478d1dff1138efdc078947d54bb1'
needed={lemma for row in selection if row['decision']=='recommended' for lemma in review[row['surfaceKey']]['familyAnchors']}
cleanAnchors={}
for key in base:
 a=anchor(key)
 if a['properReadings'] or len(a['lemmas'])!=1 or a['lemmas'][0] not in needed:continue
 f=wordfreq.zipf_frequency(key,'pl')
 if f>=2.5 and f>cleanAnchors.get(a['lemmas'][0],{}).get('zipf',0):
  a['zipf']=f;cleanAnchors[a['lemmas'][0]]=a
results=[];safe=[]
for prev in selection:
 if prev['decision']!='recommended':continue
 k=prev['surfaceKey'];r=review[k];ev=summarize(pool[k]['nativeEvidence'],k);flags=[]
 if ev['properReadings']:flags.append('candidate-proper-name-collision')
 if len(ev['commonLemmas'])>1:flags.append('candidate-multiple-common-lemmas')
 aa=[]
 if r['status']=='meets-original-frequency-policy' and r['zipf']<2:
  aa=[anchor(v['key']) for v in r['familyAnchors'].values()]
  aa += [cleanAnchors[l] for l in ev['commonLemmas'] if l in cleanAnchors]
  aa=list({a['key']:a for a in aa}.values())
  # Clean anchor needs lexical proof of target lemma without competing lemma/name.
  valid=[a for a in aa if a['available'] and not a['properReadings'] and len(a['lemmas'])==1 and a['lemmas'][0] in ev['commonLemmas']]
  if not valid:flags.append('family-threshold-without-unambiguous-anchor')
 status='reserve-frequency-ambiguity' if flags else 'retained-no-detected-collision'
 results.append(dict(surfaceKey=k,zipf=r['zipf'],status=status,flags=flags,candidateEvidence=ev,anchorEvidence=aa,sourceSelectionReason=prev['reason'],frequencyInflationProven=False,senseFrequencyMeasured=False,approvedForInstallation=False))
 if not flags:safe.append(bridge[k] if k in bridge else r['metadataProposal'])
assert len(results)==1356
sim=copy.deepcopy(doc);sim['entries']=sorted(sim['entries']+safe,key=lambda x:x['surfaceKey']);assert len({e['surfaceKey'] for e in sim['entries']})==len(sim['entries'])
cost=dict(entries=len(safe),bytes=len(serialize(sim))-len(serialize(doc)),nodes=nodes(sim)-nodes(doc),remainingEntries=120000-len(sim['entries']),remainingNodes=2000000-nodes(sim),remainingBytes=33554432-len(serialize(sim)),includesStageDescription=False)
report=dict(total=len(results),counts=dict(Counter(r['status'] for r in results)),flags=dict(Counter(f for r in results for f in r['flags'])),cost=cost,baseSha256=BASE_SHA,frequencyInflationProven=0,scope='Known SGJP readings and v11 family anchors only; no sense-disambiguated corpus measurement.',inputHashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'build/selection-review/selection.jsonl',ROOT/'build/pool-review/review.jsonl',ROOT/'build/five-modules/candidates.jsonl',ROOT/'build/practical-audit-reproduced/decisions.jsonl']})
dump('report.json',report);(OUT/'audit.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in results))
statusByKey={r['surfaceKey']:r for r in results};combined=[]
for row in selection:
 row=copy.deepcopy(row);x=statusByKey.get(row['surfaceKey'])
 if x and x['flags']:row.update(decision='reserve',reason='frequency-ambiguity:'+','.join(x['flags']))
 combined.append(row)
(OUT/'selection-updated.jsonl').write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in combined))
for state in ['recommended','reserve','held']:(OUT/(state+'.txt')).write_text(''.join(r['surfaceKey']+'\n' for r in combined if r['decision']==state))
report['wholePoolCounts']=dict(Counter(r['decision'] for r in combined));dump('report.json',report)
lines=['# Kontrola niejednoznaczności częstości względem v11','', 'Automatyczna, powtarzalna kontrola odczytań SGJP i kotwic rodzin w v11. Nie jest pomiarem częstości poszczególnych znaczeń. Nie stwierdza, że homonim zawyżył częstość; wykrywa powód do ostrożności.','',f'Z 1356 rekomendacji zachowano {len(safe)} bez wykrytej kolizji; {1356-len(safe)} przesunięto do rezerwy. Nie usunięto danych v11 ani żadnego odczytania źródłowego.','', '## Reguły','', '- Nazwa własna z tym samym zapisem po lower(): rezerwa do czasu rozdzielenia użyć. Wielka litera i kategorie nazwy pozostają w dowodzie.', '- Więcej niż jeden współczesny lemat pospolity: rezerwa. Kilka przypadków tego samego lematu nie stanowi kolizji. Sufiksy identyfikujące homonimy pozostają zachowane.', '- Dla form Zipf < 2 przyjętych dzięki rodzinie: co najmniej jedna kotwica v11 musi mieć dokładnie jeden lemat zgodny z kandydatem i nie mieć konkurencyjnej nazwy własnej.', '- Brak flagi oznacza jedynie brak wykrytej kolizji w tych danych. Nie wyklucza nieopisanej nazwy, użycia obcojęzycznego ani wielu znaczeń jednego lematu.', '- Osiem form zewnętrznych ma osobne dowody; brak odczytań SGJP nie dowodzi jednoznaczności. Nie przypisano im nieistniejących tagów.', '', '## Koszt zachowanej puli','',json.dumps(cost,ensure_ascii=False), '', 'Koszt metadanych bez przyszłego opisu etapu, nie rozmiar ZIP ani RAM. Wagi nie zostały zmienione. Nie zbudowano langpacka ani APK.','', '## Wykryte przypadki','', '| Klucz | Powody | Lematy pospolite | Nazwy własne |','|---|---|---|---|']
for r in results:
 if r['flags']:lines.append('| '+r['surfaceKey']+' | '+', '.join(r['flags'])+' | '+', '.join(r['candidateEvidence']['commonLemmas'])+' | '+', '.join(sorted({x['lemma'] for x in r['candidateEvidence']['properReadings']}))+' |')
lines+=['','## Dalsze rozstrzygnięcie','','Rezerwa nie jest listą błędnych słów. Przywracanie wymaga przykładów użycia odpowiedniego odczytania z wiarygodnego korpusu lub dodatkowej jawnej decyzji o przydatności; nie zgadywania udziału znaczeń z oceny modelu. Zachowana pula również nie ma gwarancji poprawy Top-3.','', 'Odtworzenie: python3 scripts/audit_frequency_ambiguity.py BASE_ZIP. Wejścia i ich SHA-256: report.json. Pełny wynik puli 7570: selection-updated.jsonl.']
(OUT/'RAPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
