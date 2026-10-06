# HerBERT: źródłowe grupy form — CI rozpoczęte
Weryfikacja: 2026-10-06, 19:47 UTC.

## 1. Zweryfikowane main przed zapisem
- CleverKeysPL: a10a083e90306b75df7c0926e4e0842ca4105353.
- CleverKeys-langpack-pl: 309cc59854937b36130650087830a33f438677ed.
Ten dokument jest zapisywany identycznie na obu main jako checkpoint wyłącznie dokumentacyjny. Kod pozostaje na gałęzi testowej. Dokument nie podaje własnego przyszłego SHA jako zweryfikowanego HEAD.
Odpowiedniki: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-06_HERBERT_FORM_GROUP_CI_STARTED.md) oraz [producent](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-06_HERBERT_FORM_GROUP_CI_STARTED.md).

## 2. Architektura
Geometric rozpoznaje słowa. SwipeSurfaceVariants przedstawia pierwszy klucz i opcjonalnie jeden z pierwszych pięciu już rozpoznanych kandydatów tego samego polskiego języka, o identycznej pisowni po usunięciu polskich diakrytyków. Maksymalnie dwa klucze / cztery pisownie potwierdzone w sidecarze. To bliskość pisowni, nie dowód wspólnego lematu (np. laska/łaska).
HerbertFormGroup i HerbertLiveSlate porządkują wyłącznie grupę, przenosząc z każdym słowem jego wagę geometryczną, język i exact-case. Reszta listy zachowuje kolejność. Alternatywy są obok siebie również bez SI.
HerbertLiveRuntime używa tego samego zweryfikowanego FP32, oryginalnego tokenizera, średniego logp całego zamaskowanego słowa, jednej sesji/wykonawcy i obowiązkowej zgodności natywnej. SuggestionHandler zachowuje pojedyncze wstawienie przed limitem lub powrót do bazowej kolejności, bez późniejszej podmiany.

## 3. Zaakceptowane
Po pozytywnej próbie v1 użytkownik zgłosił Malina zamiast Maliną przy „jutro będę widział się z”. Zatwierdził implementację ograniczonej grupy. Autentyczny v5 zawiera malina/Malina oraz maliną/Maliną: problem dotyczył zakresu przekazywanych kandydatur.
Kontekst32 / opcje16,32,64 / limit350 ms i SI domyślnie wyłączona pozostają. Shift/Caps/początek zdania/zastosowana preferencja, prywatne pola, tożsamość edytora/tekstu/ustawień/modelu, timeout i następne dotknięcie zachowują dotychczasowe zabezpieczenia. BS i haptyka w tym rozszerzeniu niezmienione.

## 4. Odrzucone
Bez zdublowanych wpisów w słowniku, ręcznych opisów znaczeń, wymyślonych odmian ani skanowania całego słownika w poszukiwaniu podobnych słów. Bez dodawania surowego logp do wag geometrycznych. Historyczne INT8 / bezpieczny margines mniejszych modeli pozostają nieudane, nie zostają nadpisane tym wdrożeniem.

## 5. Plan niewdrożony
Globalna naprawa pokrycia swipe: dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz, poczekaj, podpowie, pozdrawiam. Dalej osobne czasy stacjonarnego BS, interpunkcja SI, pozostałe tłumaczenia. Polski i bazowy opis SI uaktualnione.

## 6. Niezweryfikowane
Nowe testy Kotlin/Android, kompilacja, lint i APK wymagają bieżącego CI. Nie ma lokalnego SDK/kompilatora Kotlin. Przeszły lokalne kontrole XML, YAML/osadzonego Pythona i JSON; 18 nowych blobów Git zweryfikowano przed commitem.
Dodano 11 regresji w już zarejestrowanych klasach: rzeczywisty sidecar v5/pokrycie/limity, przenoszenie wag i języków, stare pary, błędne i niepełne wyniki, aktualność/timeout/jednorazowość, wejścia czterech form oryginalnego tokenizera oraz rzeczywisty handler przed commit / SI off / późny callback.
To nie ocena trafności HerBERTa. Jakość między różnymi kluczami i różną liczbą tokenów, czas, energia i PSS czterech form na telefonie pozostają niezmierzone.

