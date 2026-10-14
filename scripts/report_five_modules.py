#!/usr/bin/env python3
"""Render the audit census and entry-only cost of an unapproved scenario."""
import json,hashlib,zipfile,sys
from pathlib import Path
from copy import deepcopy
from build_shared_metadata_trial import serialize
from shared_metadata_v2 import nodes
root=Path(__file__).resolve().parents[1];out=root/'build/five-modules';r=json.loads((out/'report.json').read_text());rows=[json.loads(l) for l in (out/'candidates.jsonl').read_text().splitlines()];old=[json.loads(l) for l in (root/'build/practical-audit-reproduced/decisions.jsonl').read_text().splitlines()]
selected={}
for x in old:
 if x['state']=='confirmed':selected[x['surfaceKey']]=x['approvedMetadata']
 elif x['state']=='rejected-this-selection':
  o=x['records'][0]['original']
  if o['wordfreqZipfPl']>=1:selected[x['surfaceKey']]=o['metadataProposal']
assert len(selected)==1758
for x in rows:
 if not x['inPreviousPool'] and x['status']=='lexically-confirmed-frequency-positive':selected[x['surfaceKey']]=x['metadataProposal']
assert len(selected)==3138
base=Path(sys.argv[1]);raw=base.read_bytes();assert hashlib.sha256(raw).hexdigest()==r['baseSha256']
with zipfile.ZipFile(base) as z:doc=json.loads(z.read('language-intelligence.json'))
before=serialize(doc);original=deepcopy(doc);doc['entries']=sorted(doc['entries']+list(selected.values()),key=lambda e:e['surfaceKey']);assert len({e['surfaceKey'] for e in doc['entries']})==len(doc['entries']);new=serialize(doc)
cost=dict(scenario='1336 previous confirmed + 422 lower-frequency previous + 1380 new lexical positive',entries=len(selected),bytes=len(new)-len(before),nodes=nodes(doc)-nodes(original),remainingEntries=120000-len(doc['entries']),remainingBytes=33554432-len(new),remainingNodes=2000000-nodes(doc),includesNewProvenance=False,approved=False)
(out/'scenario-cost.json').write_text(json.dumps(cost,ensure_ascii=False,indent=2)+'\n')
names={'communication':'Komunikacja i słownictwo ogólne','digital':'Telefon, internet i aplikacje','home':'Dom i codzienność','work':'Praca, dokumenty, ekonomia i prawo','roads':'Drogi, transport i budownictwo'}
text='''# Wspólny nabór pięciu modułów — 14.10.2026

Bazą pozostaje v11. V12 jest odłożona. To raport kandydatur, nie langpack.

Przejrzano 26 zapisanych indeksów Wikisłownika, listy repozytorium, wcześniejsze zestawienie aplikacji oraz dosłownie zapisane formy z uzupełnienia źródłowego. Indeksy stanowią szerokie źródło naboru, nie dowód przydatności. Nie generowano pełnych paradygmatów odmiany.

## Wynik

15420 unikalnych kluczy źródłowych; 7060 już w v11; 6270 brakujących pojedynczych kluczy w tym naborze; 2090 pozostałych zapisów (frazy/interpunkcja) osobno.
Z 6270 kluczy 1618 nakłada się na wcześniejszą pulę. Nowych jest **4652**.
Poprzednia pula 2913 + pięć wcześniej rozpoznanych braków = 2918; po połączeniu **7570** pojedynczych kandydatur. Wszystkie 911 wcześniej odsianych słów nadal w tej puli. Nie porównywano prywatnego słownika.

| Obszar źródeł | Braki względem v11 | Dodatkowe ponad wcześniejszą pulę | SGJP i Zipf ≥1 w dodatkach |
|---|---:|---:|---:|
'''
for m,n in names.items():
 s=r['modules'][m];text+=f"| {n} | {s['newSingleKeys']} | {s['additionalSingleKeys']} | {s['status'].get('lexically-confirmed-frequency-positive',0)} |\n"
