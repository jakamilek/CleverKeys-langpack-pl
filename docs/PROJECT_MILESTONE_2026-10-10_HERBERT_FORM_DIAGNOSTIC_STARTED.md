# Kamień milowy — rzeczywista diagnostyka odmiany HerBERT: CI wystartowało
Data: 2026-10-10 UTC. Autoryzacja „Ok, działaj”, 11:54 Europe/Warsaw.

## 1. HEAD main przed zapisem
Runtime: be1e6294305f23046cae605435337fdd9968c09c.
Producer: 564b7207b147c033d7494542ae217168fe282107.
Są to odczytane HEAD przed nowymi commitami dokumentacyjnymi.
Wspólny checkpoint w [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_DIAGNOSTIC_STARTED.md) i [producer](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_DIAGNOSTIC_STARTED.md).

## 2. Architektura
Runtime trial pozostaje 3f48e456f0d8f411e80be3857f1846e4b2cd139e, compact-case-v4.
Nowa isolated producer branch experiment/herbert-form-diagnostic-v1, code 91a5986ee51d000107841bf5b1e0c32f5dc8bef3, parent d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c. Dokładnie osiem nowych plików w experiments/herbert_form_diagnostic_v1 oraz nowy workflow, stare pliki producenta nienaruszone.
Wymagane poprzednie mobile/portable contracts, siedem hashów byte-identical FP32 bundle, exact fast/portable tokenization, 2471 token vectors, 232 batches/532 candidates/five inputs i real ONNX reference score/rank parity. Dopiero potem24 nowe czteroelementowe inferencje i96 kontrolnych single-row. ORT1.21.1 CPU threads2/1.

## 3. Zaakceptowany zakres
Odtworzyć preferencje modelu dla „Gdzie leży wieś ” i kontrolnych odmian/kapitalizacji przed dobieraniem wag.
24 krótkie jawne authored gold cases, wszystkie do5 słów, limit32. Jeden zgłoszony kontekst, jeden wcześniejszy i22 nowe; grupy praca/pracą, praca/pracy, malina/maliną, laska/laską, łaska/łaską. Wszystkie4 powierzchnie każdego case są w verbatim sourcev5 fixture i mają wspólną case-sensitive source lemma/POS.
source-fixture.json pochodzi bez zmian z runtime 3f48e456, SHA2569d3b13daee6be7373d583a12f26f6694cc610b3fcd3852a47fb4fdc9830f09b1,20838B. Metadane bramkują dopuszczalne grupy; do modelu trafia kontekst i powierzchnie.
Raport zachowa każdą mean/sum ocenę, token IDs/liczbę, pięć wejść, gold rank, ending/capitalization oddzielnie, strata group/origin, single-batch error i proweniencję. Freeze wszystkich nowych plików/workflow oraz oryginalnego PortableTokenizer przed inferencją.

## 4. Odrzucone
Bez punktowego wyjątku dla wieś/Praca. Bez zmiany algorytmu mean→sum po pojedynczym zgłoszeniu. Sum-rank jest tylko diagnostyką.
Nie dopisujemy ręcznych opisów/wag/form do słownika. Nie miksujemy geometry/logp i nie ustalamy confidence penalty.
Brak APK/model export/retraining/langpack/rankingu zmian, merge/release/tag/version bump.

## 5. Plan, jeszcze niewdrożony
Po wynikach rozstrzygnąć model preference vs potrzebę diagnostyki capture/grupy/fallbacku live. Nietekstowa diagnostyka ostatniej ścieżki telefonu jest planned, nie zaimplementowana.
Ewentualne tagi SGJP/Morfeusz i case-use/geographic priors wymagają audytu pokrycia, wieloznaczności i osobnego mechanizmu oceny kontekstu. Same tagi nie wybierają przypadku.
Global swipe coverage pozostaje odłożone, nie naprawione tym eksperymentem.

