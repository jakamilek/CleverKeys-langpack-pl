# Kamień milowy — Shift i odstępy zależne od pola (2026-10-03)

Stan: wdrożenie na gałęzi próbnej; debug build i 2902 testy PASS, test na telefonie oczekiwany. Nie scalono ani nie wydano.
Repozytoria: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL) i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl).
Dokumenty partnerskie: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-03_SHIFT_AND_SPACING.md) oraz [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-03_SHIFT_AND_SPACING.md).

## 1. HEAD main i data
Weryfikacja GitHub 2026-10-03:
- CleverKeysPL main przed zapisem dokumentu: e5f341e4b19ce334bff9bb327b66db78c87fea40.
- CleverKeys-langpack-pl main przed zapisem dokumentu: 4abdc1da60e5f752f21780d7853d15a2f9e7c55b.
Zapis tego kamienia na main zmienia wyłącznie dokumentację; nie promuje kodu z gałęzi próbnej.

## 2. Architektura
PL pozostaje przy geometric. Pojedynczy klucz CKDT może mieć źródłowe formy wyświetlane z sidecara API-v1.
Nie dodano AI ani CTC dla PL. Langpack binarny i jego dane nie zmieniają się na tym etapie.
Pointers obsługuje zwykłe zwolnienie Shifta; KeyEventHandler zmienia pierwszy znak zaparkowanego słowa i zachowuje kursor.
EditorSpacingPolicy oddziela formatowanie od predykcji. SmartAutoSpace dostarcza czyste decyzje dla SuggestionHandler i KeyEventHandler.
Most IReceiver → KeyEventReceiverBridge → KeyboardReceiver odświeża podpowiedzi po kapitalizacji.

## 3. Ustalenia zaakceptowane
- Informacja użytkownika: pary form na telefonie działają całkiem dobrze; ocena jakościowa, nie pełna akceptacja wszystkich przypadków.
- Shift po powrocie kursora do początku/środka/końca istniejącego słowa przełącza jego pierwszą literę, np. łódź ↔ Łódź.
- Zwykły tekst: maźnięcie i kliknięcie podpowiedzi stosują te same preferencje odstępów przed/po.
- Hasła, wyszukiwanie, URI/email i pola liczbowe: bez automatycznych odstępów i formatowania interpunkcji.
- Wyszukiwanie nadal może wyświetlać podpowiedzi; formatowanie nie jest uprawnieniem do predykcji.
- Interpunkcja w zwykłym tekście normalizuje także ręczną zwykłą spację przed przecinkiem/kropką itp.
- Użytkownik WYCOFAŁ zgłoszenie dotyczące uzupełniania przy klikaniu liter i potwierdził, że działa. Nie zmieniać tego mechanizmu.

## 4. Odrzucone lub odłożone
- Duplikowanie wpisów CKDT dla wielkości liter i ręcznie tworzone opisy znaczeń nadal poza ustalonym rozwiązaniem.
- AI/CTC nie są potrzebne do tego etapu; generowanie fleksji Łódźi → Łodzi nie jest wdrożone.
- Automatyczna zmiana wszystkich znaków interpunkcyjnych bez wyjątków: odrzucona, bo uszkadza nawiasy, łączniki i liczby.
- Nowe ustawienia i listy nazw aplikacji do zgadywania pól: nie dodano.
- Zgłoszenie prefiksów heliko → helikopter zamknięte na podstawie wycofania przez użytkownika.

## 5. Plan, ale jeszcze niewdrożone
- Docelowa promocja dopiero po osobnej zgodzie; brak merge/tag/release/version bump.
- Pełne pokrycie słownika metadanymi ze źródeł oraz dalsze modelowanie kontekstu pozostają odrębnymi etapami.
- Cykl pełnych WIELKICH liter i przekształcanie zaznaczonego zakresu nie należą do Shifta w tej próbie.

## 6. Niezweryfikowane
- Nowy APK: rzeczywiste zachowanie InputConnection w aplikacjach użytkownika, opóźnienia i obsługa cofania.
- Rozpoznanie wyszukiwania, jeśli aplikacja nie udostępnia IME_ACTION_SEARCH ani typu URI.
- Obsługa terminala bez otaczającego tekstu, wydajność dodatkowych odczytów kursora.
- Zmienione testy instrumentacyjne są aktualizacją oczekiwań; nie oznaczają wykonania testu na emulatorze/telefonie.

