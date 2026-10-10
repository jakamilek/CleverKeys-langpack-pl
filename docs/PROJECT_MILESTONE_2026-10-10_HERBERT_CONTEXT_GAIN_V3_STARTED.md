# HerBERT V3 — zamrożony test wpływu kontekstu uruchomiony

## 1. Stan i identyfikacja
2026-10-10, Europe/Warsaw. Autoryzacja użytkownika „Ok, działaj” o 12:49 po odrzuceniu sum scorera.
Main przed checkpointem: CleverKeysPL 87b947d80a616ce0871bbc67ce94ff4d3c85eb7b; CleverKeys-langpack-pl 408ca24cbea5435a0026e5d40349e0d07064f3e4. Ten checkpoint wyłącznie dokumentacyjny. Poprzedni PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_V2_RESULTS_SUM_REJECTED.md zachowany.

## 2. Architektura i bieżąca klawiatura
Runtime trial/herbert-live-v1 nadal 3f48e456f0d8f411e80be3857f1846e4b2cd139e, draft PR4. Geometric dekoduje, opcjonalny HerBERT FP32 live używa mean log probability; compact-case-v4 bez zmian. Nie zmieniono ONNX, APK, langpacka, terminu350ms ani zasad edytora/prywatności. W V3 rozdzielone są metryki form i case; nie wdrożono dwustopniowego scorera runtime.

## 3. Przyjęte ustalenia
V1 odtworzył Pracą przed Praca; sum poprawił 18→22/24 authored Top1.
V2 SUCCESS techniczny / FAIL preservation: 232 historyczne żądania, 25 napraw Top1, 25 regresji Top1, jedna regresja Top3. Live mean pozostał.
V3 sprawdza jedną metodę: gain(surface)=sum_logp(context,surface)−sum_logp(empty_context,same_surface). Bez alpha, nowej normalizacji, współczynnika czy reguły słowa. Identyczne target IDs/maski, pusty neutralny ciąg CLS+MASK+SEP. Remisy zachowują dostarczoną kolejność.

## 4. Odrzucone i niezatwierdzone działania
Nie wdrożono globalnego sum ani wyjątków Praca. Gain nie jest prawdopodobieństwem/skalibrowanym confidence ani dokładnym likelihood ratio MLM. Nie zakładamy, że odejmowanie usuwa całą stronniczość tokenizacji.
Brak ręcznych opisów słownikowych, zgadywanych odmian/rdzeni, duplikowania kluczy, raw miksu geometrii/SI, progu rzadkości miejscowości, uczenia/exportu i release/merge/tag/version bump.

## 5. Implementacja eksperymentu
Producer experiments/herbert_context_gain_v3: policy.py (gain i osobne metryki/gates), measure.py (pełny V2 replay, świeże realne neutral/new-context calls), test_gain.py, new-cases.json, PROTOCOL.md, zewnętrzny freeze; osobny workflow herbert-context-gain-v3.yml.
History232 zachowuje stare suite/population/window/gold/feeds. Odtworzenie pełnego V2 wyniku jest wymagane przed nowymi ocenami. Form24 osobno; New24: jagoda, róża, kruk, piła, buk, kot, po dwa gold common i dwa proper. Pełne konteksty nie pokrywają starszych prób. Pisownie pobrano automatycznie z zamrożonego ai_compare_v5/source-snapshot.json; ręcznie napisano tylko jawne zdania/gold benchmarku.
Łącznie280 żądań, neutralne baseline wyliczane realnie i współdzielone tylko dla identycznej uporządkowanej paczki w tym hostowym teście; osobne single/batched i target identity gates. Zapis wszystkich280 score/token/neutral-ID/zmian oraz całych neutral feeds. Wszystkie starsze pliki/freeze/workflow pozostają byte-identical.

## 6. Walidacja przed inferencją
18 nowych lokalnych testów PASS: score differences, remisy, NaN/Inf/overflow, form/case osobno, regresje między grupami, Top3, unknown/missing gold, balanced źródłowe cases i brak overlap, 232 reproduction, neutral feeds/target identities i baseline recount157/224 Top1,218/224 rawTop3.
Transitive freeze V3→V2→V1, source surfaces i budgets PASS. Trusted portable-table SHA i przygotowanie feeds wszystkich24 nowych kontekstów + neutral PASS. AST/YAML PASS.
Nowe token counts: jagoda2/Jagoda1, róża2/Róża1, kruk2/Kruk1; piła1/Piła1, buk2/Buk2, kot1/Kot1. To preflight tokenizacji, nie inferencja.
Jedyny lokalny błąd w przygotowaniu: gold kontekst „Umowę podpisał pan ” pokrywał starszą próbę, wykrył go test; przed inferencją zmieniono na „Zebranie poprowadził doktor ” i odświeżono wyłącznie nowy V3 freeze. Żadnego doboru po wyniku modelu.
Realne ONNX V3, pełne stare CI testy i fast/native zgodność pozostają pending w CI; nie przedstawiać ich jako wykonanych lokalnie.

