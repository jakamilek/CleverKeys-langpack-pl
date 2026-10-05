# Kamień milowy: ponowienie próby MLM v3 — attempt 2
Data weryfikacji: 2026-10-05 (Europe/Warsaw). Attempt 2 przyjęty i queued; brak wyników jakości v3.

## 1. Zweryfikowane repozytoria i zakres
Main przed tym dokumentem: CleverKeysPL 8560c4c119b8d163d0bcab655689e747024e3959;
CleverKeys-langpack-pl 2d785a9aa478e324e69a42c1586548dea1fd78e5.
GitHub API sprawdzone. Ten sam dokument docs-only na obu main, bez zmiany kodu.
Producer experiment/polish-mlm-fresh-v3 kod c1e9d3a7895f2a380bc75772985c88a53db32a4b,
runtime docs trial/herbert-fp32-benchmark-v1 0367b334f770d4ad2b1925dc445850e9c19e9b78.

## 2. Architektura
Geometric dekoduje; jeden klucz ma źródłowo poświadczone formy/default/atrybuty.
Live SI off; default32/max64/4096UTF16 bez zmian. Brak nowego APK/model bundle.
Obie formy dostępne, Shift/sentence capitalization/ręczny wybór mają priorytet.

## 3. Zaakceptowane ustalenia
Licencja odłożona na wyraźną prośbę użytkownika, bez domniemania licencji wag.
V3 dane/metoda/bramki pozostają zamrożone. Nie zmieniać ich z powodu problemu runnerów.
Zielony PR run nie jest wynikiem inferencji; cancelled model job nie jest jakością FAIL.

## 4. Rozwiązania odrzucone i rezerwowe
V1 DistilRoBERTa unknown Ł nadal odrzucona; V2 Geotrend jakościowy screen FAIL.
distilHerBERT V2 wynik mieszany, HerBERT referencja; wcześniejszy INT8 FAIL niezmieniony.
Geotrend BERT12/ORIS rezerwa. CTC poza zakresem. Nie usuwać trudnych przypadków.

## 5. Wdrożone i niewdrożone
V3:64 świeże autorskie cases +64 dokładne historyczne forms,256requests/model.
8 znanych/8 nowych kluczy z fullv5, short4–6/long21–26 słów, lower/upper zbalansowane.
Oryginalny v1 WWM/fullvocab meanlogp, oba pinned oryginalne BERT MLM rerun.
27 lokalnych testów, tokenizer preflight distil256/512 PASS; pełne native scoring nie wykonane.
Nie wdrożono eksportu/kwantyzacji/telefon/liveSI/interpunkcji/nowych opcji czasów Backspace.

## 6. Stan zweryfikowany przez API
PR run37363478784 COMPLETED SUCCESS:
contract111943232127 SUCCESS; inference111946708994 i comparison111946709916 SKIPPED
zgodnie z workflow github.event_name != pull_request.
Attempt 1 run37363474711 zakończył się COMPLETED FAILURE:
contract111943219961 SUCCESS;
inference distil111943371793 i herbert111943371827 COMPLETED CANCELLED,
oba zakończone 2026-10-05T19:42:39Z, steps=[], runner_id=0, runner_name pusty.
Comparison111948399235 zakończony FAILURE: log19:48:01UTC,
ValueError: one complete result required: herbert. Poprawnie odmówił porównania brakujących wyników.
Artifact API attempt1: pusta lista. Żaden model nie otrzymał runnera/nie wykonał kroku.
Brak report/predictions; nie można oceniać jakości/RAM/latencji v3.
Na polecenie użytkownika ponowiono nieudane zadania przez rerun-failed-jobs.
API potwierdziło attempt2 QUEUED, ten sam kod c1e9d3a7895f2a380bc75772985c88a53db32a4b.
Nowe inference distil111950695899 i herbert111950696064 QUEUED.
Udany contract widoczny jako SUCCESS111950697565. Porównanie ma zależność od obu modeli.
Rerun response success=true; nie deklarować inferencji rozpoczętej lub jakości PASS.

