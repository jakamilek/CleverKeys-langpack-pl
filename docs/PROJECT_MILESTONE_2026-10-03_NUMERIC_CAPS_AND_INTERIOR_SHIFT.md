# Kamień milowy — kapitalizacja po liczbie i Shift wewnątrz słowa (2026-10-03)

Stan: poprawka na gałęzi próbnej, weryfikacja telefonu oczekiwana. Debug build i 2931 testów PASS; całe CI nadal blokują wcześniejsze bramki lint/security.
Dokumenty partnerskie: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_NUMERIC_CAPS_AND_INTERIOR_SHIFT.md) i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-03_NUMERIC_CAPS_AND_INTERIOR_SHIFT.md).

## 1. HEAD main i data
GitHub, 2026-10-03, przed zapisem tego dokumentu:
- CleverKeysPL: f349f5cda8471df1994805045c4f6f2c74ce3e81.
- CleverKeys-langpack-pl: d76c4738f1d252e8c554897cbd84865d0fa065f0.
Zapis na main dotyczy wyłącznie dokumentacji, nie promocji kodu z próby.

## 2. Architektura
PL nadal geometric; jeden CKDT klucz i opcjonalne źródłowe formy sidecara API-v1. Paczka i producent bez zmian.
Shift korzysta z planu zmiany pierwszego znaku oraz sesyjnego śledzenia kursora. Znana mutacja kapitalizacji jest teraz odróżniana od zwykłego wpisywania niezależnie od gotowości do kolejnego przełączenia.
Autocapitalisation używa wspólnej reguły granicy po liczbie zakończonej kropką, dla gestu i klikanych liter. SmartAutoSpace nie zmienia sposobu wpisywania separatorów dziesiętnych.

## 3. Ustalenia zaakceptowane
Użytkownik ocenia v2 jako „dużo lepiej”; załączony log identyfikuje debug APK, language=pl/provider=true i parę łodzi/Łodzi (exactForms=2).
Użytkownik zgłasza brak wielkiej litery po 3. i wybiórczy Shift zależny od pozycji kursora.
NOWA KOREKTA: Shift ma działać wewnątrz słowa przy każdej pozycji po pierwszej i przed ostatnią literą; za ostatnią literą ma zachować zwykłą funkcję. Poprzednia zgoda na edycję z pozycji za słowem jest nieaktualna.
Początek słowa pozostaje obsługiwany; zaznaczony zakres, pola prywatne/techniczne i tryby inline nadal nie są przekształcane.
Wcześniejsze ustawienia odstępów i wycofanie uwagi o prefiksach obowiązują.

## 4. Odrzucone / odłożone
Nie dodano AI, CTC dla PL, duplikatów CKDT ani ręcznych opisów znaczeń.
Nie formatujemy każdej kropki po cyfrze natychmiast jako końca zdania, bo przerwałoby to wpisywanie 3.4.
Nie traktujemy braku EDIT w logu jako dowodu naciśnięcia Shifta w danej pozycji; akcje Shift nie są bezpośrednio rejestrowane.
Nie uznajemy sukcesu testów mock za zamknięcie zgłoszenia telefonu.

## 5. Plan, ale niewdrożone
Pełne metadane słownika, dalszy kontekst/AI i fleksja nadal osobne etapy.
Promocja/release/tag/zmiana wersji wymagają osobnej decyzji i nie zostały wykonane.
Cały cykl Androidowych callbacków nie jest emulowany; gdy pozostaną objawy, odtworzyć konkretne zdarzenia zamiast ogólnie zmieniać tracking.

## 6. Niezweryfikowane
Zachowanie nowego APK na telefonie, w różnych edytorach i z klawiszową nawigacją kursora.
Brak końcowego callbacku po batch edit jest odtworzonym przypadkiem kodu/testu, ale sam dostarczony log nie dowodzi, że jest jedyną przyczyną wybiórczości.
Nie wykonano emulatora/instrumentacji, testu minifikowanej wersji ani pomiaru opóźnień.

