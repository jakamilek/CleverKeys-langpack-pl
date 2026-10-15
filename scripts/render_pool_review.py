#!/usr/bin/env python3
"""Report a source review; simulate metadata costs without making a langpack."""
import json,sys,zipfile,hashlib
from pathlib import Path
from collections import Counter
from copy import deepcopy
from build_shared_metadata_trial import serialize
from shared_metadata_v2 import nodes
root=Path(__file__).resolve().parents[1];out=root/'build/pool-review';rows=[json.loads(l) for l in (out/'review.jsonl').read_text().splitlines()];r=json.loads((out/'report.json').read_text());base=Path(sys.argv[1]);assert hashlib.sha256(base.read_bytes()).hexdigest()==r['baseSha256']
with zipfile.ZipFile(base) as z:original=json.loads(z.read('language-intelligence.json'))
working=[x for x in rows if x['status'] in {'meets-original-frequency-policy','lower-frequency-working-pool'}];doc=deepcopy(original);doc['entries']=sorted(doc['entries']+[x['metadataProposal'] for x in working],key=lambda x:x['surfaceKey']);assert len({x['surfaceKey'] for x in doc['entries']})==len(doc['entries']);cost=dict(entries=len(working),bytes=len(serialize(doc))-len(serialize(original)),nodes=nodes(doc)-nodes(original),remainingEntries=120000-len(doc['entries']),remainingBytes=33554432-len(serialize(doc)),remainingNodes=2000000-nodes(doc),includesNewStageProvenance=False,approved=False)
(out/'scenario-cost.json').write_text(json.dumps(cost,indent=2)+'\n')
labels={
'meets-original-frequency-policy':'Dowód SGJP i pierwotne reguły częstości',
'lower-frequency-working-pool':'Dowód SGJP i obniżony próg Zipf ≥1',
'lexical-proof-frequency-unresolved':'Dowód SGJP, ale częstość poniżej progu',
'name-or-brand-needs-identity-review':'Nazwy, marki i skrótowce: ocena tożsamości i pisowni',
'source-capitalization-needs-review':'Rozbieżność kapitalizacji źródłowej',
'excluded-by-lexical-profile':'Poza profilem SGJP: nazwy własne, dawne/regionalne odczytania lub skróty',
'external-source-supported-needs-metadata':'Wcześniejsze dowody zewnętrzne: potrzebne mapowanie metadanych',
'polish-dictionary-entry-needs-morphology-and-usage':'Polskie hasło słownikowe; dalsza kontrola odmiany i przydatności',
'dictionary-entry-flagged-for-verification':'Hasło z ostrzeżeniem redakcyjnym',
'redirect-needs-target-review':'Przekierowanie wymagające sprawdzenia celu',
'page-without-parsed-polish-definition':'Strona bez rozpoznanej polskiej definicji',
'no-lexical-proof-yet':'Dotąd brak wystarczającego dowodu leksykalnego'}
text='''# Ocena wspólnej puli kandydatów — 15.10.2026

V11 pozostaje bez zmian; nie zbudowano nowego langpacka ani APK. Oceniono całą pulę 7570 kluczy, z zachowaniem wcześniejszych 911 kandydatur o niskiej częstości. Nie odrzucano kandydatów z powodu limitu miejsca.

## Wyniki

| Wynik automatycznej oceny | Liczba |
|---|---:|
'''
for state,label in labels.items():text+=f"| {label} | {r['statusCounts'].get(state,0)} |\n"
text+='''
Kategorie są rozłączne i sumują się do 7570. „Poza profilem” nie oznacza błędnego słowa: może chodzić o historyczne znaczenie, nazwę lub regionalizm. Brak częstości nie dowodzi zbędności. Żadna nowa kandydatura nie została zatwierdzona do instalacji.

## Co sprawdzono źródłowo

'''
text+=f"Pobrano **2138 zapisów haseł** z Wikisłownika dla kandydatur bez zgodnego nowoczesnego odczytania SGJP. Znormalizowanych odpowiedzi o stronach: {r['pages']['total']}; polską sekcję z numerowaną definicją rozpoznano w {r['pages']['withPolishDefinitions']}; brakujących stron: {r['pages']['missing']}; przekierowań: {r['pages']['redirects']}. To liczby stron, nie dodatkowych słów.\n\n"
text+='''Zapisano surowe odpowiedzi, rewizje i sumy SHA-256. Parser rozdziela języki, definicje, ostrzeżenia redakcyjne, kwalifikatory, przykłady i dosłowne komórki tabel odmiany. Przykłady i przypisy są wskaźnikami do dalszej kontroli — ich treści i przywołanych publikacji nie uznajemy automatycznie za niezależnie sprawdzone.

Dla słów z dowodem SGJP ponownie oceniono zapisane odczytania i kwalifikatory oraz powiązanie z częstymi formami tej samej rodziny w v11. Zachowano klucz kotwicy i częstość. Nie korzystano z modelowej oceny znaczeń jako dowodu.

## Korekta kwalifikatorów

Dotychczasowy filtr sprawdzał początek etykiety, przez co mógł przeoczyć kwalifikator po przecinku. Nowy filtr rozdziela składniki. Dotyczy to kandydatur: '''+', '.join(r['compoundObsoleteFilterChanged'])+'''. Trzy z nich miały Zipf ≥1, jedna wynik poniżej progu. To przesunięcie do kontroli profilu, nie stwierdzenie błędu pisowni. Wcześniejsza grupa 1336 potwierdzonych form nie utraciła potwierdzenia z tego powodu.

## Scenariusz roboczy i koszt

'''
text+=f"Łącznie **{cost['entries']} kandydatur** ma zgodne odczytanie SGJP, źródłową pisownię i Zipf ≥1 (z zachowaniem wcześniejszych reguł rodzin). W porównaniu z wczorajszym scenariuszem 3138 to trzy pozycje mniej. Dokładny koszt dopisania ich metadanych w pamięci: **{cost['bytes']} bajtów**, **{cost['nodes']} elementów JSON**. Pozostaje **{cost['remainingEntries']} miejsc**, **{cost['remainingNodes']} elementów JSON**, **{cost['remainingBytes']} bajtów**. Koszt nie obejmuje nowego opisu pochodzenia etapu; nie jest pomiarem RAM telefonu. Nie zapisano paczki instalacyjnej.\n\n"
text+='''Zachowano też wcześniejsze obserwacje WSJP, Dobrego słownika, Obserwatorium Językowego UW i stron producentów; brak nowego hasła w Wikisłowniku nie kasuje tych dowodów. Te obserwacje nie zostały dziś ponownie pobrane.

Ta grupa nie jest automatyczną rekomendacją wszystkich słów. Częstość dotyczy zapisu, a nie zawsze konkretnego znaczenia. Kwalifikatory potoczne, żartobliwe, pejoratywne i wulgarne zachowano do oceny, bez automatycznego usuwania. W grupie roboczej 22 klucze mają co najmniej jedno odczytanie z etykietą wulg.; to wyodrębniona kwestia polityki podpowiedzi, a nie powód ukrytego odrzucania danych.

## Dalsza kolejność

Najpierw rozstrzygamy hasła już wsparte definicją lub zewnętrzną obserwacją źródłową, ale bez mapowania metadanych; następnie słowa o niskiej częstości należące do częstych rodzin. Przekierowania, redakcyjne ostrzeżenia i sprzeczność profili pozostają osobnymi kolejkami. Nie potrzeba ręcznego przeglądu całej listy przez użytkownika.

Nie utożsamiać obecności w Wikisłowniku z potwierdzoną współczesną przydatnością. Hasło może być regionalne lub historyczne. Brak polskiej sekcji może oznaczać brak opracowania, nie błąd zapisu. Nie sprawdzono na nowo wszystkich witryn producentów aplikacji ani korpusowej częstości znaczeń.

## Odtwarzanie i weryfikacja

Repozytorium CleverKeys-langpack-pl, gałąź audit/practical-candidates-v11. scripts/review_candidate_pool.py --base /ścieżka/v11.zip --out build/pool-review używa zamrożonych stron; --fetch pobiera brakujące partie. Następnie scripts/render_pool_review.py /ścieżka/v11.zip. Wersja wordfreq i commit są kontrolowane; ścieżki wejść i sumy znajdują się w report.json. Odczytania SGJP pochodzą z wcześniejszego przypiętego audytu, a nie z nowego pobrania słownika.

Sprawdzono na rzeczywistych snapshotach cztery istotne zachowania parsera: niemieckie ADAC nie staje się polskim hasłem; abandonware ma polską definicję; ajlauf zachowuje ostrzeżenie do weryfikacji; abwera zachowuje dosłowną formę abwery w dopełniaczu. Walidacja bazy i symulacji sprawdza sumę v11 oraz unikalność kluczy. Historycznych 97 testów nie uruchamiano ponownie.

Snapshoty Wikisłownika: CC BY-SA; rewizje i odnośniki do historii autorstwa wskazują dictionary-pages/lock.json oraz rekordy dictionaryPages. Prywatny słownik nie był wejściem analizy.
'''
(out/'RAPORT.md').write_text(text)
for state in labels:
 (out/(state+'.txt')).write_text(''.join(x['surfaceKey']+'\n' for x in rows if x['status']==state))
print(json.dumps(cost,indent=2))