## 6. Stan walidacji
Lokalnie PASS:
-13 meaningful contract tests: freeze/source identity/foreign reading bounds, kompletność, gold, tensor padding/maski, mean/sum/finite/stable ties, zewnętrzne zaufanie plików i symlinks;
-Python AST/YAML oraz uprawnienia read-only, zachowanie potrzebnych gates;
-original metadata ZIP11312569320 SHA2562310649ba6e8c9b72e40952687d88a50940a71d6cfadb186ca055138bdea91d6 pobrano/re-hashowano;
-portable2471 token vectors oraz pełna zgodność232 pięcio-wejściowych paczek/532 targets z oryginalnymi fixtures;
-wszystkie8 nowych Git blob SHAs w tree przed commit/ref; oryginalny portable blob83e5f1485f4d52ebff43bee1cc77b116c940e254 identyczny.
Brak lokalnej real ONNX inferencji. Nie traktować kontroli feeds jako pomiaru językowego.
[Run38043798307](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38043798307) HerBERT form diagnostic v1 na 91a5986ee51d000107841bf5b1e0c32f5dc8bef3: in_progress w pierwszym odczycie. Real model scores, previous CI contracts, completeness i report artifacts pozostają PENDING. Monitorowanie kończymy bez czekania; cap60s total/run.

## 7. Gałęzie i przegląd
Nowy draft[PR13](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13) przeciw experiment/herbert-fp32-benchmark-v1 (odczytany HEAD ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3), tylko do przeglądu, brak merge.
Runtime trial/herbert-live-v1 oraz draftPR4 bez zmian kodu.
Main obu repo dostają wyłącznie dokumentacyjny checkpoint.
Poprzedni checkpoint docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_PHONE_FEEDBACK.md: użytkownik „Jest dużo lepiej”, ale Pracą przed Praca. To nie pełna walidacja jakości.

## 8. Artefakty i tożsamość
Nowy raport będzie herbert-form-diagnostic-v1-reports: scores.json, SUMMARY.md, środowisko, bez modelu. Jeszcze brak zweryfikowanego artefaktu wynikowego.
Input original model artifact11312693984/run37230171787/d831e17b; API expired=false,657295441B ZIP, digest36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f, expires2026-10-18.
Model651798883B SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2; wszystkie7 compiled hashes kopią HerbertBenchmarkTrial. Workflow download-artifact w tym samym repo z actions:read, pinned original run/ID, bez nowych secrets.
Bieżący phone APK nadal artifact11665712630/live38040432033, code3f48e456. ZIP digest9064c0a0190404e9c7edfb00ceffd6ef832f5988a56bec296210783010a4aa52; APK CI SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. Nie powstał nowy APK.

## 9. Ograniczenia i luki
Gold authored i znany, nie zewnętrzny blind test. Raw model Top3 wewnątrz grupy4 nie jest Top3 na telefonicznym pasku po compact presentation.
BaselineOrder jest synthetic source default order, nie odtworzoną geometrią swipe. Route DIRECT_HOST_ONNX_NO_IME_FALLBACK potwierdzi użycie modelu w eksperymencie, ale nie dowodzi ścieżki zgłoszonego telefonu ani czasu native Android.
Jeśli direct host wybierze Pracą, odtwarzamy błąd preferencji dla tego konkretnego kontekstu/grupy. Jeśli Praca, potrzebna dalsza weryfikacja realnego capture/grupy/fallbacku; nie oznacza automatycznie poprawności modelu.
Historyczny PSS około2132MiB,234 lint warnings i dictionary backlog (dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam oraz kapitalizacją/kapitalizacje) pozostają.

## 10. Następny krok
Po informacji użytkownika o zakończeniu odczytać oba jobs, wszystkie gates, ZIP SHA i pełny scores.json, niezależnie przeliczyć metryki/ranki na wszystkich24 cases oraz osobno reported/new/previous i grupy. Dopiero wtedy dobrać ogólny kierunek poprawki lub dodać beztekstową diagnostykę live. Nie zgadywać oceny SI dla Praca przed wynikiem.

## 11. Różnica
Poprzednio był feedback i plan. Teraz nowy zamrożony diagnostyczny kod/testy/workflow są zapisane na izolowanej gałęzi, kontrola localfeeds/source PASS i uruchomiona real inferencja. Runtime pozostaje użytkownikowi dostępnym v4, bez zmian danych/modelu.