## 7. Gałęzie / rola
Runtime docs/source-variants-integration-v1, draft [PR #1](https://github.com/jakamilek/CleverKeysPL/pull/1): 6122bf9b66ef16cc966872883ae5b25c5c108a04, nowy kod.
Producent feature/source-variants-trial-v1, draft [PR #5](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/5): bez zmian, HEAD 75a06570cc9eaac72f1e7c4376a4efd068be73fb.
Poprzedni v2: c272f9ec1787310c69b681b8ef7dd0a7fdbfa813; 995b7116f224d4308706904321adb6aa7eb4331e dokumentował jego wyniki.

## 8. Artefakty, SHA i integracja
[CI 37140569285](https://github.com/jakamilek/CleverKeysPL/actions/runs/37140569285), kod 6122bf9b66ef16cc966872883ae5b25c5c108a04.
Debug assemble PASS; 2779 pure PASS; mock: import 45, swipe 15, autocapitalisation 14, partial replacement 11, Shift 21, pointers 9, bridge 3, slider 5, odstępy 15, double-space 3, dropped-space repair 11 — wszystkie PASS. Razem 2931 testów.
[APK artifact 11280003851](https://github.com/jakamilek/CleverKeysPL/actions/runs/37140569285/artifacts/11280003851), 96879857 bajtów, wygasa 2026-10-10T17:37:04Z.
Digest ZIP z metadanych GitHub: sha256:62f6c6f76380609481b7a5f420268639dde223bf18aaa953ddaf9bfeb304e0a9; nie jest to SHA pojedynczego APK ani lokalna weryfikacja bajtów.
Runtime HEAD po zapisie wyników: 7e09e4c07dc7eea7d254cd9ef833f0e9162a3764 — tylko dokumentacja względem przetestowanego kodu.
Marker cursor-caps-v3; nadal EDIT, metadata ustawień/provider oraz nowe autocap/capAtCursor.
Trial pack SHA-256: 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20 — bez zmian.
Specy runtime: docs/specs/cursor-word-capitalization.md i docs/specs/editor-spacing.md.

## 9. Ograniczenia i luki
Poprzedni guard oczekiwał potwierdzenia po zmianie litery. Gdy edytor nie wysłał końcowego callbacku dla niezmienionej pozycji w batchu, następny ruch z tego kursora był pomijany. Guard dla starego odczytu przy zwykłym wpisywaniu zachowano; wyłączono go tylko dla znanej mutacji kapitalizacji.
Plan Shifta jawnie odrzuca pozycję za ostatnią literą. Testy obejmują wszystkie pozycje w łódź/malina/warszawska/znowu, zachowanie sufiksu i kursora, brak finalnego callbacku oraz rozbrojenie przez klawisz kursora.
Po cyfrze kropka nadal literalna; po dodanej spacji albo przy prośbie o następny wyraz z włączoną spacją przed reguła rozpoznaje liczbową granicę zdania. Wymaga ustawienia autocap, CAP_SENTENCES i zwykłego pola. Nie obejmuje 3.4, 3,4, tokenów technicznych, nieznanego kontekstu ani search/password.
Pole placu dotąd było inputType=text bez CAP_SENTENCES, co ograniczało testowanie kapitalizacji. Teraz zgłasza text|textCapSentences. Nie wymuszamy kapitalizacji w innych polach, które nie zgłaszają jej flag.
Pełne CI czerwone: ten sam ProduceStateDoesNotAssignValue w SubkeyAssignActivity.kt:148 (1 błąd, 210 ostrzeżeń), release lint pominięty; security te same 4 HIGH devalue 5.8.1 w site/bun.lock. Code Quality PASS. Nie wyłączono bramek.

## 10. Następny krok
Test cursor-caps-v3 na telefonie: 3. + gest, 3. + ręczna spacja + litery, 3.4 + słowo; każdy wewnętrzny punkt kursora po kolejnych zmianach Shiftem; za słowem zwykły Shift.
Jeżeli coś nadal zawiedzie, zebrać EDIT/autocap/capAtCursor z krótkim opisem naciskanych klawiszy i pozycji. PR pozostaje próbny.

## 11. Zmiana względem poprzedniego kamienia
Poprzedni: docs/PROJECT_MILESTONE_2026-10-03_SWIPE_SPACING_FOLLOWUP.md.
Nowe: pozytywny raport v2 i potwierdzenie PL providera/par; dwa zawężone zgłoszenia; korekta wymagania dla pozycji za słowem; poprawka oczekiwania na callback po zmianie litery; liczbowy fallback kapitalizacji; prawidłowa flaga kapitalizacji zdań w placu i dodatkowe testy.