text+='''
Grupy się nakładają: nie sumować wierszy tabeli. Klucz to NFC i małe litery zgodnie z dotychczasowym porównaniem; pisownia źródłowa pozostaje osobno. Nie usuwano łączników i nie dzielono fraz.

## Jakość 4652 dodatków

- 1380: dokładny dowód analyse/generate SGJP, odczyt pospolity zgodny z dotychczasowymi filtrami, pisownia małymi literami potwierdzona w źródle, Zipf ≥1. To potwierdzenie leksykalne, nie zatwierdzenie użyteczności każdego słowa.
- 1807: analogiczny dowód leksykalny, ale wynik częstości poniżej 1. Brak mierzalnej częstości nie dowodzi zbędności.
- 1465: potrzebna dalsza ocena pisowni, kapitalizacji, tożsamości lub dowodu odmiany. Część ma wcześniejsze potwierdzenia z innych słowników; brak SGJP nie oznacza błędu.

Przykłady pierwszej grupy: jednorazówka, wywiadówka, włoszczyzna, chałka, łazanki, mascarpone, cienkopis, niewypłacalny, gotówkowy, wadium, niwelacja, wtryskiwacz, grywalny, grywalność. Szeroki nabór zawiera też np. terminy architektoniczne i waluty — samo przejście progu nie uzasadnia ich priorytetu.

## Koszt

'''
text+=f"Całe 7570 kandydatur przekracza wolne 5701 miejsc v11 o {7570-5701}. Nie zastosowano limitu do naboru ani go nie podnoszono.\n\nScenariusz roboczy: 1336 wcześniej potwierdzonych + 422 po obniżeniu progu + 1380 nowych = **3138 wpisów**. Rzeczywista serializacja metadanych w pamięci: **{cost['bytes']} dodatkowych bajtów**, **{cost['nodes']} elementów JSON**. Pozostaje **{cost['remainingEntries']} miejsc**, **{cost['remainingNodes']} elementów JSON**, **{cost['remainingBytes']} bajtów**. Nie uwzględnia nowego opisu pochodzenia etapu. Nie jest to wybór do instalacji ani pomiar RAM.\n\n"
text+='''Dla wszystkich 3187 nowych kandydatur z dowodem SGJP suma samych propozycji wpisów wynosi 587726 bajtów i 35638 elementów JSON (bez opisu etapu i separatorów). Koszt całej puli pozostaje nieznany, gdy brak gotowych metadanych.

## Ograniczenia i odtwarzanie

To pełny przegląd wskazanego, zamrożonego zestawu źródeł we wszystkich pięciu obszarach, nie komplet polskiego słownictwa ani wszystkich odmian. Praca i drogi mają szeroki zakres źródeł; przypisanie modułu nie jest oceną znaczenia. Listy repozytorium nie zastępują niezależnego źródła. Dane aplikacji i wcześniejsze obserwacje zachowano z ich poprzednią datą — nie przedstawiamy ich jako ponownie zweryfikowanych.

Każdy rekord zachowuje pisownię, źródła, moduły, obecność w v11, nakładanie na poprzednią pulę, wynik wordfreq, dowód SGJP i ewentualną propozycję metadanych. Pochodzenie i wersje w report.json; dokładne odpowiedzi API i ich sumy w sources/lock.json. Morfeusz2 1.99.15, SGJP 2026.06.01 i wordfreq 3.2.0 z przypiętego commitu jak w poprzednim audycie.

Uruchom scripts/audit_five_modules.py --base /ścieżka/do/v11.zip --out build/five-modules bez --fetch, aby użyć zamrożonych źródeł. Wymagane skrypty repozytorium i build/practical-audit-reproduced/decisions.jsonl (w paczce). Następnie scripts/report_five_modules.py /ścieżka/do/v11.zip. Opcja --fetch służy nowemu naborowi, nie odtwarzaniu starego.

Nie wykonano ponownie historycznych 97 testów. Nowe sprawdzenia obejmują sumę v11, strukturę słownika, wersje źródeł, wszystkie 26 sum snapshotów, dowody SGJP dla brakujących pojedynczych kluczy i brak duplikatów w symulacji metadanych. Nie powstał APK ani pakiet do importu.
'''
(out/'RAPORT.md').write_text(text);print(json.dumps(cost,indent=2))
