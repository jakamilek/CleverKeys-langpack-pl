# Kamień milowy: ostrożny ranking v4 zamrożony przed walidacją
Data: 2026-10-06, Europe/Warsaw.

## 1. Repozytoria
Main przed zapisem: CleverKeys-langpack-pl 2115ec406692d76657772198fefde51245400a53;
CleverKeysPL ac4411fd027af2230387a00978b5660ecd49e5a9.
Dokument identyczny na obu main, docs-only. Kod wyłącznie na nowej gałęzi.

## 2. Architektura
Geometric i źródłowe warianty/default/metadata polskiego packa bez zmian.
Android SI nadal osobny benchmark, live ranking off, default32/max64/4096UTF16.
V4 to hostowy test ostrożnego rankingu dwóch form jednego źródłowego klucza.
Globalna przewaga mean-logp alternatywy nad defaultem >=progu i >0 zmienia kolejność;
inaczej default zostaje. Obie formy pozostają. Bez wyjątków dla poszczególnych słów.
Przewaga nie jest kalibrowanym prawdopodobieństwem ani procentową pewnością.

## 3. Zaakceptowane
Użytkownik autoryzował sprawdzenie ostrożnego rankingu na osobnym zestawie.
Naprawa słownika ODŁOŻONA, obowiązek późniejszego powrotu zachowany.
Dotyczy9 brakujących form swipe: dodam/grzeje/kasami/nawilżane/odpowiadam/patrzysz/
poczekaj/podpowie/pozdrawiam. Nie poprawiono ich tutaj.
Licencja odłożona na prośbę użytkownika; nie jest to grant ani założenie licencji.

## 4. Odrzucone
Nie zmieniać progów/gold po holdout. Nie poprawiać rankingu wyjątkami per-word.
Nie traktować niezmieniania niczego jako sukcesu. Nie udawać niezależnego humanblind.
Nie anulować jakościowego FAIL v3: historical rawdistil46vsHerBERT50, próg49.
V4 ma nowy jawny cel bezpieczeństwa, nie zastępuje tamtej bramki.
HerBERT INT8 wcześniejszy FAIL, DistilRoBERTa unknownŁ, Geotrend v2 screenFAIL
pozostają. Nie utożsamiać host RSS z Android PSS.

## 5. Wykonane i plan
policy.py/calibrate.py: przed kalibracją siatka0/.25/.5/1/2/3/4/6/8/abstain-all,
cel repairs−4*regressions; tie mniej regresji, mniej zmian, większy próg.
Development tylko archived v3256 requests obu okien. Wynik globalny próg0.25
wybrany PRZED napisaniem nowych kontekstów i PRZED ich inferencją.
Development raw216/256 repairs96/regressions8; gated214/256 repairs90/regressions4.
Te liczby dotyczą correlated window requests, nie nowej walidacji.
calibration.json i freeze wiążą wejścia SHA, próg odtwarzany przez kontrakt.
64 nowe konteksty+64 jawne development replay, dwa okna i oba modele.
Plan po wynikach: zweryfikować artefakty/recompute i omówić tradeoff
mniej błędnych nadpisań vs pominięte trafne poprawki. Nie decydować o produkcji.

## 6. Walidacja i niewiadome
45 local tests PASS: v1 11/v2 8/v3 11/v4 15; AST PASS.
20 nowych plików/workflow zweryfikowane Git blob SHA na nowym tree.
Original runner/scoring/projection/loading/requirements bajtowo jak corrected v3.
Request SHA84ec2282a35f0e96b4020c42c6e9bca8376b00b712d7653adf2148f4541a3f60.
128 cases/256 requests/model, nowe64 w4 grupach16, każda8 lower/8 upper.
Nowe teksty rozłączne z v1/v2/v3. Wszystkie16 kluczy były w development:
holdout kontekstów, NIE holdout słów; known/new_key odnosi się do v1 natural.
Nowe konteksty autorskie po development, bez zewnętrznego anotatora.
Stare64 tylko development replay, oznaczone populationRoles; nie kwalifikują v4.
Actual tokenizer preflight nowych tekstów przed wagami w CI, lokalnie nie wykonany.
Nie użyto starego preflight v3 jako dowodu. Model/forward-parity/quality PENDING.

