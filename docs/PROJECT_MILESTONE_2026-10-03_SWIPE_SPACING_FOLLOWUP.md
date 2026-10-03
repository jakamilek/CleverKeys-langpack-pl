# Kamień milowy — zgłoszenie z telefonu i pełna ścieżka gestu (2026-10-03)

Stan: zgłoszenie z telefonu pozostaje nierozwiązane; potwierdzoną lukę kodu poprawiono na gałęzi próbnej. Debug build i 2907 testów PASS; weryfikacja poprawki na telefonie oczekiwana.
Repozytoria partnerskie: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_SWIPE_SPACING_FOLLOWUP.md) i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-03_SWIPE_SPACING_FOLLOWUP.md).

## 1. HEAD main i data weryfikacji
GitHub, 2026-10-03, przed zapisem tego dokumentu:
- CleverKeysPL: 6a5ada690334ce33a26758ec4f0b50355f572277.
- CleverKeys-langpack-pl: eb1840a925f75fc351e69d67de325d3752a05487.
Zapis kamienia zmienia wyłącznie dokumentację na main, bez promocji kodu próbnego.

## 2. Architektura
PL nadal używa geometric. Jeden klucz CKDT może dostarczać źródłowe formy z opcjonalnego sidecara API-v1; CKDT i producent paczki nie zmieniły się.
Shift edytuje pierwszy znak istniejącego słowa po powrocie kursora. Reguły odstępów i interpunkcji pozostają deterministyczne, niezależne od AI.
Pełna ścieżka gestu teraz pozostawia decyzję o obu odstępach wspólnemu onSuggestionSelected/EditorSpacingPolicy zamiast osobnego commitText(" ").

## 3. Ustalenia zaakceptowane
Obowiązują ustalenia poprzedniego kamienia: te same preferencje przed/po dla gestów i kliknięć; wyjątki hasło/wyszukiwanie/URI/email/liczby; Shift zachowujący kursor.
Użytkownik wycofał uwagę o uzupełnieniach przy klikaniu liter — nie zmieniono tego mechanizmu.
Wcześniejsza jakościowa pochwała par form nie zamyka nowszego zgłoszenia słabego działania.

## 4. Odrzucone lub odłożone
Nie uznajemy przejścia testów JVM/mock za potwierdzenie poprawnego zachowania na telefonie.
Nie przypisujemy przyczyny sklejeń, zmian pozycji ani braku par konkretnej wersji APK, ustawieniu lub paczce bez dowodu.
Nie zmieniono na ślepo maszyny stanów Shifta ani synchronizacji kursora.
AI, CTC dla PL, duplikaty CKDT i ręczne opisy znaczeń nadal poza tym etapem.

## 5. Plan, ale jeszcze niewdrożone
Pełne metadane słownika i dalsze modelowanie kontekstu pozostają odrębne.
Promocja do main wymaga osobnej decyzji; nie wykonano merge, tagu, release ani zmiany wersji.
Jeżeli nowy zapis wskaże błąd opóźnionych callbacków, należy odtworzyć konkretną sekwencję i dopiero poprawić jej obsługę.

## 6. Niezweryfikowane
Aktywny APK/paczka/provider/ustawienia i działania użytkownika między gestami w zgłoszonym logu.
Rzeczywiste sklejenie tekstu vs nieaktualny stan trackera, zachowanie Shifta i alternatyw na urządzeniu.
Nowa poprawka i diagnostyka na telefonie; testów instrumentacyjnych nadal nie wykonywano.
Terminal, opóźnienia i wyszukiwanie nieoznaczone prawidłowym EditorInfo pozostają ograniczeniami.

