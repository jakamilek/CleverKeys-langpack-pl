# HerBERT: zweryfikowany pomiar form V1, porównanie historii V2 rozpoczęte

## 1. Stan i identyfikacja
2026-10-10. Main przed checkpointem: CleverKeysPL 775b255e70757df3eb77d0dc2b47035bf4ebc2f5; CleverKeys-langpack-pl 0dc1df447508b6be34af0fa58ecace4449d98038. Ten checkpoint dodaje wyłącznie dokumentację. Poprzedni: PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_DIAGNOSTIC_STARTED.md.

## 2. Architektura i aktualna aplikacja
CleverKeysPL trial/herbert-live-v1 pozostaje na 3f48e456f0d8f411e80be3857f1846e4b2cd139e, draft PR4. Geometric dekoduje swipe, opcjonalny oryginalny HerBERT FP32 ocenia formy i kapitalizację. Live używa mean log probability. Compact-case-v4 ogranicza nadmiar wariantów wielkości liter w pierwszych podpowiedziach, zachowuje wszystkie formy i zwycięzcę. Brak zmiany APK/runtime/model/langpack w tym etapie.

## 3. Ustalenia i zweryfikowany wynik V1
Użytkownik: „Zakończone”. Run 38043798307 SUCCESS na 91a5986ee51d000107841bf5b1e0c32f5dc8bef3.
Model odtworzył „Gdzie leży wieś ”: mean daje Pracą, Praca, praca, pracą.
Praca: token [13567], mean=sum -12.620338439941406.
Pracą: tokeny [2819,2845], mean -8.603775978088379, sum -17.207551956176758.
Sum daje Praca, praca, Pracą, pracą.
Na 24 autorskich gold cases: mean Top1 18/24, diagnostyczny sum 22/24, raw group Top3 23/24 w obu; poprawna forma bez wielkości liter 20→24/24; kapitalizacja 22/24 w obu. Cztery naprawy form-01/02/03/04, zero regresji w tej próbie. Pozostałe błędy form-11/12: Pracy→pracy, tokenizacja jednoelementowa.
To trop normalizacji wyniku względem tokenizacji; nie dowód jedynej przyczyny błędów językowych.

## 4. Odrzucone lub niezatwierdzone działania
Nie przełączono live scorera na sum na podstawie 24 zdań. Nie dopisano ręcznych opisów, form ani reguł dla słowa Praca. Nie dodano zgadywanego progu rzadkości nazw wsi, duplikatów kluczy, CTC, raw miksowania SI/geometrii ani nowych uprawnień. Brak merge/release/tag/version bump.

## 5. Plan i realizacja V2
Nowy izolowany katalog experiments/herbert_form_diagnostic_v2 i workflow herbert-form-diagnostic-v2.yml; V1 pliki/workflow/freeze pozostały identyczne.
V2 najpierw powtarza zgodność oryginalnego modelu i 24 przypadki V1. Wymaga pełnych rankingów V1 bez zmian i wyników w tolerancji 0.001. Następnie realnie odczytuje mean/sum dla wszystkich 232 oryginalnych żądań z niezmienionym gold/context/surfaces/feeds. Grupy suite/population/window raportowane osobno; naprawy nie maskują regresji.
preservationPassed wymaga zero regresji Top1 i Top3 w każdej historycznej grupie. Quality fail jest wynikiem raportu, nie błędem uploadu. SUCCESS CI nie oznacza zatwierdzenia sum.

## 6. Walidacja
V1 CI: stare mobile 13 i portable 5, nowe 13 testów PASS. Tokenizer 2471 przykładów i 232 paczki / 532 kandydatów / pięć wejść: PASS, maxAbsScoreError 0.00004482269287109375. Single/batched różnica 0 dla nowych 24 grup.
Pobrano i zweryfikowano hash ZIP raportu; zachowano scores.json verbatim i niezależnie przeliczono wszystkie 24 rankingi, mean/sum, tokeny, maski i metryki.
V2 lokalnie: 7 testów kolektora i 13 niezmienionych testów V1 PASS; transitive freeze, AST/YAML PASS. Recount nowym kolektorem: 18→22 Top1, 23→23 Top3, 4 naprawy, 0 regresji.
Pełna inferencja V2 jest nadal oczekiwana: nie przedstawiać jej jako lokalnie wykonanej ani zakończonej.

## 7. Gałęzie, PR i runy
Producer experiment/herbert-form-diagnostic-v1: V2 commit 90a8398495cd119afce9038f5f55c454db2d6960, parent 91a5986ee51d000107841bf5b1e0c32f5dc8bef3.
Draft PR13: https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 (base experiment/herbert-fp32-benchmark-v1).
V1 SUCCESS: https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38043798307
V2 uruchomiony, ostatni odczyt in_progress: https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38045114375
Runtime draft PR4: https://github.com/jakamilek/CleverKeysPL/pull/4
Nie monitorować zakończenia; użytkownik zgłasza stan. Limit 60 s całego monitorowania runu.

## 8. Artefakty i pochodzenie
V1 raport artifact 11667680259, herbert-form-diagnostic-v1-reports, ZIP 8794 B; SHA-256 cf16f3053bf8ec2355cbb871fd8df7a2b4a995c92212dcb2a4ee93888f79688a, pobrany i rehashowany.
Wynik zapisany w producer experiments/herbert_form_diagnostic_results/2026-10-10-v1/{scores.json,RESULTS.md}.
Oryginalny bundle: run37230171787 artifact11312693984; ZIP SHA-256 36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f.
Model SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2, ORT1.21.1 CPU 2/1.
Ostatni APK compact-case-v4: runtime run38040432033 artifact11665712630; CI SHA-256 APK b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. Brak nowego APK.

## 9. Ograniczenia i backlog
24 krótkie autorskie zdania, cztery naprawy jednej rodziny; nie niezależny blind benchmark. Raw Top3 wewnątrz grupy nie jest Top3 całego paska telefonu. Direct host nie potwierdza ścieżki/timingu/geometry zgłoszonego swipe. Sum może preferować krótszą tokenizację. Błędy Pracy są osobnym problemem kapitalizacji/kontekstu.
FP32 RAM pozostaje wysoki. SI domyślnie 32 słowa (16/32/64), bez zapisu kontekstu użytkownika.
Odroczony słownik swipe: dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie, pozdrawiam; braki kapitalizacją/kapitalizacje. Dane częstości/populacji nazw miejscowości i ich źródła nadal do zaprojektowania, bez ręcznych hacków.

## 10. Następny krok
Po zgłoszeniu zakończenia sprawdzić oba jobs V2, wszystkie 232 sparowane wyniki i regresje per grupa, hash i pełne raporty; nie wnioskować z samego statusu SUCCESS. Jeśli są regresje sum, pozostawić mean i zaplanować ogólny dalszy eksperyment. Jeśli brak regresji, sprawdzić dodatkowe różne słowa/odmiany i długości tokenizacji przed zmianą opt-in aplikacji. Dopiero potem Android guards i test telefonu.

## 11. Różnica wobec poprzedniego checkpointu
Poprzednio V1 był tylko uruchomiony. Teraz SUCCESS i kompletny wynik V1 są sprawdzone i zachowane, diagnoza długości tokenizacji udokumentowana, V2 uruchomiony na całej wcześniejszej historii. Runtime i dotychczasowy APK bez zmian. Wszystkie wcześniejsze checkpointy pozostają zachowane.
