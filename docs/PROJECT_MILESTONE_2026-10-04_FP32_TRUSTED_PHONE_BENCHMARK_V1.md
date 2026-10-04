# Kamień milowy — zweryfikowana paczka FP32 i przygotowanie APK do telefonu

Data: 2026-10-04. Paczka FP32 PASS; poprzedni Android compile/tests PASS, lint FAIL tylko brak tłumaczeń trial. Nowy run z mandatory real fixtures i APK trwa przy jedynym odczycie.

## 1. Zweryfikowany stan repozytoriów

Main przed dokumentem: producer fb56aeaf7eb958ce8cceaea2cc95e1a36b8342ff; runtime b35da3e40c4edba04d17e9e82c2944b48b6f56d8. Main wyłącznie docs. Poprzedni checkpoint PROJECT_MILESTONE_2026-10-04_FP32_BENCHMARK_PREPARATION_V1.md.

Producer experiment/herbert-fp32-benchmark-v1: source freeze d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c; results 1934a32e94fe50dcf7f7a748145f793f94b67825, tree e70002623e741ce91f3321eef64f8ec749e828fc. Sześć nowych result files, wszystkie blob SHA zweryfikowano. [Draft PR #7](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/7), base experiment/herbert-mobile-v1.

Runtime trial/herbert-fp32-benchmark-v1: preparation 63524ecda63cbbfebc39392a8826f28b0690a0d1; nowy HEAD 90615f0c7655ea5597c45db963e40480bfd03484, tree 64031ac091d956a19433d1c83e67ddacd09a2b90. Dziewiętnaście zmienionych/nowych plików, wszystkie blob SHA verified, w tym binary gzip 714592a80bc3663af64cccb8288b122ac0a7a238. [Draft PR #3](https://github.com/jakamilek/CleverKeysPL/pull/3), base trial/herbert-mobile-preparation-v1. Bez merge/release/tag/version bump.

## 2. Aktualna architektura

Geometric i normalny SuggestionHandler nie wywołują SI. Langpack źródłowo potwierdzone warianty/default zachowane. Runtime ma oryginalny portable Char-BPE, bounded WWM feeds i actual ONNX scorer, teraz z compiled trust siedmiu plików zweryfikowanej paczki.

Diagnostic Activity (non-exported) otwierana z Swipe Playground przyciskiem Test polskiej SI. Import/prywatny noBackup staging, mapped read-only model, inferencja/native close/usuwanie na jednym workerze. Nie odczytuje edytorów ani historii pisania. Context default 32 słowa, safety maximum 64 i 4096 UTF-16. Docelowy live context ma pochodzić z aktualnego pola przed kursorem, zachowywać case/punctuation i uwzględniać paste/edits; ta ścieżka jeszcze niewdrożona.

## 3. Ustalenia zaakceptowane

Użytkownik zgłosił zakończenie obu runów oraz zakwestionował potrzebę 64 słów, wskazując połowę jako wystarczającą dla krótkiego pisania. Przyjęto 32 jako domyślny limit przygotowywanego kontekstu i 64 jako cap do porównania. Krótki tekst przekazywany w całości, bez sztucznego wypełniania. Rozmiar modelu/APK nie zależy od tej stałej; wpływ na latency/RAM wymaga pomiaru.

Polski priorytetem; braki innych języków odnotować do późniejszego uzupełnienia. Native benchmark to przygotowanie integracji, nie live aktywacja. Pierwszy przyszły live zakres nadal kolejność dwóch potwierdzonych form najlepszego klucza geometric, obie zachowane.

## 4. Rozwiązania odrzucone lub odłożone

Nie akceptować hash z manifestu user ZIP jako źródła zaufania. Nie interpretować green host run jako Kotlin/JNI/mobile accuracy. Poprzedni INT8 FAIL nadal FAIL. Bez punktowych wyjątków, ręcznie wymyślonych opisów, nieskalibrowanych MLM+geometric scores, CTC zmian, treningu, interpunkcji lub live settings.

Nie dodawać dużych wag ani test fixtures do APK. Bez gromadzonej historii z innych aplikacji, editor logging, network fallback czy model/text backup. Bez arbitralnych latency thresholds i accuracy conclusions z benchmarku 32/64.

## 5. Zaplanowane, jeszcze niewdrożone

Po informacji o ukończeniu nowego runtime run: sprawdzić dokładny head, compile, obowiązkowy real-conformance marker, regression tests, debug/vital lint, assembly i APK ZIP audit/upload. Dopiero pobrać/podać actual APK artifact ID i hashes. Obecnie nowego APK nie potwierdzono.

Nubia Z60 Ultra LV 12/512: zainstalować ARM64 trial, otworzyć Playground/Test polskiej SI, importować external model ZIP z producer run, uruchomić test i skopiować metryki. Phone native score/rank parity, cold/warm repeated latency/PSS/thermal/UI jeszcze pending. Następnie niezależne konteksty/slates i opt-in live dispatcher/settings z identity/deadline/recheck, bez drugiego commit path.

BS trzy czasy pierwszego preview/usunięcia/przerwy pozostają backlogiem. Nie zmieniać zaakceptowanego przeciągania.

## 6. Weryfikacja i rzeczy niezweryfikowane

[Producer run 37230171787](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787), head d831e17: contract/package SUCCESS, model i small metadata upload SUCCESS. FP32 byte-identical, 232 requests/532 candidate scores, zero ranking changes. 2471 saved token vectors i 4352 exhaustive scalar blocks host portable/reference vs original fast PASS.

Lokalnie metadata ZIP SHA/rozmiar, bezpieczne entries i każdy nie-modelowy member SHA/size PASS. Full float-comparison przeliczony z score vectors + archived reference i dokładnie zgodny. All 2471 portable token vectors ponownie PASS. Actual raw weight ZIP nie był pobrany lokalnie; CI wymagało raw model hash przed upload.

[Poprzedni runtime 37230173951](https://github.com/jakamilek/CleverKeysPL/actions/runs/37230173951), head 63524ecd: Kotlin compile PASS; JUnitCore OK(2834), focused 45+16+8+11+3=83 PASS. Real fixture test wtedy assumption-skipped, więc nie jest to real-tokenizer success. Debug lint FAIL: 19 MissingTranslation errors w nowym trial resource file; release-vital/assembly nie uruchomione. Pozostałe 225 warnings nie są nowym dowodem błędu blokującego.

[Nowy runtime run 37231774451](https://github.com/jakamilek/CleverKeysPL/actions/runs/37231774451), head 90615f0: IN_PROGRESS przy jedynym odczycie. Mandatory Kotlin 2471 vectors/232 batches, nowe default-context testy, lint, APK assembly jeszcze niepotwierdzone. XML/base-PL 20 keys/numbered formats, YAML/pinned actions/guard i wszystkie commit blob SHA lokalnie PASS.

## 7. Gałęzie historyczne i ich role

Accepted v15 app 4e51c3b45285fdbfdc93531bd80e228444601818, workflow-only 6b3b2580094170384e1e0f9a4b72138546ebd884, docs/source-variants-integration-v1, draft PR #1. Passive mobile core b1c829cf28886391cdc98a7b8d7b0bd16bf6b65e, trial/herbert-mobile-preparation-v1, draft PR #2, CI 37227497872 SUCCESS (compile/2901 registered+focused test results/lints).

Producer v5 source 041b28ae4587c531ef73e62933e9151cadb84c33; metadata results c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b, experiment/context-surface-window-v1, draft PR #4. Mobile freeze f4f994d3fd890402d6f4106ae4f75f4ebab76838 i results 1fb12ad350a8091e84edb561b0422d6f891b8c25, experiment/herbert-mobile-v1, draft PR #6. Stare source/request/freeze/results zachowane.

## 8. Artefakty, SHA i punkty integracji

[FP32 results](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/1934a32e94fe50dcf7f7a748145f793f94b67825/experiments/herbert_fp32_benchmark_v1_results/RESULTS.md), full reports/manifest/provenance obok. Model allegro/herbert-base-cased rev 50e33e0567be0c0b313832314c586e3df0dc2297, CC BY4.0. FP32 651798883 B, SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.

Small metadata artifact 11312569320, 1299643 B, ZIP SHA256 2310649ba6e8c9b72e40952687d88a50940a71d6cfadb186ca055138bdea91d6. Model artifact 11312693984, 657295441 B, GitHub archive digest 36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f, expires 2026-10-18T19:57:49Z. Manifest 1243 B, SHA256 667bd4fee413a13ca8edca75f5b7defff2c58d0450d8d87ab8e9ccef948026b0.

Compiled trust: model, tokenizer.json (3688783 B), portable-tokenizer.json (1468574 B), tokenizer-conformance.json (225506 B), android-score-vectors.json (109889 B), NOTICE.txt (1653 B), manifest.json. Pełne SHA w HerbertBenchmarkTrial i producer manifest. Runtime test resources: deterministyczny gzip portable (541439 B) i dwa oryginalne JSON vectors; hashes sprawdzane po dekompresji. Bez wag, nie APK assets.

Planowany APK artifact cleverkeys-herbert-fp32-benchmark-trial-arm64: istniejąca wersja/debug signature, APK + sha256 + identity JSON. Publikacja tylko po gates, exact conformance PASS marker i APK ZIP audit braku giant weights/test fixtures. ID jeszcze nieznane.

## 9. Ograniczenia i znane luki

Archived contexts najwyżej 13 słów; 32/64 nie porównano pod kątem niezależnej trafności. Saved fixtures to znane próby, nie generalizacja; top3 par samych form nasycone strukturalnie. Current INT8: 22 rank changes, 7 top1 regressions, 3 repairs, 1 top3 regression — bez nowej zmiany tych faktów.

Benchmark porównuje runtime latency 32/64 na dwóch formach i trzech długościach synthetic context, trzy warmupy per context/window, 30 powtórzeń, 90 próbek/window (180 total). Naprzemienna kolejność limitów ogranicza stały order bias. Raport per-window i pooled feed/inference/total p50/p95, load z rehash, phone/Android/ABI i maximum sampled whole-process PSS. PSS między calls co najmniej co250 ms, nie exact peak, model-only memory ani energia/thermal claim. Bez edytora i historycznych tekstów usera.

Braki 18 innych locale dla 20 nowych strings w docs/LOCALIZATION_BACKLOG_POLISH_AI.md; Polish/base complete. Local-only tools:ignore MissingTranslation w nowym pliku experimental screen realizuje preferencję użytkownika; globalne lint rules nietknięte. Uzupełnić native review przed szerszą publikacją.

## 10. Następny uzasadniony krok techniczny

Nie monitorować runu stale. Nowy build odczytano raz, wyraźnie <60 sekund TOTAL monitorowania; completed reports pobierano jako pracę, nie oczekiwanie. Użytkownik zgłasza ukończenie. Wtedy sprawdzić real Kotlin/native-related preparation/compile/test/lint/APK artifact. Jeśli real fixtures fail, rozpoznać algorytm/dane, nie pomijać checka ani powracać do Assume.

Jeśli gates PASS: przekazać trial APK i zewnętrzną paczkę wraz z prostą kolejnością testu na telefonie, zebrać wynik. Live pozostaje osobną fazą po pomiarach i niezależnych przypadkach. Bez merge/tag/release/version bump, Gradle wyłącznie guard, Gemini/PAL waiver, bez subagentów.

## 11. Różnica względem poprzedniego kamienia milowego

FP32 paczka/original host tokenizer gates potwierdzone; trust null zastąpiony siedmioma verified identities. Mandatory real JVM fixtures zastępują optional skip. Ujawniono konkretny lint blocker innych tłumaczeń i zapisano backlog/ściśle lokalne odroczenie. Default kontekstu 32, benchmark porównuje 32/64. Nowy workflow po required gates przygotuje ARM64 APK bez modelu/test fixtures; run jeszcze pending. Aktualne results/code/docs commits zapisane i zweryfikowane, main dalej docs-only, live IME unchanged.
