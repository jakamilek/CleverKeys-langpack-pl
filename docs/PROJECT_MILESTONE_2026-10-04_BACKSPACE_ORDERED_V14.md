# Backspace: uporządkowane granice zaznaczenia dla edytorów — v14

## 1. Zweryfikowany stan i data
2026-10-04. Przed zapisaniem tego kamienia main CleverKeysPL:
521470f78bf1b39b3a977e9fe421d669d815665d; main CleverKeys-langpack-pl:
0edbd3762055c7354d1d57709882241d51bb590e. Oba mainy otrzymują wyłącznie ten dokument
ciągłości. Runtime trial docs/source-variants-integration-v1 przesunięto fast-forward
z 9582257fd7deeb849f0c97550babdd01708799fa do
95f302c1d528bd9d006e5660697f6a307b983ce2. Draft PR #1 pozostaje otwarty.
Wszystkie osiem zmienionych blobów zweryfikowano względem lokalnych plików.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_BACKSPACE_ORDERED_V14.md)
oraz [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_BACKSPACE_ORDERED_V14.md).

## 2. Architektura
Trzy operacje Backspace przekazują edytorowi setSelection(start, end) z start <= end:
pierwszy podgląd słowa/start DRAG, przesunięcie DRAG oraz podgląd następnego słowa
w cyklu przytrzymania. Prawa kotwica pozostaje w BackspaceHold, niezależnie od
kolejności argumentów API. Logiczny zakres zaznaczenia pozostaje taki sam.
Wspólny SliderMotion ze spacją, czułość i dynamika v13 pozostają bez zmian.
Cykl słów zachowuje 350 ms podglądu i 200 ms przerwy. Guards edytora, tekstu,
zaznaczenia i potwierdzania zmian nadal obowiązują.

## 3. Zaakceptowane ustalenia
Użytkownik zaakceptował dynamikę v13: „teraz działa to bardzo dobrze”.
Zgłosił osobny problem w SimpleX: gest zatrzymuje się na zaznaczeniu spacji przed
słowem. V14 jest próbą poprawy zgodności tego przypadku, wymagającą testu na telefonie.
Sterowanie palcem, usuwanie po puszczeniu według ustawienia i cykl przytrzymania
zachowujemy. Priorytet interfejsu pozostaje polski.

## 4. Rozwiązania odrzucone
Nie dodajemy wyjątków po nazwie aplikacji, nie obchodzimy guards ani nie wysyłamy
niezweryfikowanego DEL. Nie zmieniamy dynamiki zaakceptowanego gestu.
Nie traktujemy modelu edytora w teście jako testu prawdziwego SimpleX.
Bez merge, tagu, release, zmiany wersji aplikacji ani promocji trial do main.

## 5. Niewdrożone plany
AI/CTC i ranking kontekstowy pozostają osobnym etapem. Osobne suwaki czasów 350/200 ms
pozostają planem. Backlog opisów współdzielonego ruchu w innych językach z v13
pozostaje w memory/todo.md; nie zmieniono tłumaczeń ani ustawień w v14.

## 6. Weryfikacja i jej granice
Lokalne PASS: git diff --check; skan trzech uporządkowanych operacji i braku trzech
starych odwróconych operacji; generator wyszukiwarki ustawień — 145 wpisów;
frozen Bun 1.3.11 install; Astro — 84 strony; 50 wewnętrznych odnośników wiki/spec
na dwóch zmienionych stronach. package.json i lockfile bez zmian.
Osiem zdalnych blobów zgadza się z lokalnymi; nowe drzewo:
ccf9399ad0ec036dd690786341b9a5c9d0633983.

BackspaceHoldTest ma teraz 39 przypadków, o trzy więcej niż w v13.
Dodane regresje modelują edytor normalizujący granice, który przy odwróconym żądaniu
może ponownie ustawić pole i zmienić InputConnection. Obejmują podgląd i drag,
przejście przez spacje przed/po słowie, cofanie zaznaczenia, usunięcie właściwego
zakresu oraz kolejne podglądy/usunięcia trzech słów. To model zgodności, nie test
zainstalowanego SimpleX. Zestaw jest już zarejestrowany w skupionym CI.

