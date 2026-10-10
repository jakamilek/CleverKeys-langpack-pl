# HerBERT V3 — wyniki sprawdzone, context gain odrzucony

## 1. Stan i identyfikacja
2026-10-10 po „Zakończone” o 13:21 Europe/Warsaw. Main przed checkpointem: CleverKeysPL 076afb511e5f07489b98018ddcd9b86c53afb431; CleverKeys-langpack-pl 62bbabfbb2a13592a2b4b05441684296fc5a6008. Ten commit dodaje wyłącznie dokumentację; poprzedni PROJECT_MILESTONE_2026-10-10_HERBERT_CONTEXT_GAIN_V3_STARTED.md zachowany.

## 2. Architektura i bieżąca aplikacja
CleverKeysPL trial/herbert-live-v1 nadal 3f48e456f0d8f411e80be3857f1846e4b2cd139e, draft PR4. Geometric + opcjonalny oryginalny HerBERT FP32 mean log probability, compact-case-v4. Nie zmieniono scorer/runtime/APK/model/langpack/deadline350ms ani edytora/prywatności. V3 miał osobne metryki odmiany i case, nie dwustopniowy runtime scorer.

## 3. Zweryfikowane wyniki i przyjęte ustalenia
V3 run38046863143 completed SUCCESS na 523d53e7b4e93db932030ca87a2e62730d7f5d03. Contract/measure i wszystkie kroki PASS, lecz allPreservationPassed=false. Każdy z trzech zbiorów nie przeszedł gate.
Metoda była zamrożona: sum_logp(context,same surface)−sum_logp(empty context,same surface).
History232/224 labelled: Top1 157→167,29 napraw/19 regresji,1 regresja rawTop3.
Form24: Top1 18→17,1 naprawa/2 regresje,1 regresja rawTop3; poprawna forma20→18/24.
New24: Top1 20→21,3 naprawy/2 regresje,0 regresji rawTop3.
Historia opisowo poprawia aggregate, ale strata 19 wcześniejszych trafnych Top1 blokuje zmianę. Nie łączyć trzech zbiorów dla ogólnej trafności.

## 4. Odrzucone i niezatwierdzone
Globalny gain scorer odrzucony; wcześniejszy sum nadal odrzucony po V2. Live mean pozostaje. Nie stroić współczynnika na tym samym zestawie ani dodawać wyjątku Praca.
Brak ręcznych opisów słownikowych, odmian/rdzeni, duplikatów, raw miksu geometrii/SI, zgadywanych progów miejscowości. Brak nowej aplikacji/exportu/uczenia, merge/release/tag/version bump.

## 5. Plan dalszej diagnozy
Niewdrożona hipoteza: ocena obserwowanego fragmentu zdania z widocznym kandydatem, przez te same maskowane słowa kontekstu dla wszystkich kandydatów. Wymaga osobnego freeze/protokołu, source-backed form i historycznych gates, nowych rodzin odmian oraz pomiaru dodatkowego kosztu. Nie traktować pomysłu jako sprawdzonego scorera.
Dwa sprawdzone przeliczenia target scores nie dały bezpiecznej poprawy; nie dowodzi to, że wszystkie metody lub sam HerBERT muszą zawieść.

## 6. Walidacja i dowody
CI testy mobile13+portable5+V1 13+V2 7+V3 18 PASS. Transitive freeze/source-bound cases,2471 tokenizer vectors,232batches/532candidates native/feeds parity, pełny fresh V1/V2 replay PASS.
280 rzeczywistych contextual/gain measurements,46 neutral batches,195 dodatkowych native calls; maxSingleBatchScoreError0. To host, nie pomiar Android.
Pobrano/re-hashowano report ZIP. Niezależnie sprawdzono wszystkie280 ID/context/surfaces/gold, frozen inputs, reprodukcje232/24, token IDs/counts, mean/sum/gain, pełne rankingi i każde pole metryk każdej grupy. Sprawdzono46 neutral feeds/attention/padding/target positions/masks, identyczność targetów i formułę gain. Nie była to lokalna nowa inferencja.
Przykłady: „Gdzie leży wieś ” nadal Pracą (gain3.166693) przed pracą0.023317,Praca−1.844588,praca−2.449965.
Nowe form regresje „Odwiedzi nas pani ” Malina→Maliną oraz „Ta wieś nazywa się ” Laska→Laską.
Nowe case regresje „Nad polem przeleciał wielki czarny ” i „Ten ptak o czarnym dziobie to ” kruk→Kruk.

