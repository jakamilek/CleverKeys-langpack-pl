# Kamień milowy: naprawa ładowania MLM v3 i nowa próba
Data weryfikacji: 2026-10-06, Europe/Warsaw.

## 1. Repozytoria
Main przed zapisem: CleverKeys-langpack-pl 25c848cba824dda06bb29598b312f202c2411eea;
CleverKeysPL 60c933831aa6cb2264ff1834329d8dc5aa6b5b7c.
Dokument identyczny na obu main, docs-only. Kod na izolowanej gałęzi.

## 2. Architektura
Geometric dekoduje. Źródłowy klucz słownika ma warianty/default/metadata.
SI w Androidzie nadal osobny benchmark, live ranking off. Default32/max64/4096UTF16.
Poprawka dotyczy hostowego testu oryginalnych MLM; nie Androida ani słownika.

## 3. Zaakceptowane ustalenia
Użytkownik autoryzował naprawę kontroli ładowania i nowe porównanie.
Naprawa słownika ODŁOŻONA, obowiązek powrotu zachowany:
9 form dodam/grzeje/kasami/nawilżane/odpowiadam/patrzysz/poczekaj/podpowie/pozdrawiam.
Nie zmieniać danych/gold/metody i kryteriów jakości po zobaczeniu wyników.
Licencja modeli nadal odłożona przez użytkownika. Brak decyzji produkcyjnej.

## 4. Odrzucone rozwiązania
Brak blanket ignore unexpected keys, brak dopuszczenia braków MLM.
Nie mieszać starego distil wyniku z nową referencją. Nie przepisywać v3 historii.
DistilRoBERTa unknown Ł i poprzedni HerBERT INT8 FAIL nadal odrzucone.
Geotrend v2 screen FAIL, distilHerBERT v2 mixed; nie production approval.

## 5. Wdrożone i planowane
Nowy wspólny loading.py używany przez runner i collector.
HerBERT wymaga dokładnie 4 znanych nieużywanych kluczy oryginalnego checkpointu:
bert.pooler.dense.bias/weight, cls.sso.sso_relationship.bias/weight.
DistilHerBERT wymaga 0. Missing/mismatched/error, nieznane/niepełne/zdublowane
klucze i brak/list-type błędny loading_info nadal FAIL.
Oryginalne MLM/encoder, pinned revision/config, hashe wag, tokenizer i
3 full-forward parity checks pozostają wymagane.
Plan: po zakończeniu runa zweryfikować oba pełne wyniki i przeliczyć collector;
następnie warunkowo ONNX FP32 i pomiar Nubii, INT8 po zgodnym FP32.

## 6. Weryfikacja
30 testów lokalnych PASS: v1 11, v2 8, poprawione v3 11 (3 nowe testy bramek).
AST wszystkich 9 skryptów v3 PASS. Oryginalne frozen dependencies SHA zweryfikowane.
128 cases/256 requests, request SHA identyczny:
a20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d.
Case/source/tokenizer/scoring/projection/contract danych bez zmian;
quality screening w collectorze bez zmian.
Wszystkie 8 zmienionych/dodanych plików exact readback z GitHub na nowym commit.
Nie wykonano lokalnie inferencji modeli. Bieżące actual inference/quality pending CI.
Testowe synthetic scores sprawdzają kontrakty, nie stanowią jakości modeli.

## 7. Gałęzie i historia
Nowa experiment/polish-mlm-v3-loading-fix-v1:
83fa31fd6071ba48b8e7828c58bb28ff2d49f2f1.
Draft PR11 base experiment/polish-mlm-fresh-v3:
https://github.com/jakamilek/CleverKeys-langpack-pl/pull/11
Historyczny kod v3 c1e9d3a7895f2a380bc75772985c88a53db32a4b, PR10,
run37363474711 zachowany: distil SUCCESS, HerBERT loading gate FAILURE,
comparison FAILURE. Nie jest to wynik jakości HerBERT.
V2 raw results a729fd780241a581f9cac153c0a6d926d8bfa1c1.
Runtime APK kod db88fd28cca21ba2aa1e99b38e3886f1f147b5d6 bez zmian.

## 8. Artefakty i integracja
Nowy frozen manifest executionRevision=loading-fix-v1, previousRunId=37363474711,
previousFrozenCodeCommit=c1e9d3a7895f2a380bc75772985c88a53db32a4b.
SHA256 pliku freeze-manifest.json:
1ad6fba137949fcc2d6a87ef83ecf19cc8d2404d6efcfa83f0c2cfe07c8cdc4c.
Protocol ID v3 opisuje identyczne requests; commit/manifest identyfikują wykonanie.
Nowy push run37500235605, head83fa31..., ostatni odczyt QUEUED:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37500235605
Workflow polish-mlm-fresh-v3.yml. Inference tylko push/manual; PR tylko kontrakty.
Nowe artefakty prefix polish-mlm-fresh-v3-loading-fix-v1-16-32-*.
Wyniki zawierają raporty/predictions/validation/environment, bez wag.
Brak nowego APK/export/live SI. Nie scalono PR.

## 9. Ograniczenia
V3 to autorskie konteksty po odczycie v2, nie zewnętrzny/humanblind benchmark.
Top3 dwóch form nasycone z konstrukcji, nie dowód poprawy SI.
Dłuższe świeże teksty21–26 słów, brak testu >32 oraz reprezentatywnych rozmów.
Host koszty nie są pomiarem PSS/energii/latencji telefonu.
HerBERT FP32 PSS >2GiB jest przeszkodą; distil Android PSS jeszcze nieznany.
Nie ma wyboru modelu do produkcji/default16 ani osłabienia bramek jakości.

## 10. Następny krok
Użytkownik podaje zakończenie run37500235605. Odczytać artefakty, identities i
przeliczyć collector, osobno 4 fresh strata, historical64 i 16/32 window pairs.
Jeżeli screen FAIL, zachować wynik i omówić przyczynę, nie luzować bramek.
Monitoring <=60s TOTAL/run, nie czekać do końca.
Słownik i 3 ustawienia czasów stacjonarnego BS nadal backlog.

## 11. Różnica od poprzedniego kamienia
PROJECT_MILESTONE_2026-10-06_AI_PRIORITY_DICTIONARY_DEFERRED.md
przywrócił priorytet SI i zaplanował naprawę.
Teraz poprawka zapisana/zweryfikowana w nowym frozen commit, 30 testów PASS,
draft PR11 oraz nowy run z tymi samymi requests. Wyniki jakości nadal pending.
Checkpoint exact readback w obu repo. Bez merge/release/tag/version bump.
Polski UI priorytet, inne locale backlog. Bez subagentów.
