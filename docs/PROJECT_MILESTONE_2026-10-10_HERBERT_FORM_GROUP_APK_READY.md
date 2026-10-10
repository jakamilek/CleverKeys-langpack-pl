# HerBERT: źródłowe grupy form — APK po udanym CI
Wyniki CI odczytane: 2026-10-06. Dokończenie zapisu i ponowna weryfikacja HEAD, runów i dostępności artefaktu: 2026-10-10.

## 1. Zweryfikowane main przed zapisem
- CleverKeysPL: 19e9e1027c63a1dd1dd13e3ed3a7d2d9d10f449e.
- CleverKeys-langpack-pl: 271259bf39ff3f18b40ccd67d2db49b4dba7cc04.
Ten dokument jest zapisywany identycznie na obu main jako checkpoint wyłącznie dokumentacyjny. Kod pozostaje na gałęzi testowej. Dokument nie podaje własnego przyszłego SHA jako zweryfikowanego HEAD.
Odpowiedniki: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_GROUP_APK_READY.md) oraz [producent](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-10_HERBERT_FORM_GROUP_APK_READY.md).

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

## 6. Zweryfikowane CI i pozostałe niewiadome
Oba runy na dokładnym 1f32967362917ae60c42f9e116f96fd47ed9b097 zakończone SUCCESS.
Live37521468585 /job112467677883: rzeczywista kompilacja Androida, 2865 pure PASS; oryginalny marker 2471 token vectors /232 batches /532 candidates /five inputs PASS, także nowy test wejść czterech form. Dziewięć klas mock191 PASS: LanguagePackImport45, SwipeAutocapCommit23, EditorPredictionRegression8, SuggestionTapPartialReplace11, SuggestionStripScroll3, BackspaceHold45, PointersBackspaceHold26, BackspaceHapticRouting1, LearningFunnelBookkeeping29.
Standard37521486297: build, 2865 pure, 18 klas integracyjnych296, debug/vital lint, security, code quality i size PASS. Wyniki wspólnych testów nie są sumowane między runami.
Lokalnie pobrany reportsZIP22420B ma SHA zgodne z GitHub: 8fefc5362c7da660087c67e59a12997cadb409c3b43ef724315fd430838efa6e. Odczytano OK(2865) i pełny marker oryginalnych fixture. Debug lint XML:0 Error/Fatal,234 pozostałe zgłoszenia; nie oznacza braku wszystkich ostrzeżeń.
Testy rzeczywistego źródła/presentation/reordering/handler/timeout przeszły. Nie są oceną trafności modelu. Wyniki natywne telefonu dla czterech form, Top3, czas/energia/PSS pozostają niezmierzone; bieżący test JVM nie dowodzi wykonania JNI na telefonie.

