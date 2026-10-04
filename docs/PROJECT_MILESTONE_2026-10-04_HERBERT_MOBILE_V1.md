# Kamień milowy — eksport HerBERT i przygotowanie Androida v1

Data weryfikacji: 2026-10-04. Eksport zakończony: FP32 PASS, INT8 preservation FAIL. Kod przygotowawczy Androida zapisany; jego CI przy ostatnim odczycie trwało.

## 1. Zweryfikowany stan repozytoriów

Main przed tym zapisem: langpack 74348a44e4141d3d35615394aa68dc984ade914b; runtime fce8e760bcb08e159cf43c9bdd4d01077ce7204d. Oba main otrzymują wyłącznie dokumentację. Poprzedni checkpoint: PROJECT_MILESTONE_2026-10-04_METADATA_GUIDANCE_RESULTS_V5.md.

Producer experiment/herbert-mobile-v1: freeze f4f994d3fd890402d6f4106ae4f75f4ebab76838 (9 nowych plików); wyniki 1fb12ad350a8091e84edb561b0422d6f891b8c25 (7 nowych plików). Draft [PR #6](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/6) względem poprzedniej gałęzi eksperymentu. Runtime trial/herbert-mobile-preparation-v1: b1c829cf28886391cdc98a7b8d7b0bd16bf6b65e (11 plików), draft [PR #2](https://github.com/jakamilek/CleverKeysPL/pull/2) względem zaakceptowanej gałęzi v15. Git blob SHA nowych zmian zweryfikowano; cztery dokumenty/build.gradle dodatkowo porównano z oczekiwaną pełną treścią.

Wspólne punkty wejścia: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_HERBERT_MOBILE_V1.md), [langpack](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_HERBERT_MOBILE_V1.md).

## 2. Aktualna architektura

Geometric nadal dekoduje słowa. Langpack v5 ma jeden klucz z potwierdzonymi źródłowo wariantami i defaultem. SI plain wybiera pisownię na podstawie dłuższego kontekstu; źródłowe metadane nie są usuwane, ale obecny tekstowy prefiks nie jest rekomendowany.

Przygotowano prawdziwy graf ONNX WWM: wszystkie target subwords maskowane jednocześnie, BERT, MLM projekcja wybranych pozycji, log-softmax całego oryginalnego słownika, średnia/suma. Kandydaci w niezależnych wierszach batcha. Runtime ma pasywny rzeczywisty scorer ONNX, defensywne feeds, okno 64 słów/4096 jednostek UTF-16 zachowujące pisownię i ścisłą politykę kolejności dwóch form. Żaden komponent nie jest podłączony do IME.

## 3. Ustalenia zaakceptowane

Użytkownik zlecił mobilne sprawdzenie i przygotowanie integracji HerBERT. Pierwsza planowana widoczna faza porządkuje wyłącznie parę najlepszego klucza geometric, zachowując obie formy, klucze/punkty/języki/proweniencję i pojedynczy pipeline SuggestionHandler. Pełny ranking kluczy wymaga osobnej kalibracji.

FP32 i batched eager zachowują wszystkie 232 rankingi wcześniejszej próby. Obecny INT8 nie przeszedł zamrożonej bramki regresji. FP32 jest zgodnym punktem odniesienia do następnej jawnej fazy benchmarkowej; nie jest jeszcze gotowym modelem telefonu. Potwierdzony telefon Nubia Z60 Ultra LV 12/512 GB; OS/SoC nadal nieznane.

## 4. Rozwiązania odrzucone lub odłożone

Nie promujemy INT8 na podstawie zielonego statusu workflow: SUCCESS oznacza poprawnie ukończony eksperyment, a nie przejście obu bramek. Bez łagodzenia kryteriów po wynikach, wyjątków per słowo, strojenia na odkrytych pomyłkach lub wymyślonych opisów słownikowych.

Nie zastępujemy właściwego tokenizera przybliżeniem WordPiece/byte BPE. Nie dodajemy nieskalibrowanych log-probabilities do punktów geometric. Bez CTC zmian, produkcyjnej SI/interpunkcji, modelu w APK/Git, merge/release/tag/version bump.

## 5. Zaplanowane, jeszcze niewdrożone

Jawne przygotowanie paczki FP32 do benchmarku; dokładny tokenizer zgodny z HerbertTokenizerFast i wyeksportowanymi vectors; bezpieczny import/staging/hashes/NOTICE/usuwanie/lifecycle. Następnie shadow pomiar telefonu bez zmiany propozycji i niezależne konteksty/slates.

Live dispatcher z jednym najnowszym zadaniem, timeout/cancel, pełnymi tożsamościami edytora i main-thread recheck. Polski opt-in SI default off, tryb pomiar/kolejność wariantów, status/model, import/usunięcie/atrybucja, search/backup/reset. Nie wymyślać limitu opóźnienia przed pomiarem. Ciężary i tekst nie trafiają do backupu.

Backlog BS zachowany: czas do pierwszego zaznaczenia, preview do usunięcia (obecnie 350 ms), gap do następnego preview (200 ms); zaakceptowanego przeciągania nie zmieniać. Polski priorytetem tłumaczeń, inne odkryte błędy zapisywać na później.

## 6. Weryfikacja i rzeczy niezweryfikowane

[Producer run 37227484110](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37227484110): contract/export SUCCESS, upload INT8 candidate SKIPPED (bramka FAIL). PR contract 37227524084 SUCCESS, nie powtarza inferencji. 232 plain wejścia / 532 oceny; lokalnie przeliczono całe trzy comparisons z scores.json — dokładnie zgodne z CI. ZIP SHA256, commit/model/freeze/request, kompletność i skończone oceny zweryfikowane.