[CI run 37199887090](https://github.com/jakamilek/CleverKeysPL/actions/runs/37199887090)
w jednym odczycie miał in_progress dla dokładnego 95f302c1d528bd9d006e5660697f6a307b983ce2.
Nie potwierdzono jeszcze wyników Androida, testów, lint ani nowego APK.
Lokalnie brak Android/Kotlin toolchaina. Monitorowanie zakończono po około
0,93 sekundy; kolejny odczyt dopiero po zgłoszeniu użytkownika. Limit pozostaje
60 sekund łącznie na build. Test telefonu v14 oczekuje.

## 7. Gałęzie i historia
Runtime trial pozostaje na docs/source-variants-integration-v1 i draft PR #1.
V13 przeszedł run 37192552115: 2801 pure JVM + 248 skupionych = 3049 testów,
assembleDebug, lint debug/release, Code Quality, gate fixed HIGH/CRITICAL i
APK Size Analysis. BackspaceHoldTest miał 36 przypadków, PointersBackspaceHoldTest 26.
Upload raportów nie znalazł build/reports/tests/; liczby potwierdziły logi JUnit.
Użytkownik zaakceptował v13 ogólnie, zgłaszając wyjątek SimpleX.
Te wyniki nie potwierdzają nowego v14.
Producer feature/source-variants-trial-v1 pozostaje na
bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f. Generator i langpack bez zmian.

## 8. Artefakty i integracja
Commit runtime 95f302c1d528bd9d006e5660697f6a307b983ce2; rodzic
9582257fd7deeb849f0c97550babdd01708799fa. Marker: backspace-ordered-v14.
Osiem zmienionych plików: KeyEventHandler.kt, BackspaceHoldTest.kt,
SuggestionHandler.kt, AGENTS.md, docs/TABLE_OF_CONTENTS.md, memory/todo.md
oraz przewodnik i specyfikacja selection-delete.
Nowy APK v14 nie został jeszcze potwierdzony.
Historyczny [APK v13, artifact 11299851311](https://github.com/jakamilek/CleverKeysPL/actions/runs/37192552115/artifacts/11299851311)
ma 97024300 bajtów; digest ZIP:
sha256:07716ecd6f6a8a3ce9974fc324add39d23e52d73de5cd3e304d2e4c406f61e85,
wygaśnięcie 2026-10-11T09:40:40Z. To nie jest artefakt nowej poprawki.
Pochodzenie packa pozostaje w kamieniu kapitalizacji funkcji słów.

## 9. Ograniczenia i hipoteza zgodności
Sprawdzono pierwotny kod SimpleX na stable commit
479548ee53ffb73db73841e77acbeee5a78dbbd5:
[PlatformTextField.android.kt](https://github.com/simplex-chat/simplex-chat/blob/479548ee53ffb73db73841e77acbeee5a78dbbd5/apps/multiplatform/common/src/androidMain/kotlin/chat/simplex/common/platform/PlatformTextField.android.kt).
onSelectionChanged porządkuje granice min/max. Aktualizacja AndroidView porównuje
stan tekstu i zaznaczenia z widokiem, a przy rozbieżności wywołuje setText oraz
setSelection. Wcześniejsze odwrócone żądania BS mogą prowadzić do resynchronizacji
i zatrzymania sesji przez guards. To hipoteza oparta na źródle, nie potwierdzona
przyczyna błędu użytkownika. Wersja zainstalowanego SimpleX nie jest znana;
wersję przypiętego źródła sprawdzono względem odczytanego kodu.

Uporządkowany zakres zaznacza te same znaki, lecz aktywny koniec zaznaczenia może
wpływać na przewijanie widoku — wymaga kontroli w długim/wielowierszowym tekście.
Granica odczytu pozostaje 4096 jednostek UTF-16, ruch liczy punkty kodowe Unicode,
nie pełne klastry grafemów. Fallback pól prywatnych/technicznych, ograniczenia
separatorów i walidacja żywego tekstu pozostają. Testy hostowe nie zastępują telefonu.

## 10. Następny krok
Po zgłoszeniu zakończenia runu sprawdzić dokładny head, logi i artefakt v14.
Następnie w SimpleX wpisać „olej mleko karton ”: przeciągnąć BS przez końcową
spację, słowo i poprzedzającą spację; zatrzymać, cofnąć i ponownie zaznaczyć;
puścić i sprawdzić usunięty zakres. Sprawdzić stacjonarny cykl kolejnych słów,
przejście do DRAG oraz długi/wielowierszowy tekst i przewijanie.
Powtórzyć krótki test kontrolny w aplikacji, w której BS działał poprawnie.
Zachować limit monitorowania i nie promować trial bez odrębnego zlecenia.

## 11. Różnica wobec poprzedniego kamienia
[Poprzedni etap v13](PROJECT_MILESTONE_2026-10-04_BACKSPACE_SLIDER_V13.md)
wprowadził ruch BS taki jak na spacji i uporządkował ustawienia.
V14 zmienia kolejność granic w trzech żądaniach API edytora, dodaje trzy regresje
i zapis hipotezy SimpleX. Nie zmienia ruchu, ustawień, czasów cyklu ani langpacka.
Lokalne kontrole przeszły; CI i potwierdzenie telefonu v14 oczekują.