## 7. Gałęzie
Runtime trial/herbert-live-v1: 1f32967362917ae60c42f9e116f96fd47ed9b097; rodzic aebe6afd82fa0d37fc40d37cd1105ad6c949cc9d; drzewo440660c932005cd3a41a57fb6fc61d319d02dc12.
[Draft PR4](https://github.com/jakamilek/CleverKeysPL/pull/4) obejmuje również wcześniejszą zaakceptowaną bazę, nie tylko ostatnią zmianę. Nie scalać, nie wydawać, nie zmieniać wersji bez osobnej autoryzacji. Producent: bez zmian danych/modelu.

## 8. Artefakty i integracja
[Live37521468585](https://github.com/jakamilek/CleverKeysPL/actions/runs/37521468585) i [CI37521486297](https://github.com/jakamilek/CleverKeysPL/actions/runs/37521486297) SUCCESS, commit1f32967362917ae60c42f9e116f96fd47ed9b097.
[Nowy artefakt11441445238](https://github.com/jakamilek/CleverKeysPL/actions/runs/37521468585/artifacts/11441445238), cleverkeys-herbert-live-trial-arm64, ZIP35802278B, SHA3d8ac60e65cc9aa3d4bc6d41a022e96f32130942cb1dacf2daa740fa42118565; wygasa2026-10-20T19:58:25Z.
APK CleverKeys-v2.0.0-arm64-v8a.apk,35801058B, SHA z CI efbbfc4c0478eea506f56ea8237175771e46cbf37691efabe93ddbe46642442c. Audyt CI potwierdził brak wag FP32 i testowych fixture w APK. Tożsamość: case-family-v2 /maxLiveSurfaces4 /familySearchCandidates5 /default32 /wait350ms /optInDefaultfalse. Suma i JSON w tym samym ZIP.
Bez niezależnego lokalnego rehash APK: ZIP przekracza limit pobierania32MiB. Report ZIP11441445242 jest lokalnie zweryfikowany; nie utożsamiać tego z rehash APK.
Poprzedni APK aebe6afd: live37512331919 i standard37512337696 PASS, 2857 pure oraz188 live-mock; telefon ogólnie pozytywny, zgłoszona luka Maliną.
[Poprzedni artefakt11436446299](https://github.com/jakamilek/CleverKeysPL/actions/runs/37512331919/artifacts/11436446299), ZIP SHA b1f8dc0d1ec8697c62fc0bcc88981214d749a8dd574464478ec751ffa9ae5cf7, APK SHA z CI 76f38752684c5502992ecdb5854bbd32d0c643df3efa6e1a35e39c6119f28c6a. Brak niezależnego lokalnego rehash APK (limit pobrania32MiB).
Model producenta d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c / run37230171787 / artefakt11312693984 bez zmian; model SHA f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
Źródło testowego podzbioru sześciu wpisów: v5 ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb, pełny sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d. Same obiekty wpisów i proweniencja, bez ręcznych opisów.

## 9. Ograniczenia
Cztery formy nie mieszczą się wszystkie w Top3. Cel: właściwa forma w Top3, nie gwarancja. Brak drugiego klucza w pierwszych pięciu lub jego źródłowych pisowni oznacza brak rozszerzenia. łódź→łodzi wymaga innych liter i nie jest objęte tą regułą. Kolejność bazowa może przesunąć niespokrewniony kandydat za grupę; jego waga i względna kolejność poza grupą pozostają.
FP32: poprzedni pomiar całego procesu ~2132 MiB PSS i duży koszt przy wczytaniu. Nie ma dowodu, że cztery formy mają koszt dwóch ani że przy długim kontekście zmieszczą się w350ms. Normalizacja średnią nie gwarantuje porównywalnej trafności między formami.

## 10. Następny krok
Aktualizacja samego APK bez zmiany źródłowego modelu i słownika. Potwierdzić SI gotowa.
Telefon: „Jutro będę widział się z Maliną” / „Deser pachnie maliną”; maznąć malina, porównać słowo wstawione i Top3 na pasku, SI on/off, możliwość wyboru pozostałych form. Grupa powstaje tylko, jeśli drugi klucz jest w pierwszych pięciu i ma dane źródłowe.
Osobno regresje łódź/Łódź, szybkie kolejne gesty, BS/Shift/zmiana pola/wytnij-wklej, prywatne pola. Czas/fallback sprawdzić przy krótkim i dłuższym kontekście bez zbierania prywatnego tekstu. Nie zwiększać arbitralnie limitu ani nie ogłaszać jakości na podstawie samego przykładu.
Instrukcja runtime docs/HERBERT_LIVE_TRIAL_V1.md. Po akceptacji aplikacji wrócić do globalnego pokrycia słownika, bez punktowych wyjątków. Nie uruchomiono następnego CI ani oczekiwania; oceniono zakończone runy po informacji użytkownika.

## 11. Różnica
Zapis przygotowany 2026-10-06 został przerwany przed publikacją checkpointu; dokończony 2026-10-10 po instrukcji użytkownika „Kontynuuj”. Main obu repozytoriów i trial zachowały zweryfikowane HEAD; nie uruchomiono nowych testów ani nowej budowy, artefakt nie wygasł.
Poprzedni PROJECT_MILESTONE_2026-10-06_HERBERT_FORM_GROUP_CI_STARTED.md miał pending compilation/test/APK. Teraz oba CI zweryfikowane SUCCESS i nowy artefakt ARM64 dostępny. Producent/słownik/model niezmienione. Telefon i niezależna jakość czterech form nadal pending. Dokument na obu main wyłącznie dokumentacyjny; kod pozostaje na trial.