## 7. Gałęzie
Runtime trial/herbert-live-v1: 1f32967362917ae60c42f9e116f96fd47ed9b097; rodzic aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d; drzewo440660c932005cd3a41a57fb6fc61d319d02dc12.
[Draft PR4](https://github.com/jakamilek/CleverKeysPL/pull/4) obejmuje również wcześniejszą zaakceptowaną bazę, nie tylko ostatnią zmianę. Nie scalać, nie wydawać, nie zmieniać wersji bez osobnej autoryzacji. Producent: bez zmian danych/modelu.

## 8. Artefakty i integracja
Nowe runy na dokładnym commicie: [live37521468585](https://github.com/jakamilek/CleverKeysPL/actions/runs/37521468585) i [CI37521486297](https://github.com/jakamilek/CleverKeysPL/actions/runs/37521486297), przy sprawdzeniu in_progress. Nie ma jeszcze potwierdzonego nowego APK. Tożsamość przyszłego artefaktu: case-family-v2, maxLiveSurfaces4, familySearchCandidates5.
Poprzedni APK aebe6afd: live37512331919 i standard37512337696 PASS, 2857 pure oraz188 live-mock; telefon ogólnie pozytywny, zgłoszona luka Maliną.
[Poprzedni artefakt11436446299](https://github.com/jakamilek/CleverKeysPL/actions/runs/37512331919/artifacts/11436446299), ZIP SHA b1f8dc0d1ec8697c62fc0bcc88981214d749a8dd574464478ec751ffa9ae5cf7, APK SHA z CI 76f38752684c5502992ecdb5854bbd32d0c643df3efa6e1a35e39c6119f28c6a. Brak niezależnego lokalnego rehash APK (limit pobrania32MiB).
Model producenta d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c / run37230171787 / artefakt11312693984 bez zmian; model SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
Źródło testowego podzbioru sześciu wpisów: v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb, pełny sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d. Same obiekty wpisów i proweniencja, bez ręcznych opisów.

## 9. Ograniczenia
Cztery formy nie mieszczą się wszystkie w Top3. Cel: właściwa forma w Top3, nie gwarancja. Brak drugiego klucza w pierwszych pięciu lub jego źródłowych pisowni oznacza brak rozszerzenia. łódź→łodzi wymaga innych liter i nie jest objęte tą regułą. Kolejność bazowa może przesunąć niespokrewniony kandydat za grupę; jego waga i względna kolejność poza grupą pozostają.
FP32: poprzedni pomiar całego procesu ~2132 MiB PSS i duży koszt przy wczytaniu. Nie ma dowodu, że cztery formy mają koszt dwóch ani że przy długim kontekście zmieszczą się w350ms. Normalizacja średnią nie gwarantuje porównywalnej trafności między formami.

## 10. Następny krok
Po informacji użytkownika o zakończeniu runów zweryfikować dokładny commit, wszystkie wymagane bramki i tożsamość nowego artefaktu. Następnie próba „Jutro będę widział się z Maliną” / „Ciasto smakuje maliną”, formy łódź/Łódź, SI off, szybkie kolejne gesty, timeout, prywatne pola. Osobno kolejność wstawienia/paska i liczniki czasu/fallback. Instrukcja w runtime docs/HERBERT_LIVE_TRIAL_V1.md. Monitorowanie Actions najwyżej60s na run; teraz przerwane po pierwszym odczycie, użytkownik zgłasza zakończenie.

## 11. Różnica
Poprzedni PROJECT_MILESTONE_2026-10-06_PHONE_CASE_FAMILY_GAP.md opisywał propozycję i lukę pierwszej pary. Teraz użytkownik zatwierdził rozszerzenie, kod zapisano i dwa CI rozpoczęte. Producent/słownik/wagi modelu bez zmian; nie ma jeszcze nowego potwierdzonego APK ani próby czterech form na telefonie.
