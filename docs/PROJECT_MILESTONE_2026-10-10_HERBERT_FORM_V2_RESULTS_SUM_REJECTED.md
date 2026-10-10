# HerBERT V2: pełne wyniki, globalny sum scorer odrzucony

## 1. Stan i identyfikacja
2026-10-10, po „Zakończone” użytkownika o 12:37 Europe/Warsaw.
Main przed checkpointem: CleverKeysPL f3cc2c4ef743ffd2432c6ede8a937159ca8bde97; CleverKeys-langpack-pl b830d0ccc6e0a616f30eb9ec55561f0b96bde9d8. Ten checkpoint wyłącznie dokumentacyjny. Poprzedni PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_V1_RESULTS_V2_STARTED.md pozostaje zachowany.

## 2. Architektura i aktualna aplikacja
Runtime trial/herbert-live-v1 nadal 3f48e456f0d8f411e80be3857f1846e4b2cd139e, draft PR4. Geometric + opt-in oryginalny HerBERT FP32; live mean log probability, compact-case-v4 zachowuje zwycięzcę i wszystkie formy, ogranicza warianty kapitalizacji w pierwszych miejscach. Brak nowej aplikacji/modelu/langpacka.

## 3. Przyjęte ustalenia i rezultat
V2 run38045114375 completed SUCCESS na 90a8398495cd119afce9038f5f55c454db2d6960, oba jobs contract/measure i wszystkie wymagane kroki PASS.
Jednak preservationPassed=false. Suma wyników NIE zachowuje wcześniejszych poprawnych wyborów.
232 żądania to 116 przypadków w krótkim i długim kontekście; 224 labelled (4 gold poza kandydatami), 8 unlabelled. W historii: 25 napraw Top1, 25 regresji Top1, 1 regresja Top3, 60 zmian pełnych rankingów. Opisowo Top1 157→157/224, raw group Top3 218→219/224. Nie sumować tego z fresh24 jako niezależnych testów.
Fresh24 powtórzony identycznie: mean 18/24, sum 22/24, raw Top3 23/24 w obu. Poprawienie Praca nie równoważy historycznych strat.

## 4. Odrzucone i niezatwierdzone
Globalna zamiana mean na sum odrzucona z powodu regresji. Bez per-word wyjątku dla Praca, ręcznych reguł kapitalizacji, opisów/odmian w słowniku, zgadywanych progów rzadkości czy duplikatów kluczy.
Nie wybrano jeszcze nowego scorera/współczynnika i nie wdrożono nowego eksperymentu. Brak merge/release/tag/version bump.

## 5. Plan dalszej diagnozy
Następny eksperyment musi osobno oceniać dobór formy i kapitalizację, uwzględniając nierówną tokenizację. Ma używać źródłowych form/metadanych i zachować poprawne historyczne Top1/Top3. Nowy scorer wymaga także nowych różnych rodzin słów przed zmianą APK. Nie obiecywać, że sum rozwiązuje odmianę bez skutków ubocznych.

## 6. Walidacja i sprawdzone przykłady
Testy CI: mobile 13 + portable 5 + V1 13 + V2 7 PASS; niezmienne freezes, oryginalna zgodność 2471 tokenizer vectors / 232 batches / 532 candidates, świeży V1 replay i pełne 232 native paired requests PASS.
Pobrano ZIP i zweryfikowano SHA. Niezależnie sprawdzono wszystkie 232 unikalne ID, wyrównane skończone wyniki, liczbę tokenów, mean*count=sum oraz każde pole metryk 12 grup. Osobno sprawdzono 24 ID, obydwa rankingi, target IDs, pełne feeds i tolerancję wyników względem zachowanego V1.
Regresje sum: „pękła dojrzała” jagoda→Jagoda; „usiadł czarny” kruk→Kruk; „Znam dwie kobiety o imieniu Luba. Nie pamiętam adresów obu” Lub→lub.
replay-4/short/plain „się bardzo”: miękko miejsce2→5.

## 7. Gałęzie, PR i runy
Producer experiment/herbert-form-diagnostic-v1: zmierzony kod 90a8398495cd119afce9038f5f55c454db2d6960; result-only HEAD e57f1585dd10124237299f1cee0e23cba0ed2046. Dodano wyłącznie dwa pliki wyniku, bez zmiany kodu/workflow/freeze i bez potrzeby nowej inferencji.
Draft PR13 https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 zaktualizowany do rzeczywistych wyników.
V2 SUCCESS https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38045114375
Runtime draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 bez zmian.
Monitorowanie runów max60s total; użytkownik raportuje zakończenie.

## 8. Artefakty i pochodzenie
V2 report artifact11667083213 herbert-form-diagnostic-v2-reports, ZIP35017B, SHA-256 c82bccad37fa8e7e5ba1a69ed7e018862fee0091f4bcf08cc81031504d852ab7. Pobrany/re-hashowany.
Raw scores.json188790B SHA-256 daeba444338ea0e6ffd012f1a28e29a016d6fdd639b5cb6347c769f5f5034443 zachowany verbatim wraz z RESULTS.md w experiments/herbert_form_diagnostic_results/2026-10-10-v2.
Oryginalny model SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2, ORT1.21.1CPU2/1, źródłowy artifact11312693984/run37230171787.
Ostatni APK compact-case-v4 run38040432033/artifact11665712630; CI APK SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. Brak nowego APK.

## 9. Ograniczenia i backlog
Historyczne i autorskie gold nie są nowym ślepym benchmarkiem. Krótki/długi kontekst jednego przypadku nie tworzy dwóch niezależnych zdań. Raw group Top3 nie jest całym paskiem telefonu. Brak potwierdzenia konkretnego phone routing/swipe geometry/timing.
Pracy→pracy pozostaje osobnym błędem kapitalizacji; sum go nie poprawia. Duży RAM FP32 pozostaje ograniczeniem; domyślny kontekst32 (16/32/64), bez zapisu kontekstu użytkownika.
Odłożony słownik swipe: dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie, pozdrawiam; kapitalizacją/kapitalizacje braki. Warstwa częstości/populacji nazw miejscowości nadal planowana, bez zgadywanych progów.

## 10. Następny krok
Przedstawić użytkownikowi wynik: sum jest regresywny, klawiatura pozostaje na mean. Zaplanować i zamrozić kolejną ogólną metodę porównania form/kapitalizacji oraz jej testy; nie poprawiać Praca punktowo ani wdrażać sum tylko dla tego przykładu. Każdą ewentualną zmianę aplikacji sprawdzić z historią, nowymi źródłowymi formami i Android guards.

## 11. Różnica od poprzedniego checkpointu
V2 z pending zmienił się na zweryfikowany SUCCESS techniczny / FAIL jakościowy zachowania wyników. Pełne surowe wyniki zachowano, regresje policzono i udokumentowano; globalny sum scorer odrzucono. Runtime/APK pozostaje bez zmian. Wszystkie poprzednie checkpointy zachowane.
