# Kamień milowy — integralność tekstu po edycji (2026-10-03)

Stan: pierwsza poprawka skompilowana; dwa błędy pure CI poprawione w follow-up, jego testy i weryfikacja telefonu oczekiwane. Nie uznajemy zgłoszenia telefonu za zamknięte.
Dokument partnerski istnieje pod tym samym path na main CleverKeysPL i CleverKeys-langpack-pl.

## 1. HEAD main i data
2026-10-03, przed dokumentem: runtime b3872eeddd889ebb668854d32f99c34c846f8269; producent c73371775b09f6db9ebd26fa17bd7f004a2828c0.
Main otrzymuje wyłącznie dokumentację. Kod pozostaje w próbie.

## 2. Architektura
PL nadal geometric i jeden CKDT klucz; opcjonalne źródłowe warianty sidecara bez zmian.
SuggestionHandler posiada rewizję przewidywania dla bieżącego stanu edytora. InputCoordinator unieważnia oczekujące publikacje przed debounce 100ms. PredictionContextTracker współdzieli odczyt rzeczywistego tokenu po literze i przy synchronizacji.

## 3. Ustalenia zaakceptowane
Priorytetem jest zgłoszona regresja: po zmianie/wycięciu/wklejeniu gubione podpowiedzi, a kliknięcie dodania słowa może usunąć tekst.
ExactAdd ma dodać pełny aktualny token do słownika, bez usuwania, ponownego commitowania i przesuwania kursora; chip pierwszy w pasku. Przy niewłaściwym tokenie, zaznaczeniu lub braku odczytu stary chip jest odrzucany.
Najnowsze wymaganie ponownie obejmuje Shift za ostatnią literą słowa. Zastępuje wcześniejsze wykluczenie tej pozycji, ale zmiana kodu jest odłożona do ustabilizowania edycji.
Użytkownik wymaga maksymalnie 60 sekund ŁĄCZNIE monitorowania pojedynczej budowy, potem sam zgłasza stan. Nie uruchamiamy długiego pollingu.

## 4. Odrzucone / odłożone
Nie poszerzamy teraz zmian zachowania Backspace/Shift, nie poprawiamy Ale/Lub przez ręczne wyjątki w kodzie.
Nie diagnozujemy przyczyny zerwania połączenia z użytkownikiem bez danych aplikacji/sieci.
Nie dodano AI, CTC dla PL, duplikatów CKDT ani ręcznych opisów słownika.

## 5. Plan, ale niewdrożone
Shift na końcu słowa; krótkie Backspace cofające dostępną autokorektę, bez natychmiastowego całego-word deletion po swipe; pierwszy hold usuwa słowo, kolejne powtórzenia znaki.
Reset przewinięcia paska po Backspace i przyczyna kapitalizacji Ale/Lub pozostają pending.
Pełne metadane, dalszy kontekst/AI i fleksja są osobnymi etapami.

## 6. Niezweryfikowane
Nie ma nowego logu odtwarzającego najnowszą regresję. Dostępny Wklejony tekst.txt ma marker swipe-spacing-v2.
Nie wykazano, która ścieżka jest jedyną przyczyną telefonu. Wskazane w kodzie ryzyka są realne: cached-length deletion, brak rewizji prefix UI post, stale special prompt i pomijanie pierwszego odczytu.
Nowa kompilacja, testy, Android instrumentacja, wydajność i telefon pozostają nieweryfikowane.

## 7. Gałęzie / rola
Runtime docs/source-variants-integration-v1, draft PR1, nowy kod 0d7a1744175d29c1af12d595035b754b501c47d7, parent 7e09e4c07dc7eea7d254cd9ef833f0e9162a3764.
Producent feature/source-variants-trial-v1, PR5, HEAD 75a06570cc9eaac72f1e7c4376a4efd068be73fb — bez zmian.