## 7. Gałęzie i historia
Draft PR10 v3 baza experiment/polish-mlm-16-32-v2, bez merge.
V2 run37359525824 SUCCESS, producer raw results a729fd780241a581f9cac153c0a6d926d8bfa1c1;
V1 run37355290211 FAILURE, HerBERT pełny i odrzucona DistilRoBERTa.
Poprzedni checkpoint docs/PROJECT_MILESTONE_2026-10-05_FRESH_CASE_MLM_V3.md.
Zaakceptowany APK db88fd28cca21ba2aa1e99b38e3886f1f147b5d6 niezmieniony.

## 8. Źródła i tożsamość
Frozen protocol:
https://github.com/jakamilek/CleverKeys-langpack-pl/blob/c1e9d3a7895f2a380bc75772985c88a53db32a4b/experiments/polish_mlm_fresh_v3/PROTOCOL.md
Requests SHAa20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d.
HerBERT rev50e33e0567be0c0b313832314c586e3df0dc2297;
distilHerBERT rev7276461b7a8fd668aaf30313c03a68bd11aad642.
Źródłowy fullv5 pack SHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb.
Oficjalny https://www.githubstatus.com/ 2026-10-05 zgłasza Actions Degraded Performance,
od19:11UTC; update19:15UTC mówi o opóźnieniach przydzielania hosted runners.
To pasuje do pustych runnerów. Dokładnej przyczyny anulowania tych dwóch jobs API nie podało;
nie twierdzić, że globalny incydent jest udowodnioną bezpośrednią przyczyną cancellation.

## 9. Ograniczenia
Nowe autorskie gold nie jest zewnętrznym niezależnym/humanblind benchmarkiem.
Top3 par strukturalnie nasycone bezSI, potrzebny top1 i osobne regresje.
Fresh strata i stare64 mają osobne zamrożone exploratory gates; nie statystyczne wdrożenie.
Host RSS nie jest AndroidPSS; HerBERT phone load2121/max2132.1MiB pozostaje dowodem.
Brak native model wyników v3, brak testu >32 słów/prywatnych rozmów.

## 10. Następny uzasadniony krok
Retry wykonany: attempt2 tego samego runu i frozen commitu; nie powielono udanego PR.
Po informacji użytkownika o zakończeniu sprawdzić oba nowe model jobs i pełny collector.
Nie dodawać kolejnych retry podczas oczekiwania; nie zmieniono danych/metody/bramek.
Nie czekać/watch/sleep: <=60s TOTAL monitorowania/run, następny odczyt po wiadomości użytkownika.
Dopiero complete wyniki: artifact SHA/size, dokładne collector recomputation, all regressions,
ocena16/32; następnie uzasadniony export/nativefixtures/telefon. Licencja dalej deferred.

## 11. Różnica wobec poprzedniego stanu
Poprzedni docs/PROJECT_MILESTONE_2026-10-05_FRESH_MLM_V3_RUNNER_INTERRUPTION.md:
oba model jobs cancelled, comparison queued. Teraz attempt1 comparisonFAIL z powodu
braku wyników, retry przyjęty i attempt2 queued z nowymi model jobs.
Dalsze informacje poniżej opisują historyczną zmianę wobec pierwotnego launch:
Poprzednio v3 runy queued i jakość pending. Teraz PR contract SUCCESS z expected skips;
główne oba model jobs anulowane bez runnera/kroków, comparison jeszcze queued, artifacts brak.
Dane/kod/metoda/model revisions niezmienione. To przeszkoda wykonania, nie regresja algorytmu.
Dokument identyczny na obu main, exact readback wymagany. Brak merge/tag/release/model APK.
Polski UI priorytet; inne locale backlog; bez subagentów; Gemini/PAL wymóg uchylony.
