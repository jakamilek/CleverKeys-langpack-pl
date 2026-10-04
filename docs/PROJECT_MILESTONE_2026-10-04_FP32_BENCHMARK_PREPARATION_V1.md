# Kamień milowy — przygotowanie benchmarku FP32 i Androida v1

Data: 2026-10-04. Poprzedni Android PASS; nowa paczka/Android CI przy jedynym odczycie trwały. Import trust unset, bez nowego APK i bez live SI.

## 1. Zweryfikowany stan repozytoriów

Main przed tym zapisem: langpack 4f4ff2fd618ab8a5da83594eafdd78f6a414efd8; runtime 08d56bf8ae1b769cb79b40b29104b7656977fe92. Main otrzymuje wyłącznie ten dokument. Poprzedni checkpoint PROJECT_MILESTONE_2026-10-04_HERBERT_MOBILE_V1.md.

Producer experiment/herbert-fp32-benchmark-v1: d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, tree 8e99d860ce8a23d56dc4a9c672d4ed19b6793ab2; parent 1fb12ad350a8091e84edb561b0422d6f891b8c25. [Draft PR #7](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/7), base experiment/herbert-mobile-v1. Osiem nowych plików; wszystkie Git blob SHA porównano z lokalną treścią.

Runtime trial/herbert-fp32-benchmark-v1: 63524ecda63cbbfebc39392a8826f28b0690a0d1, tree 0de9397fc27f3c20eec1112bae40307301ce0aa3; parent b1c829cf28886391cdc98a7b8d7b0bd16bf6b65e. [Draft PR #3](https://github.com/jakamilek/CleverKeysPL/pull/3), base trial/herbert-mobile-preparation-v1. Dwadzieścia plików; wszystkie blob SHA zweryfikowane. Bez merge/tag/release/version bump.

## 2. Aktualna architektura

Geometric nadal dekoduje. Source langpack v5 zachowuje jeden klucz i źródłowo potwierdzone warianty/default. Pasywne SI ma okno zachowujące kapitalizację/interpunkcję, feed WWM i scorer ONNX. Nowy tokenizer odczytuje oryginalny cased Char-BPE: słownik 50000 tokenów modelu, ranki/ID merge, suffix </w>, special tokens i tablice Unicode wyprowadzone z pinned Rust backend. To tokenizer modelu, a nie nowy słownik klawiatury.

Dodano import uwierzytelniany kompletem siedmiu niezależnie zaufanych tożsamości plików, private noBackup staging i scorer mapujący/ponownie haszujący model read-only. Jeden worker serializuje import, native load/score/close i usuwanie. Normalny pipeline IME nie wywołuje SI.

## 3. Ustalenia zaakceptowane

Użytkownik zlecił sprawdzenie i przygotowanie implementacji SI. Pierwszym punktem odniesienia mobilnego jest FP32, który przeszedł poprzednie score/rank parity. Nowy etap jawnie pakuje FP32; nie zmienia zakończonej próby INT8 ani jej bramki FAIL.

Docelowy pierwszy live zakres nadal porządkuje dwie formy najlepszego klucza geometric, zachowując obie i dotychczasowe klucze/punkty/języki/commit pipeline. Dopuszczenie do pierwszych trzech pozycji pozostaje celem użytkownika, nie nowym dowodem skuteczności SI. Telefon Nubia Z60 Ultra LV 12/512 GB; OS/SoC nadal niepotwierdzone.

## 4. Rozwiązania odrzucone lub odłożone

Bez ręcznego dopisywania opisów znaczeń, wyjątków Ale/Lub/tutaj, duplikowania słownika i mieszaniny surowych MLM/geometric scores. Bez CTC zmian, nowych modeli/interpunkcji/treningu, aktywacji produkcyjnej SI lub arbitralnego limitu latencji.

Nie akceptować własnych sum z manifestu importowanego ZIP jako uwierzytelnienia. HerbertBenchmarkTrial.trust pozostaje null do zweryfikowania pełnej nowej paczki. Nie twierdzić, że oryginalne Kotlin token vectors/JNI parity przeszły na podstawie samych syntetycznych testów. Nie wnioskować wydajności Nubii z hosta.

## 5. Zaplanowane, jeszcze niewdrożone

Po informacji o zakończeniu runów: sprawdzić head/compile/test/lint/export logs oraz raport i wszystkie artefakty. Pobrać mały metadata artifact, potwierdzić model/freeze/parity, przypiąć wszystkie siedem SHA/rozmiarów z provenance. Dostarczyć real metadata do JVM conformance test; następnie przygotować APK trial do telefonu.

Na telefonie: import zewnętrznej paczki, token/feed/native score/rank zgodność, cold load i repeated warmed pair timing, pamięć/PSS/thermal/UI. Potem niezależne konteksty/slates i opt-in dispatcher/settings z pełną tożsamością/timeout/recheck. Żadnego late update starej propozycji. BS trzy czasy hold/preview/gap pozostają backlogiem; zaakceptowanego przeciągania nie zmieniać.

## 6. Weryfikacja i rzeczy niezweryfikowane

[Poprzedni runtime run 37227497872](https://github.com/jakamilek/CleverKeysPL/actions/runs/37227497872), head b1c829cf: SUCCESS. Actual Kotlin compile, 2818 pure tests, 83 focused tests (LanguagePackImport 45, SwipeAutocapCommit 16, EditorPredictionRegression 8, SuggestionTapPartialReplace 11, SuggestionStripScroll 3), razem 2901, debug lint i release vital lint PASS. Bez APK.

Nowy [producer push run 37230171787](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787), head d831e17: IN_PROGRESS przy jedynym odczycie. PR-only contract [37230209583](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230209583): SUCCESS; nie wykonuje model inferencji. Nowy [runtime run 37230173951](https://github.com/jakamilek/CleverKeysPL/actions/runs/37230173951), head 63524ecd: IN_PROGRESS. Nowych compile/test/lint i właściwej konwersji jeszcze nie potwierdzono.

Lokalnie 13 poprzednich i 5 nowych stdlib tests PASS, Python compilation, stare/new source freeze, workflow YAML/permissions/pinned actions i guarded Gradle checks PASS. Manifest/layout/PL/base XML i 19 resource keys PASS. Dodano 15 Kotlin unit tests i jeden optional real-fixture test z jawnym skip, gdy nie dostarczono metadata. Nie ma lokalnego Kotlin/Android toolchain ani real inference; native wheels wcześniejszego lokalnego venv są niesprawne, nie używać ich.

## 7. Gałęzie historyczne i ich role

Accepted runtime v15 code 4e51c3b45285fdbfdc93531bd80e228444601818, workflow HEAD 6b3b2580094170384e1e0f9a4b72138546ebd884, docs/source-variants-integration-v1, draft PR #1. Passive mobile core b1c829cf, trial/herbert-mobile-preparation-v1, draft PR #2.

Producer v5 source 041b28ae4587c531ef73e62933e9151cadb84c33 na feature/source-variants-trial-v1. Metadata results c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b na experiment/context-surface-window-v1, draft PR #4. Mobile export freeze f4f994d3fd890402d6f4106ae4f75f4ebab76838 i results 1fb12ad na experiment/herbert-mobile-v1, draft PR #6. Stare metody/request/results zachowane.

## 8. Artefakty, SHA i punkty integracji

Nowy frozen protokół: [experiments/herbert_fp32_benchmark_v1](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c/experiments/herbert_fp32_benchmark_v1). Freeze pokrywa siedem source/workflow plików. Eksport ma odtworzyć FP32 651798883 B, SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2; zmiana przerywa publikację, bez automatycznego repin. Model allegro/herbert-base-cased rev 50e33e0567be0c0b313832314c586e3df0dc2297, CC BY 4.0. ORT 1.21.1, torch CPU 2.8.0, transformers 4.57.6, tokenizers jawnie 0.22.2, onnx 1.17.0, numpy 2.2.6.

Planowane artefakty: herbert-fp32-benchmark-v1-reports (małe metadata/environment/raporty) i herbert-fp32-benchmark-v1-model (zewnętrzny benchmark ZIP, bez kompresji, 14 dni). Bundle: model.onnx, tokenizer.json, portable-tokenizer.json, tokenizer-conformance.json, android-score-vectors.json, NOTICE.txt, manifest.json. Brak nowych artifact IDs/model hash manifestu do zaufania przed wynikiem.

[Runtime spec](https://github.com/jakamilek/CleverKeysPL/blob/63524ecda63cbbfebc39392a8826f28b0690a0d1/docs/specs/polish-context-ai.md) i AGENTS opisują granice. HerbertConformance porównuje token IDs, pięć feeds wszystkich 232 requests i native score/rank. HerbertBenchmarkActivity nieeksportowana; wejście przyciskiem Test polskiej SI na Swipe Playground. SI/live settings nadal nie istnieją.

## 9. Ograniczenia i znane luki

Dopiero nowe CI zweryfikuje założenia eksportu/tokenizer config i kompilację nowego Androida. Import jest celowo niedostępny. Model nie jest w Git/APK/backup. Normalizer/pre-tokenizer probe obejmuje wszystkie scalars; host interpreter dodatkowo wszystkie 4352 scalar blocks i boundary/seeded/archived/special cases. Real Kotlin/jni parity osobno.

Ekran używa wyłącznie syntetycznych/archived przykładów, nie czyta edytorów. Raport: device/Android/ABI, load z rehash, 90 warmed pomiarów dwóch form dla trzech długości; p50/p95 feed, inference, całość. Maximum sampled PSS całego procesu mierzone pomiędzy wywołaniami co najmniej 250 ms, nie dokładny peak ani pamięć wyłącznie modelu. Brak jeszcze wyników telefonu/thermal/energii czy niezależnej trafności. Usuwanie odbywa się po zamknięciu native session na workerze; pozostawiony staging po process death sprzątany przy następnym otwarciu testu.

Poprzedni FP32 PASS: max error 0.0001030, zero rank changes. Poprzedni INT8 FAIL: 22 rank changes, 7 top1 regressions, 3 repairs, 1 top3 regression. Nie poolingować new/reused/short/long jakości, nie przypisywać SI nasyconego top3 par samych form.

## 10. Następny uzasadniony krok techniczny

Poczekać na informację użytkownika, że runy zakończone; pobrać wyniki, nie uruchamiać długiego monitorowania. Zakończone raporty pobierać jako pracę, nie oczekiwanie. W tej fazie jeden odczyt list runów; całe monitorowanie wyraźnie poniżej 60 s/build, dalszego pollingu nie prowadzono.

Po udanych gates zweryfikować mały metadata ZIP i niezależnie pin pełny trust record, wykonać real JVM tokenizer/feed test, dopiero potem APK benchmark i pomiar Nubii. W razie błędu konfiguracji/hash/gates rozpoznać przyczynę, nie zdejmować bramki. Bez live aktywacji przed pomiarami. Gemini/PAL waiver, Gradle guard i zakaz subagentów bez jawnego zlecenia obowiązują.

## 11. Różnica względem poprzedniego kamienia milowego

Poprzedni Android CI już potwierdzono jako PASS. Od pasywnego scorera przechodzimy do konkretnego przygotowania FP32 paczki/tokenizera/importu i polskiego ekranu pomiarowego. Nowe code/workflow trial commits i draft PRs są opublikowane; modele/new CI/real parity jeszcze pending, trust null. Każdy main nadal tylko docs. Nie ma nowego APK, aktywnej SI, zmiany zaakceptowanej obsługi klawiatury ani nowej deklaracji jakości.