## 7. Gałęzie, PR i uruchomienia
Producer experiment/herbert-form-diagnostic-v1: measured code523d53e7b4e93db932030ca87a2e62730d7f5d03; result-only HEAD 186f116ff79c7317d3578dd40fd142114682357d, dwa nowe pliki wyniku. Stare code/workflow/freeze byte-identical.
Draft PR13 https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 zaktualizowany z rzeczywistymi wynikami i odrzuceniem gain.
V3 SUCCESS https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38046863143
Runtime draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 bez zmian.
Nie uruchomiono kolejnego pomiaru ani nie monitorowano trwającego runu. Limit60s total/run nadal obowiązuje.

## 8. Artefakty i pochodzenie
V3 artifact11668485090 herbert-context-gain-v3-reports, ZIP89899B SHA-256 716919e079f178d936de10540fc014698f1ef436f3112fdf9d9a823084f38b63, pobrany i zweryfikowany.
Raw scores.json496135B SHA-256 cd125b04f67a69aa0f185a9151e4448dc8f58c134cc40c7a30e5e9487b1f9b76. Zachowany verbatim w experiments/herbert_form_diagnostic_results/2026-10-10-v3 wraz z RESULTS.md. Git blob25b951c82a840c71a9643eda47edef9841be21d8 zgodny z lokalnymi bytes.
Oryginalny FP32 SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2,ORT1.21.1CPU2/1, artifact11312693984/run37230171787.
Ostatni APK compact-case-v4 run38040432033/artifact11665712630, CI APK SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. Brak nowego APK.

## 9. Ograniczenia i backlog
History116cases każda short/long;224 labelled,8 unlabelled,4 labelled gold poza kandydatami. New24 to nowe konteksty znanych słów; Form24 tylko cztery rodziny. Brak niezależnego blind gold. Raw group Top3 nie jest całym phone suggestion strip.
FormComparable wymaga dostępnego gold i wielu lower-keys: History16eligible9→14,0formregressions. CaseGivenGoldForm porównuje kapitalizację wewnątrz gold form: History200eligible144→149,19case regressions. Form24 case22→22/24, ale jedna case regresja. Aggregate nie zastępuje zmian per request.
Neutralny baseline zmienia pozycję/prior początku zdania i może odejmować użyteczną częstość. Brak phone routing/geometry/latency claims.
FP32 RAM wciąż duży, default32 kontekstu (16/32/64). Odłożone braki swipe: dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam; kapitalizacją/kapitalizacje. Źródłowa warstwa częstości/populacji miejscowości nadal planowana.

## 10. Następny krok
Przedstawić użytkownikowi negatywny wynik dla Praca/Pracą i regresje, zachować stabilny APK. Jeśli kontynuujemy diagnozę, osobno zamrozić metodę zgodności gramatycznej obserwowanego kontekstu z widocznym kandydatem; bez kolejnego ad-hoc przeliczenia współczynnika i bez wdrożenia przed pełnymi gates/kosztem Android. Potrzebne także nowe różne rodziny odmian, nie tylko stare przykłady.

## 11. Różnica wobec poprzedniego checkpointu
V3 pending zmienił się na zweryfikowany SUCCESS techniczny/FAIL jakościowy. W pełni zachowano raw wyniki, niezależnie sprawdzono neutral feeds i wszystkie metryki. Gain odrzucono, nie naprawił Praca i pogorszył dwie poprawne odmiany. Aktualna klawiatura bez zmian; starsze checkpointy zachowane.