Batched Torch: max błąd 0,0000882, 0 zmian pełnego rankingu. FP32 ONNX: 0,0001030, 0 zmian, PASS (próg 0,001 i brak zmian). INT8: 22 zmiany rankingu, 7 regresji top 1, 3 naprawy, 1 regresja top 3 (Karsin, krótki replay, 2→4), FAIL. Long nowe 25/32→24/32; reused 50/64→47/64; long replay 7/8 top 1 i 8/8 top 3 bez zmian. Każda populacja/okno oddzielnie.

13 lokalnych stdlib tests PASS, Python compilation, YAML/pinned actions/permissions i freeze checks PASS. 17 testów JVM zarejestrowano w runtime. [Runtime run 37227497872](https://github.com/jakamilek/CleverKeysPL/actions/runs/37227497872) przy jedynym odczycie IN_PROGRESS; nie twierdzić że compile/test/lint przeszły. Brak lokalnego Android/Kotlin toolchain, realnego Android tokenizer/JNI parity, importu, pomiarów telefonu i APK SI.

## 7. Gałęzie historyczne i ich role

Zaakceptowana app v15: code 4e51c3b45285fdbfdc93531bd80e228444601818, workflow-only HEAD 6b3b2580094170384e1e0f9a4b72138546ebd884, docs/source-variants-integration-v1, draft PR #1. Producer v5 041b28ae4587c531ef73e62933e9151cadb84c33 na feature/source-variants-trial-v1.

Poprzednie model results 6c468719da474408b8ebadfcb03ebc184c32afda; metadata freeze bc5c4f46895a4bd8a64d5c0736d3d58357ef12a7, results c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b na experiment/context-surface-window-v1, draft PR #4. Te pliki/gałęzie zachowane; nowe PR są kolejno zależne od ich baselines, bez merge.

## 8. Artefakty, SHA i punkty integracji

[Raport konwersji](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/1fb12ad350a8091e84edb561b0422d6f891b8c25/experiments/herbert_mobile_v1_results/RESULTS.md); raw scores, pełny conversion report, tokenizer i Android score vectors, SUMMARY i artifact-manifest obok. Artifact 11313090360, ZIP SHA256 fda36d777a04a4502cc19efecf857899f1bb4f64f7fc4a3dc327228adbd2747d.

Mobile freeze SHA256 ae6d982a1974f196b35aa9a0b08d827b4d47c37425ccd353d88f55f4631e0eca; request payload 532b44e562982338195a5d1ba5f0b532b16fee52755ad2d17db970e82b581708. Model allegro/herbert-base-cased rev 50e33e0567be0c0b313832314c586e3df0dc2297, CC BY 4.0; NOTICE opisuje autorów i modyfikację. ONNX 1.17.0; ORT 1.21.1 odpowiada faktycznym Android/JVM build.gradle, README 1.20.0 jest nieaktualne.

Tymczasowy FP32 651798883 B, SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2; INT8 280876470 B, SHA256 295bce14c649bdd1549f710f19d8b59d13e3cbcec6275c80de2bf6cb6909025b. Wagi nie zostały opublikowane jako candidate. Kolejny benchmark wymaga jawnego etapu pakowania.

[Runtime spec](https://github.com/jakamilek/CleverKeysPL/blob/b1c829cf28886391cdc98a7b8d7b0bd16bf6b65e/docs/specs/polish-context-ai.md) określa integrację po source lookup w istniejącym SuggestionHandler/SwipeSurfaceVariants, przed publikacją i auto-insert; bez drugiego commit path i późnych zmian starej propozycji.

## 9. Ograniczenia i znane luki

Obecne dane są diagnostyką znanych kluczy, nie niezależną próbą generalizacji. Top 3 samych form nasycone dwiema formami, również bez SI; nie przypisywać SI takiej skuteczności. Replays historyczne i nieskalibrowane z geometrią.

Host CPU, dwa wątki, p50/p95 całego zestawu bez tokenizacji/feed preparation: FP32 24,8/44,3 ms, 621,6 MiB; INT8 13,7/23,6 ms, 267,9 MiB. Szczyt RSS 3171 MiB dotyczy wspólnego procesu z Torch i dwiema sesjami, nie jednej zoptymalizowanej ścieżki. To nie wynik Nubii. Brak startu/RAM/energii/płynności telefonu. Native scorer nie ma jeszcze potwierdzenia actual model vectors na Androidzie.

## 10. Następny uzasadniony krok techniczny

Po informacji użytkownika o zakończeniu runtime run sprawdzić compile/tests/lint. Równolegle następny jawny etap: paczka FP32 benchmark, dokładny tokenizer/import i telefon shadow. Lżejszy model wymaga osobnego freeze i jakości, obecnego v1 nie zmieniać ani nie powtarzać bez potrzeby.

Maksymalnie 60 sekund TOTAL monitorowania na build. W tym etapie jeden odczyt list runów około 0,7 s; eksport już był zakończony, dalsze odczyty pobierały jego wyniki, nie czekały na CI. Runtime nie był ponownie odpytywany. Gemini/PAL waiver i zakaz subagentów bez jawnego zlecenia obowiązują.

## 11. Różnica względem poprzedniego kamienia milowego

Z rekomendacji HerBERT przechodzimy do rzeczywistej konwersji i konkretnego pasywnego kodu Androida. FP32 zachowuje wcześniejsze wyniki; obecny INT8 wprowadza regresje i nie otrzymał paczki candidate. Źródła, v5, poprzednie metody i zaakceptowana obsługa app pozostają. Nie ma jeszcze live SI ani nowego APK. Przygotowano kontrolowany następny etap tokenizera/importu i pomiaru telefonu.
