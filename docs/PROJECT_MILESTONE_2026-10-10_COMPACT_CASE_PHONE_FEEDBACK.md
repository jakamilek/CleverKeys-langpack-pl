# Kamień milowy — feedback telefonu: wybór odmiany po „Gdzie leży wieś”
Data: 2026-10-10. Zgłoszenie użytkownika 11:45 Europe/Warsaw.

## 1. HEAD main przed dokumentacyjnym zapisem
Runtime: 3255765281f87b9ece2e3b4673170f84306e1d0a.
Producer: fa8c7a60735b5c032344bc6f1f95d0b6f5b41985.
Ten dokument jest wspólny dla [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_PHONE_FEEDBACK.md) i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_PHONE_FEEDBACK.md).

## 2. Architektura
Trial code 3f48e456f0d8f411e80be3857f1846e4b2cd139e, branch trial/herbert-live-v1, draft PR4. Geometric + oryginalny HerBERT FP32, bounded group max4, default32/350ms; compact-case-v4 terminalna prezentacja zachowuje winner i wszystkie alternatywy.
Zweryfikowano na tym SHA: HerbertLiveRuntime.rank wysyła context i group.surfaces do tokenizer.prepare; HerbertFormGroup.ordered sortuje powierzchnie po mean log probability. Metadane wybierają uprawnioną grupę porównania; nie są instrukcją/promptem ani dodatkowym constraintem przypadków.

## 3. Zaakceptowane i feedback
Użytkownik: „Jest dużo lepiej”. Jednocześnie po kontekście „Gdzie leży wieś ” zgłosił Pracą jako pierwszą, Praca jako drugą.
W docelowym zdaniu „Gdzie leży wieś Praca” oczekiwana jest Praca. Poprawna forma była dostępna Top2, lecz pierwsza propozycja miała niewłaściwy przypadek. To jakościowa obserwacja, nie benchmark trafności.

## 4. Odrzucone
Bez punktowego wyjątku dla Praca lub słowa wieś. Bez zmiany źródłowej pisowni słownika i bez arbitralnego geometry/logp penalty na podstawie jednego przykładu. Nie przypisujemy tego wyniku na pewno inferencji SI bez danych o użyciu/fallbacku w tej próbie.

## 5. Plan, jeszcze niewdrożony
Najpierw niezależna próba rzeczywistego modelu na jawnych, syntetycznych kontekstach i tych samych powierzchniach, z wynikami per powierzchnia, identyfikacją SI/fallback oraz bazowym rankingiem. Przykłady kontrolne: „Gdzie leży wieś ” → Praca, „Ta wieś nazywa się ” → Praca, „Jutro spotkam się z ” → Maliną, „To jest bardzo ważna ” → praca. Cel: ocena zarówno rodzaju nazwy, jak i odmiany; zachowanie poprawnych alternatyw.
Dopiero po wynikach dobrać mechanizm ogólny. Rozważyć źródłowe tagi SGJP/Morfeusz (przypadek/liczba/rodzaj), z audytem pełnego pokrycia i wieloznaczności. Same tagi opisują kandydata; wybór przypadku dla kontekstu wymaga modelu/analityka składniowego oraz niezależnej walidacji. Nie obiecywać, że samo dodanie tagów naprawi ranking.
Wagi case-use i pomocnicza geografia/populacja nadal planned według docs/specs/polish-case-usage-priors.md, bez wdrożonych wag. Nie są samodzielną naprawą tego przykładu gramatycznego.

## 6. Zweryfikowane / nieweryfikowane
Odczytano z GitHub aktualne HerbertLiveRuntime.kt, HerbertFormGroup.kt i niezmieniony verbatim fixture polish-surface-family-v5.json na code SHA.
Praca/pracą mają lexicalReadings lemma Praca (nazwa_geograficzna)/praca (nazwa_pospolita), partOfSpeech subst i surfaces. Te wpisy fixture NIE zawierają tagów przypadku ani źródłowych wag użycia.
Brak reprodukcji na oryginalnym modelu w tej sesji. Brak wyników SI, czasu, przyczyny fallbacku, ścieżki swipe oraz dokładnego pełnego kontekstu telefonu dla zgłoszonej próby. SI-vs-geometric przyczyna pozostaje nieustalona. Nie włączono logowania prywatnego tekstu.
CI zgodność/tokenizer i mocked routing nie są dowodem poprawności językowej.

## 7. Gałęzie i historia
trial/herbert-live-v1 i draft https://github.com/jakamilek/CleverKeysPL/pull/4 zachowują kod. Main obu repo dostają wyłącznie dokument.
Poprzedni checkpoint: docs/PROJECT_MILESTONE_2026-10-10_COMPACT_CASE_APK_READY.md. Nie nadpisywać wcześniejszego etapu CI-repair.

## 8. Artefakty i integracja
Live run38040432033 i standard38040436247 SUCCESS na 3f48e456f0d8f411e80be3857f1846e4b2cd139e, odczytane w poprzednim etapie: 2881 pure/195 live/300 standard integration PASS (overlap).
APK artifact11665712630: https://github.com/jakamilek/CleverKeysPL/actions/runs/38040432033/artifacts/11665712630.
ZIP digest9064c0a0190404e9c7edfb00ceffd6ef832f5988a56bec296210783010a4aa52; APK CI SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. APK nie re-hashowano lokalnie.
Oryginalny model SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2. Pack/model/APK bez nowych zmian w tym etapie.

## 9. Ograniczenia i luki
Dostępna poprawna forma Top2 nie oznacza poprawnego wyboru Top1. „Dużo lepiej” nie oznacza akceptacji wszystkich przypadków.
Nie powielać błędu: kapitalizacja właściwej nazwy i poprawny przypadek to osobne decyzje.
Pozostają historyczne około2132MiB PSS, 234 warning lint i backlog pokrycia swipe: dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie, pozdrawiam, kapitalizacją/kapitalizacje. Szczegóły w APK-ready.

## 10. Następny krok
Reprodukcja i niezależny pomiar gramatyczny rzeczywistych wyników SI, z rozróżnieniem fallbacku, przed zmianami runtime/wag. Dopiero na tej podstawie decyzja o ogólnej kontroli odmiany i zakresie metadanych.
Zachować limit60s total monitorowania Actions. Brak nowego CI, bo ten etap to wyłącznie dokumentacja.

## 11. Różnica
APK-ready/pending phone zastąpiono częściowym pozytywnym feedbackiem oraz konkretną porażką Top1 odmiany. Zapisano zweryfikowany zakres wykorzystania metadanych i brak potwierdzonej przyczyny SI-vs-fallback. Żadnych nowych zmian kodu ani danych.
