#!/usr/bin/env python3
"""Editorial shortlist from locked evidence; no installable output or weight edits."""
import json,sys,copy,hashlib
from pathlib import Path
from collections import Counter
from build_practical_candidate_modules import read_base,BASE_SHA,DICT_SHA
from build_shared_metadata_trial import serialize
from shared_metadata_v2 import nodes
ROOT=Path(__file__).resolve().parents[1]; OUT=ROOT/'build/selection-review';OUT.mkdir(parents=True,exist_ok=True)
def rows(p):return [json.loads(l) for l in p.read_text().splitlines()]
def dump(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n')
review=rows(ROOT/'build/pool-review/review.jsonl');tables={r['surfaceKey']:r for r in rows(ROOT/'build/external-33/sense-scoped-case-evidence.jsonl')}
bridged=json.loads((OUT/'external-bridge-compact.json').read_text());bridge={r['surfaceKey']:r for r in bridged}
# Editorial policy, not linguistic truth or proof of everyday utility.
marked={'rzad.','reg.','pogard.','lekcew.','wulg.','indyw.'}
practical={'komp.','techn.','kulin.','bud.','elektr.','praw.','ekon.','handl.','mot.'}
specialist={'bot.','zool.','mikol.','paleont.','num.','monet.','mit.','astrol.','archeol.','geol.','żegl.','mors.','poligr.'}
policy=dict(version=1,markedReserve=sorted(marked),specialistReserve=sorted(specialist),lowerFrequencyPriority=sorted(practical),minimumZipf=1,originalPolicy='Zipf >= 2 OR Zipf >= 1 with v11 same-lemma anchor >= 2.5',note='Recommendation is editorial. Frequency is surface-level, not sense-specific. pot./slang are not automatic exclusions.')
dump(OUT/'selection-policy.json',policy)
results=[];entries=[];table171=[]
for r in review:
 k=r['surfaceKey'];s=r['status'];labels=set(r['usageLabels']);decision='held';reason=s;meta=None
 if k in bridge:decision='recommended';reason='explicit-external-form-link-and-positive-frequency-reader-tested';meta=bridge[k]
 elif s in {'meets-original-frequency-policy','lower-frequency-working-pool'}:
  if labels & marked:decision='reserve';reason='marked-usage:'+','.join(sorted(labels&marked))
  elif labels & specialist and not labels & practical:decision='reserve';reason='specialist-domain:'+','.join(sorted(labels&specialist))
  elif s=='meets-original-frequency-policy':decision='recommended';reason='SGJP-exact-form-and-original-frequency-policy';meta=r['metadataProposal']
  elif labels & practical:decision='recommended';reason='SGJP-exact-form-lower-frequency-practical-domain:'+','.join(sorted(labels&practical));meta=r['metadataProposal']
  else:decision='reserve';reason='lower-frequency-no-source-domain-priority'
 elif s=='lexical-proof-frequency-unresolved':decision='reserve';reason='SGJP-form-confirmed-frequency-below-1'
 elif k in tables and tables[k]['status']=='explicit-sense-scoped-table-evidence' and r['zipf']>=1:
  decision='reserve';reason='dictionary-case-table-confirmed-needs-sense-specific-usage-and-metadata'
  pageflags=sorted({q for p in r['dictionaryPages'] for q in p['qualifiers']})
  evidence=dict(surfaceKey=k,zipf=r['zipf'],pageQualifiers=pageflags,qualifiersAreSenseScoped=False,caseTableReadings=tables[k]['caseTableReadings'],pages=r['dictionaryPages'],reason=reason)
  # Page-level markers flag follow-up, never assign a label to an unverified sense.
  evidence['followUpReasons']=['frequency-does-not-identify-Polish-sense','table-is-not-full-lexical-reading','consumer-metadata-not-yet-constructed']
  if pageflags:evidence['followUpReasons'].append('scope-of-page-qualifiers-needs-check')
  if not any(p['referenceMarkers'] for p in r['dictionaryPages']):evidence['followUpReasons'].append('no-reference-marker-in-parsed-page')
  table171.append(evidence)
 results.append(dict(surfaceKey=k,decision=decision,reason=reason,sourceStatus=s,zipf=r['zipf'],usageLabels=r['usageLabels'],approvedForInstallation=False))
 if meta:entries.append(meta)
assert len(review)==7570 and len(table171)==171 and len({r['surfaceKey'] for r in results})==7570
_,_,doc,words,_,_=read_base(Path(sys.argv[1]).read_bytes(),BASE_SHA,DICT_SHA,11,3)
assert not ({e['surfaceKey'] for e in entries}&set(words))
sim=copy.deepcopy(doc);sim['entries']=sorted(sim['entries']+entries,key=lambda e:e['surfaceKey']);assert len({e['surfaceKey'] for e in sim['entries']})==len(sim['entries'])
cost=dict(entries=len(entries),bytes=len(serialize(sim))-len(serialize(doc)),nodes=nodes(sim)-nodes(doc),includesStageDescription=False,remainingEntries=120000-len(sim['entries']),remainingNodes=2000000-nodes(sim),remainingBytes=33554432-len(serialize(sim)))
assert min(cost['remainingEntries'],cost['remainingNodes'],cost['remainingBytes'])>=0
report=dict(total=len(results),counts=dict(Counter(r['decision'] for r in results)),reasons=dict(Counter(r['reason'] for r in results)),dictionary171=len(table171),cost=cost,baseSha256=BASE_SHA,baseUnchanged=True,approvedForInstallation=False,inputHashes={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [ROOT/'build/pool-review/review.jsonl',ROOT/'build/external-33/sense-scoped-case-evidence.jsonl',OUT/'external-bridge-compact.json']})
for name,rr in [('selection.jsonl',results),('dictionary-171-review.jsonl',table171)]: (OUT/name).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rr))
for d in ['recommended','reserve','held']:(OUT/(d+'.txt')).write_text(''.join(r['surfaceKey']+'\n' for r in results if r['decision']==d))
dump(OUT/'selection-report.json',report)
lines=['# Selekcja kandydatów względem v11','', 'To rekomendacja redakcyjna do kolejnego etapu, nie zgoda na instalację. V11 i jej wagi pozostają niezmienione. V12 pominięta.','', '| Wynik | Liczba |','|---|---:|']
for d,pl in [('recommended','Rekomendowane'),('reserve','Rezerwa'),('held','Wstrzymane')]:lines.append(f'| {pl} | {report["counts"][d]} |')
lines+=['', '## Zasady i ograniczenia','', 'SGJP potwierdza formę; wordfreq opisuje częstość zapisu, nie znaczenia. Rekomendacja nie dowodzi codziennej użyteczności każdego wpisu. Pozostawiono dotychczasowy próg oraz osobno wybrano formy >= 1 z wyraźnym kwalifikatorem praktycznej dziedziny. Potoczność i slang nie wykluczają. Rzadkie, obraźliwe i wulgarne oraz wybrane specjalistyczne dziedziny są w rezerwie. Dokładne, jawne zbiory kwalifikatorów są w selection-policy.json; to wybór redakcyjny, nie nowa wiedza źródłowa.', '', '171 kandydatur z Wikisłownika pozostaje w rezerwie: przypisano komórki tabeli do zakresu znaczenia, ale nie zamknięto dowodu użycia konkretnego polskiego znaczenia ani jego docelowych metadanych. Każda ma rekord z tabelą, wersją strony, kwalifikatorami strony i dalszymi brakami. Kwalifikatorów strony nie przypisano automatycznie do znaczenia. Brak znacznika referencji nie oznacza braku wszystkich możliwych dowodów.', '', 'Wstrzymanie nie oznacza uznania słowa za błędne. Obejmuje m.in. nazwy wymagające weryfikacji tożsamości, kapitalizację, profil historyczny i brak wystarczającego dowodu. Poprzednie potwierdzenia językowe zachowano w sourceStatus.', '', '## Czytnik v11','', 'Osiem form: googlować, googluje, powerbank, powerbanki, streaming, streamingu, streamować, streamuje. Test uruchomiono na niezmienionych źródłach czytnika z commitu 0b94e323789e96c44a77f762a6f83fa11e285699: 4 pary dodatnie, 2 ujemne, zachowanie dwóch znaczeń streamować i wszystkich 114299 istniejących wpisów. Kategorie części mowy są dosłownymi kategoriami źródeł, nie tagami SGJP. To test JVM, nie pomiar RAM telefonu i nie test jakości Top-3.', '', '## Koszt rekomendacji','',f'{cost["entries"]} wpisów; {cost["nodes"]} elementów JSON; {cost["bytes"]} bajtów metadanych. Pozostaje {cost["remainingEntries"]} wpisów, {cost["remainingNodes"]} elementów JSON i {cost["remainingBytes"]} bajtów limitu. Koszt obejmuje źródła przy wpisach, ale nie przyszły opis etapu. Nie jest to rozmiar ZIP ani RAM.', '', '## Przykłady według powodów','']
for reason,count in report['reasons'].items():lines.append(f'- {reason}: {count}; przykłady: '+', '.join(r['surfaceKey'] for r in results if r['reason']==reason)[:240])
lines+=['','## Odtworzenie','','Najpierw istniejące review_candidate_pool.py oraz map_dictionary_case_evidence.py i prepare_external_33.py; następnie bridge_external_lemmas.py BASE_ZIP oraz select_reviewed_candidates.py BASE_ZIP. Dane i hashe wejść zachowano w paczce. Żaden krok nie tworzy pakietu instalacyjnego.']
(OUT/'RAPORT.md').write_text('\n'.join(lines)+'\n');print(json.dumps(report,ensure_ascii=False,indent=2))