## 7. Gałęzie, PR i uruchomienia
Producer experiment/herbert-form-diagnostic-v1: V3 commit 523d53e7b4e93db932030ca87a2e62730d7f5d03, parent e57f1585dd10124237299f1cee0e23cba0ed2046, tree 25072da04d0d1d331a1e145efb3ae99d71f30c69. Sprawdzono exact Git blob SHA siedmiu nowych plików, brak zmian starych oraz źródłowy snapshot blob6682a95b70fcf4cca9e5adb66a8e30ac73065fbe.
Draft PR13 https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 zaktualizowany do V1/V2 wyników i V3 pending.
Nowy run 38046863143 https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38046863143, zmierzony HEAD=523d53e7b4e93db932030ca87a2e62730d7f5d03; ostatni odczyt queued, nie zakończony. Nie czekać na completion. Limit60s total monitorowania/run, użytkownik zgłasza „Zakończone”.
Runtime draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 bez zmian.

## 8. Artefakty i pochodzenie
V3 oczekiwany artifact herbert-context-gain-v3-reports; brak nowego APK. Workflow przypięte action SHAs, Python3.12, requirements oryginalnego V1, ORT1.21.1CPU2/1.
Oryginalny bundle artifact11312693984/run37230171787; model SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2. To samo siedem trusted plików, bez re-exportu.
V2 verified report artifact11667083213 ZIP SHA c82bccad37fa8e7e5ba1a69ed7e018862fee0091f4bcf08cc81031504d852ab7; surowy scores.json SHA daeba444338ea0e6ffd012f1a28e29a016d6fdd639b5cb6347c769f5f5034443, zachowany w producer results/2026-10-10-v2.
Ostatni APK compact-case-v4: runtime run38040432033/artifact11665712630, CI APK SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f.

## 9. Ograniczenia i backlog
New24 = nowe konteksty znanych słów, nie unseen vocabulary; Form24 to tylko cztery rodziny odmian. Frozen/authored gold nie jest niezależnym blind benchmarkiem. Short/long jednego przypadku nie są niezależnymi zdaniami. Raw group Top3 nie jest całym paskiem telefonu.
Empty context zmienia pozycję i prior początku zdania; odjęcie może usunąć użyteczną częstość. Host neutral cache nie dowodzi kosztu Android; bez phone route/geometry/latency claim. Brak dowodu, że gain poprawia Praca lub Pracy.
FP32 RAM nadal wysoki, kontekst32 domyślnie (16/32/64). Odłożone słownikowe braki swipe dodam/grzeje/kasami/nawilżane/odpowiadam/patrzysz/poczekaj/podpowie/pozdrawiam i kapitalizacją/kapitalizacje. Warstwa źródłowych częstości/populacji miejscowości nadal planowana.

## 10. Następny krok po zgłoszeniu zakończenia
Sprawdzić oba jobs/logs, ZIP SHA, kompletne280 wyniki i każde neutral feed/token/hash. Niezależnie przeliczyć mean/gain rankingi, osobne metryki i regresje w każdej grupie; nie polegać na samym SUCCESS.
Gate zero regressions exactTop1/rawTop3/form/case w każdej grupie/dataset. Jeśli FAIL, zachować mean. Jeśli PASS, wymagać realnej poprawy form i nowych szerszych źródłowych rodzin odmian oraz Android guards/kosztu zanim powstanie nowy opt-in APK. Nie stroić współczynnika na tej samej ocenie.

## 11. Różnica względem poprzedniego checkpointu
Po odrzuceniu globalnego sum przygotowano i lokalnie zweryfikowano jedną inną metodę oraz24 nowe konteksty z source-backed kapitalizacją. Zamrożono protokół i uruchomiono pełny V3. Wyniku jakościowego jeszcze nie znamy. Klawiatura/ostatni APK pozostają bez zmian; starsze checkpointy zachowane.