## 7. Gałęzie i ich role
- CleverKeysPL docs/source-variants-integration-v1, draft [PR #1](https://github.com/jakamilek/CleverKeysPL/pull/1): runtime, Shift i odstępy.
- CleverKeys-langpack-pl feature/source-variants-trial-v1, draft [PR #5](https://github.com/jakamilek/CleverKeys-langpack-pl/pull/5): producent tej samej 9-kluczowej paczki; HEAD 75a06570cc9eaac72f1e7c4376a4efd068be73fb w chwili weryfikacji.
- Main zawiera dokumentację stanu, a nie eksperymentalną implementację z PR.
- Runtime HEAD po zapisaniu wyników: 04fe5aef5cd2d037383db3e6b836d72edf292436 (tylko aktualizacja dokumentacji względem przetestowanego kodu).

## 8. SHA, testy i artefakty
- Wcześniejsza wersja z samymi parami form: a21d9fef3b643ad7a09520f232d9d39f42be1071.
- Shift: 1b3dcda293b98c2191d824c2e76754657e258f77, 05be9dc1a1417b98541bb399932ed3ff0a14558f, d64439acf1308a8bddfb8c9add25cbdaf26b6215.
- Shift d64439ac, [run 37114260076](https://github.com/jakamilek/CleverKeysPL/actions/runs/37114260076): debug build PASS, 2762 pure PASS, mock: import 45, swipe 7, partial replacement 5, Shift 20, pointers 9, bridge 3, slider 5 — PASS.
- Odstępy: 2723517f201599f916bccebeb11ef6b48c92f3bd i 3ab447bf401be77a4e602d34f5fb2c8fa445dc2c.
- Końcowy przetestowany kod: b373391c88de57edacd7ad2d0ad4ea8b62e23985. [Run 37123257770](https://github.com/jakamilek/CleverKeysPL/actions/runs/37123257770): debug build PASS, 2773 pure PASS; mock: import 45, swipe 7, partial replacement 11, Shift 20, pointers 9, bridge 3, slider 5, odstępy 15, double-space 3, dropped-space repair 11 — PASS. Łącznie 2902 testy.
- Pierwsza próba 2723517f: budowa i 2773 pure PASS, dwa błędy nowej atrapy MockK (nullable owed-space zwracało pusty tekst). Poprawiono test w b373391c88de57edacd7ad2d0ad4ea8b62e23985; nie wyłączono sprawdzenia.
- [APK debug artifact 11273393913](https://github.com/jakamilek/CleverKeysPL/actions/runs/37123257770/artifacts/11273393913), 96874457 bajtów, wygasa 2026-10-10. ZIP digest z metadanych GitHub: sha256:dc3caddbfca1b0012efe62970bd1ad1d27e8a36b15fbeadccf15b5a0e0be7ab1. Nie jest to SHA pojedynczego APK ani lokalna weryfikacja pobranych bajtów.
- Trial pack SHA-256: 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7 (nie zmieniono).
- CKDT SHA-256: 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20.
- Specy: docs/specs/cursor-word-capitalization.md i docs/specs/editor-spacing.md na gałęzi runtime.

## 9. Ograniczenia i luki
Całe CI końcowego b373391c i Shifta d64439ac nie jest zielone: istniejący ProduceStateDoesNotAssignValue w SubkeyAssignActivity.kt:148 i 4 HIGH devalue 5.8.1 w site/bun.lock. Nie wyłączono bramek; release lint nie wykonał się po błędzie debug lint.
Formatowanie jest deterministyczne, nie jest parserem języka. Konserwatywnie zachowuje . , : po cyfrze bez dodawania spacji; skróty i nietypowe adresy w zwykłym polu pozostają ograniczeniem.
Normalizowane jest najwyżej 8 zwykłych spacji przy kursorze; tabulatory, nowe linie i wcięcia nie są usuwane.
Shift wymaga użytecznych informacji o zaznaczeniu i tekście; na nieobsługiwanych połączeniach pozostaje zwykłym Shiftem.
Zamiana alternatywy sprawdza rzeczywisty sufiks zamiast zakładać dodatkową spację i usuwać poprzedni znak.

## 10. Następny krok
Udostępnić artefakt końcowego b373391c, przeprowadzić test na telefonie według obu specyfikacji.
Pozostawić PR próbny do osobnej decyzji o promocji. Nie wracać do wycofanego zgłoszenia uzupełnień.

## 11. Różnica względem poprzedniego kamienia
Poprzedni: docs/PROJECT_MILESTONE_2026-10-03_FIREFOX_DOWNLOAD_AUDIT.md w obu repozytoriach.
Nowe: jakościowy wynik testu par, wdrożony/testowany Shift, zaakceptowana i wdrożona polityka odstępów/interpunkcji oraz wycofanie uwagi o uzupełnieniach.
Audyt wcześniejszego ostrzeżenia Firefox nie ustalał przyczyny ostrzeżenia i nie jest gwarancją dla nowego APK.
