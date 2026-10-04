# Kamień milowy — potwierdzona tokenizacja Kotlin i naprawa kontrolki CI

Data: 2026-10-04. Real Kotlin tokenizer/feed parity PASS. Run zakończył brak rg w workflow po udanych testach; poprawka stdlib uruchomiona, APK nadal pending.

## 1. Zweryfikowany stan repozytoriów

Main przed tym dokumentem: producer a6c40c8157120d022c4c63102ce2aec1aa3ceb51; runtime 726d4d6c8de3dc68e4c6c393e1b27bbbdf8160f3. Każdy main otrzymuje tylko docs. Poprzedni checkpoint PROJECT_MILESTONE_2026-10-04_FP32_TRUSTED_PHONE_BENCHMARK_V1.md.

Producer experiment/herbert-fp32-benchmark-v1: source freeze d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c, results 1934a32e94fe50dcf7f7a748145f793f94b67825, aktualizacja dowodu Kotlin c4a3bdfa1cc386e743b9119eccc12b3a90255792 (tree 3fbb6cf51669481ddd26ced7a362ac99e373f1fb). Jeden plik RESULTS.md, blob verified. Draft PR #7 bez merge.

Runtime trial/herbert-fp32-benchmark-v1: functional HEAD 90615f0c7655ea5597c45db963e40480bfd03484; workflow/docs repair 73627fae758bcdf845ed8696be821b7052e326ff, tree c514b69c4d9378254563540e76cce3a007892cce. Cztery files workflow/AGENTS/todo/spec, wszystkie blob SHA verified. Żaden Kotlin/test/fixture/resource/model plik nie zmieniony w naprawie. Draft PR #3; bez merge/tag/release/version bump.

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

Producer 37230171787 at d831e17 SUCCESS: byte-identical FP32, 232 requests/532 candidate scores, zero archived rank changes, 2471 saved token vectors i 4352 exhaustive scalar-block host-reference comparisons PASS. Small ZIP/every non-model member locally hash verified; full comparison/saved token vectors recomputed PASS. Dużego model ZIP nie pobrano lokalnie.

[Runtime run 37231774451](https://github.com/jakamilek/CleverKeysPL/actions/runs/37231774451), head 90615f0: actual compile PASS, JUnitCore OK(2835), mandatory original conformance log PASS: 2471 token vectors; 232 batches /532 candidates /all five inputs. Nie ma Assume skip tego testu. Gradle BUILD SUCCESSFUL. Następny workflow command rg zakończył exit127 (command not found); krok/rund FAIL. Focused regression/lint/assembly/upload zostały skipped; żadnego APK.

Naprawa zastępuje dodatkowy rg marker search assertionem Python stdlib, zachowując tę samą pełną treść required marker. Lokalne wykonanie assertionu na obecnym markerze PASS, brak markeru odrzucony, YAML/pins/read-only permissions PASS. Odczyt logs potwierdza actual test output, nie tylko echo komendy.

[New run 37232458354](https://github.com/jakamilek/CleverKeysPL/actions/runs/37232458354), head 73627fa: IN_PROGRESS przy jedynym odczycie. Nie twierdzić że focused regressions/debug+vital lint/assembly/APK audit/upload przeszły. Native inference/phone timings nadal nieweryfikowane. Poprzedni 63524ecd compile/tests PASS i local-only other-locale lint correction opisany w poprzednim milestone.

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

Użytkownik zgłasza ukończenie nowego runu 37232458354. Wtedy sprawdzić cały job i artifact: exact head, real-conformance assertion, focused editor tests, debug/vital lint, assembly i APK ZIP audit. Dopiero podać zweryfikowany actual APK/link/SHA plus external model ZIP i instrukcję Playground/Test polskiej SI. Native parity i Nubia measurements pozostają kolejną fazą.

Nie pomijać tests/lint/marker, nie promować main kodem. Nie zakładać obecności rg na runnerze; Python stdlib już jest potrzebne do APK audit i nie dodaje zależności. Duża paczka zachowuje wszystkie fixed hashes; nie generować trust z user manifest.

Monitorowanie nowego build: jeden odczyt listy runów, <60 sekund TOTAL. Dalszego pollingu/oczekiwania nie prowadzono. Completed result/log retrieval jest pracą. Gradle guard, Gemini/PAL waiver, no subagents/merge/release/tag/version bump obowiązują.

## 11. Różnica względem poprzedniego kamienia milowego

Real Kotlin oryginalnego tokenizera i wszystkich pięciu feedów jest teraz potwierdzony; poprzednio pending. Nowy błąd nie jest pomyłką modelu/tokenizera: po udanych 2835 tests workflow użył nieobecnego rg. Naprawiono tylko tę komendę i docs, bez zmiany wymagań, kodu, danych/modelu czy ustawień. Workflow z dalszymi APK gates ponowiony; nadal brak APK i live SI. Dowód zapisano także w producer RESULTS, oba main tylko docs.