## 7. Gałęzie
Nowa experiment/polish-mlm-safe-rank-v4 commit7d7d3ec4f7be31476df11f198dfcc2b21d813e5b.
DraftPR12 baza experiment/polish-mlm-v3-loading-fix-v1:
https://github.com/jakamilek/CleverKeys-langpack-pl/pull/12
Base archive b2c3342643a77ef01a04323034465acae8609c27.
V3 frozen executable83fa31fd6071ba48b8e7828c58bb28ff2d49f2f1/run37500235605
technicznieSUCCESS, qualityFAIL. Rawresults zachowane.
Historyczny failed v3 c1e9d3.../run37363474711 nieprzepisany.
Runtime APK code db88fd28cca21ba2aa1e99b38e3886f1f147b5d6 bez zmian.

## 8. Artefakty i wykonanie
V4 katalog experiments/polish_mlm_safe_rank_v4, workflow polish-mlm-safe-rank-v4.yml.
Freeze file SHA256 5c16b760927e70d89131a0d2a10a5c5d6bce90d9ac9985f09a68d5afc5705a07.
Push run37502851581, frozen head7d7d3ec4f7be31476df11f198dfcc2b21d813e5b, ostatni odczyt IN_PROGRESS.
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37502851581
Nie monitorowano do zakończenia. PR wykonuje tylko kontrakty.
Artifact prefix polish-mlm-safe-rank-v4-16-32-*, wynik bez wag.
Inference tylko push/manual, PR tylko kontrakty. Bez APK/export/live SI.
Poprzednie authenticatedZIP source/SHAs w checkpoint MLM_V3_VERIFIED_RESULTS.
Kalibracja wiąże rawdistil predictionsSHA
72a31bd85cb4a071941ea16b31c13c36cf21d55fb9e2a5f473749b973fbda923
oraz reportSHA3ee69596a2e547e52cbcfa1cfc9e142d91d61c6c66fdf80a9eeb175a74cf4e4b.

## 9. Kryteria i ograniczenia
Nowy wstępny safety screen primary nowe64/window16 wymaga łącznie:
regresje default<=2 i <=raw, utility>=raw, top1>baseline,
overrides>=8, każda4grupa top1>=baseline i regresje<=1.
Okno32/rawHerBERT/replay opisowe, bez wyboru progu/okna po holdout.
Stary historical rawdistil>=HerBERT-1 nadal osobno raportowany jako development gate.
PASS v4 nie jest produkcyjnym zatwierdzeniem ani anulowaniem v3FAIL.
Top3 par nasycone bezSI. Brak interpunkcji/multi-key replays/default16 decision.
Host koszty nie dowodzą telefonu; phone distilPSS/energy/latency nieznane.
FP32 HerBERT phone >2GiB całoprocesowegoPSS nadal przeszkodą.

## 10. Następny krok
Po zakończeniu runa odczytać artefakty/provenance, przeliczyć obie raw i gated reports,
ocenić primary64 niezależnie od development replay i raportować wszystkie
regresje/naprawy/pominięte poprawki. Nie dostrajać progu na holdout.
Monitoring<=60s TOTAL/run; użytkownik podaje zakończenie.
Słownik,3 czasy stacjonarnegoBS i inne locale backlog.
Bez merge/release/tag/version bump, bez nowych wag.

## 11. Różnica od poprzedniego zapisu
PROJECT_MILESTONE_2026-10-06_MLM_V3_VERIFIED_RESULTS.md opisał mixed v3 quality.
Teraz nowa autoryzowana metoda abstention, jawna kalibracja development,
nowe64 konteksty oraz osobne frozen kryterium ryzyka. Model/scoring niezmienione.
Brak wyniku nowej jakości; dotychczasowe FAIL nieprzemianowane.
Dokument exact readback na obu main, kod na isolated draftPR12.