## 7. Gałęzie i role
- Runtime docs/source-variants-integration-v1, draft [PR #1](https://github.com/jakamilek/CleverKeysPL/pull/1): c272f9ec1787310c69b681b8ef7dd0a7fdbfa813 — poprawka i diagnostyka.
- Producent feature/source-variants-trial-v1, draft [PR #5](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/5): niezmieniony HEAD 75a06570cc9eaac72f1e7c4376a4efd068be73fb.
- Poprzedni przetestowany runtime: b373391c88de57edacd7ad2d0ad4ea8b62e23985; 04fe5aef5cd2d037383db3e6b836d72edf292436 dokumentował jego wyniki.

## 8. SHA, artefakty i integracja
Poprawka c272f9ec1787310c69b681b8ef7dd0a7fdbfa813; [CI 37133110865](https://github.com/jakamilek/CleverKeysPL/actions/runs/37133110865).
Debug assemble PASS; 2773 pure PASS; mock: import 45, swipe 12, partial replacement 11, Shift 20, pointers 9, bridge 3, slider 5, odstępy 15, double-space 3, dropped-space repair 11 — wszystkie PASS. Razem 2907 testów.
[APK artifact 11277678542](https://github.com/jakamilek/CleverKeysPL/actions/runs/37133110865/artifacts/11277678542), 96876869 bajtów; wygasa 2026-10-10T15:33:49Z.
Digest ZIP z metadanych GitHub: sha256:d04ae983d463345c9c43105a1af8fdf645749d11f6e44ef4c20ca54fd49789bc. To nie SHA pojedynczego APK ani lokalna weryfikacja pobranych bajtów.
Runtime HEAD po zapisie wyników: 995b7116f224d4308706904321adb6aa7eb4331e — tylko dokumentacja względem przetestowanego c272f9ec.
Trial pack SHA-256 niezmieniony: 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7.
CKDT SHA-256: 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20.
Trial marker swipe-spacing-v2 pokazuje identyfikator aplikacji zarówno na ekranie, jak i w logu IME.
Linia IME: before/after, format, language, provider i liczba exactForms — bez tekstu edytora.
EDIT zapisuje wyłącznie zmiany w jawnym polu placu testowego: początek, liczby usuniętych/wstawionych znaków i maksymalnie 120 wstawionych znaków; ␠/⏎/⇥ pokazują odstępy.

## 9. Znane luki i ograniczenia
Potwierdzona luka poprzedniego kodu: gdy tracker miał bieżące słowo, wrapper gestu bezwarunkowo dopisywał osobną spację. Omijał preferencję przed słowem i wyłączenia dla pól. Ta operacja została usunięta.
Pięć nowych testów prowadzi pełną ścieżkę handleSwipePredictionResults z żywym buforem edytora: po wpisanym słowie, przed=false, wyszukiwanie, hasło opt-in i istniejąca spacja przy starym trackerze. Nie symulują całego Androidowego cyklu opóźnionych callbacków.
Log użytkownika zawiera prefix łódźłodzi i łódźłodzijuror oraz brak par Łódź/łódź i Łodzi/łodzi. Ranking placu zapisuje już listę po rozszerzeniu wariantów — nie jest wyłącznie surowym rankingiem dekodera.
Opóźniony log kursora może zestawiać pozycję przechwyconego callbacku z późniejszym tekstem; synchronizeWithCursor może też pominąć odczyt przy expectingSelectionUpdate. Sam log nie ustala dokładnej chronologii edycji.
Cały workflow pozostaje czerwony: debug lint ma ten sam ProduceStateDoesNotAssignValue w SubkeyAssignActivity.kt:148 (1 błąd, 210 ostrzeżeń); release lint pominięty. Security: te same 4 HIGH devalue 5.8.1 w site/bun.lock. Code Quality PASS. Nie osłabiono bramek.

## 10. Następny krok techniczny
Zainstalować nowy APK i sprawdzić w zwykłym polu kolejno same gesty, potem wybór alternatywy, potem powrót kursora i Shift.
Zebrać log z markerem swipe-spacing-v2, liniami EDIT i metadata IME oraz opisem czynności między słowami. Sprawdzić, czy oba warianty są widoczne na rzeczywistym pasku.
Dopiero na tej podstawie odtworzyć pozostałą usterkę. Zgłoszenie pozostaje otwarte, nie promować PR na podstawie samego CI.

## 11. Różnica względem poprzedniego kamienia
Poprzedni: docs/PROJECT_MILESTONE_2026-10-03_SHIFT_AND_SPACING.md w obu repozytoriach.
Nowe: negatywny raport z telefonu, wykryta luka wrappera, jej poprawka, pięć testów pełnej ścieżki i diagnostyka oddzielająca edycje od logów kursora.
Korygujemy wcześniejszą uwagę z rozmowy: ranking placu powinien obejmować warianty; brak par wymaga diagnozy aktywnego providera, nie wyjaśnienia „surowym rankingiem”.