## 8. Artefakty, SHA i integracja
Aktualizacja po zgłoszeniu zakończenia runów przez użytkownika: 37143267946 zakończony failure. Debug assembly i kompilacja testów PASS; pure 2779, dwa błędy (stary anchor w RELEASE_RECORD i literalny matcher M6 dla rozbudowanego warunku). Mock regresje pominięte, brak artefaktu APK. Code Quality PASS; security cztery wcześniejsze devalue HIGH.
Follow-up 383137f8a60f372215cb887c57a4c115b46a488f aktualizuje odnośnik i rozdziela istniejący guard generacji paska od dodanego guardu rewizji/hasła. Żadnej ochrony ani testu nie wyłączono. Kontrola źródła: oba guardy M6 i nowy anchor prawidłowe; readback czterech plików PASS.
Nowy CI 37143960348: https://github.com/jakamilek/CleverKeysPL/actions/runs/37143960348, rozpoczęty. Monitorowanie zakończone po odczycie startu, wynik zgłosi użytkownik. Poniższy opis poprzedniego odczytu zachowano jako historię etapu.

CI 37143267946: https://github.com/jakamilek/CleverKeysPL/actions/runs/37143267946, przypięte do 0d7a1744175d29c1af12d595035b754b501c47d7; przy odczycie rozpoczęte, bez conclusion. Monitorowanie zakończono po sprawdzeniu startu, bez oczekiwania na wynik. Nie ma jeszcze zweryfikowanego nowego APK.
Weryfikacja readback: wszystkie 13 zmienionych plików zgodne z commitem. Nowe osiem testów EditorPredictionRegressionTest oraz zaktualizowane SuggestionTapAddAndIWordTest w guarded CI.
Poprzednie debug assembly i 2931 testów PASS dotyczą 6122bf9b, nie nowej poprawki.
Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20 — bez zmian.
Marker playground editor-sync-v4. Spec docs/specs/editor-prediction-integrity.md; powiązane cursor-aware-predictions.md i work queue zaktualizowane.

## 9. Ograniczenia i luki
Dictionary-only ExactAdd nie kończy słowa ani nie dodaje spacji. Zwykłe podpowiedzi nadal mają istniejące reguły zastępowania i odstępów.
Niedostępny/wykluczony odczyt edytora zachowuje tap fallback, a stale ExactAdd jest odrzucany. Potrzebna walidacja niestandardowych edytorów.
Zaakceptowane wcześniej reguły haseł/wyszukiwania i prywatności obowiązują; nie dodano plaintext logging.
Całe wcześniejsze CI blokują SubkeyAssignActivity ProduceStateDoesNotAssignValue i cztery HIGH devalue 5.8.1 w site/bun.lock. Bramki pozostają aktywne.
Bez lokalnego Android SDK/Gradle nie deklarujemy lokalnego uruchomienia testów.

## 10. Następny krok
Użytkownik zgłasza zakończenie nowego CI 37143960348; sprawdzić testy i artefakt dla 383137f8a60f372215cb887c57a4c115b46a488f przed poleceniem APK. Poprzedni run nie dostarczył APK.
Telefon: nieznane słowo → dodaj (tekst/kursor bez zmian); zmień, wytnij/wklej inne słowo i dopisz literę; wybierz podpowiedź przy kursorze wewnątrz słowa; equal-length replacement; zwykłe swipe alternates.
W razie regresji krótki aktualny log i dokładna kolejność czynności. Nie promować kodu do main ani release przed akceptacją.

## 11. Zmiana względem poprzedniego kamienia
Poprzedni NUMERIC_CAPS_AND_INTERIOR_SHIFT dokumentował v3. Najnowsza korekta użytkownika ponownie włącza pozycję za słowem w oczekiwanym zachowaniu.
Priorytet przesunięty na ochronę tekstu i aktualność podpowiedzi; ExactAdd przestaje modyfikować pole, używa pełnego live tokenu i pierwszego miejsca; kolejkowane wyniki mają guard rewizji, a synchronizacja nie pomija odczytu po oczekiwanym callbacku.
Ograniczono monitorowanie Actions zgodnie z instrukcją użytkownika. Upstream issues odczytane bez interakcji; brak komentarzy.
