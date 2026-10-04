# Kamień milowy — objaśnienia i instrukcja metadanych v5

Data weryfikacji: 2026-10-04. Stan: nowa próba zamrożona i uruchomiona; wyniki inferencji oczekujące.

## 1. Zweryfikowany stan repozytoriów

HEAD main przed zapisem: CleverKeysPL `dade1bbd8cd96150c74ae03d26546d410ad3c193`; CleverKeys-langpack-pl `8b5055622de9aafc340e9dc33b1625c302f2adca`.

Producer `experiment/context-surface-window-v1`: `bc5c4f46895a4bd8a64d5c0736d3d58357ef12a7`, draft PR #4. Zweryfikowano 13 nowych plików i ich Git blob SHA; poprzednie pliki nie zostały zmienione. Main obu repozytoriów otrzymuje wyłącznie dokumentację.

Punkty wejścia: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_METADATA_GUIDANCE_V5.md), [langpack](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_METADATA_GUIDANCE_V5.md). Poprzedni checkpoint `PROJECT_MILESTONE_2026-10-04_AI_COMPARISON_RESULTS_V5.md` zachowuje pełne wcześniejsze wyniki.

## 2. Aktualna architektura

Geometric pozostaje dekoderem. Jeden klucz langpacka v5 ma dopuszczalne warianty z metadanych bez powielania CKDT. Nowy katalog `experiments/ai_metadata_v5` używa tych samych źródeł v5 i oryginalnego kodu ładowania/scoringu HerBERT, MiniLM i Qwen3-0.6B. Manifest wiąże nowe pliki oraz sześć rzeczywistych zależności poprzedniej próby.

Nowy renderer objaśnia globalne kody POS/NAME i zachowuje lemma/labels/surfaces. Nie dodaje słowom opisów owocu, miasta, pojazdu, ptaka ani ulicy. Brak NAME jest opisany jako brak podanej klasy, nie dowód znaczenia pospolitego. Kwalifikatory zachowano dosłownie. Instrukcja i renderer są wspólne dla wszystkich słów.

## 3. Ustalenia zaakceptowane

Użytkownik zlecił sprawdzenie, czy objaśnienie metadanych i instrukcja ich użycia poprawią wyniki. Pięć warunków: plain, raw, explained, guided oraz plain_guided. Ostatni daje tę samą instrukcję bez opisów metadanych, rozdzielając korzyść z polecenia od korzyści z danych.

HerBERT/MiniLM nie są traktowane jako modele nauczone wykonywania tej instrukcji: otrzymują eksperymentalny prefiks/premise. Qwen otrzymuje ją w komunikacie użytkownika. Scoring i ogólne zadanie są niezmienione. Kryterium użytkownika pozostaje poprawna forma w top 3, z oddzielnym top 1 i regresjami.

Telefon: Nubia Z60 Ultra LV, 12 GB RAM / 512 GB; Android/SoC nie są domyślane. Polski pozostaje priorytetem tłumaczeń.

## 4. Rozwiązania odrzucone lub odłożone

Nie interpretujemy poprzedniego słabszego wyniku metadanych jako dowodu ich bezużyteczności. Nie zakładamy znajomości schematu przez modele. Nie tworzymy ręcznych opisów słów ani wyjątków Ale/Lub/Tutaj.

Nie nadpisujemy wcześniejszych testów/wyników. Nie dobieramy promptu, modelu, scoringu, progów czy warunku per słowo po nowym wyniku. Nie wdrażamy niekalibrowanego rankingu ani interpunkcji do aplikacji. CTC pozostaje poza tym etapem.

## 5. Zaplanowane, jeszcze niewdrożone

Po zakończeniu nowej próby: oddzielnie ocenić efekt objaśnienia i instrukcji oraz dane przy tej samej instrukcji. HerBERT bez prefiksu pozostaje kandydatem wynikającym z poprzedniej próby, nie wyborem produkcyjnym. Nowy wynik może zmienić rekomendację adaptera.

Dalszy etap: niezależne rzeczywiste konteksty i slates, eksport/kwantyzacja, jakość po konwersji, start/p50/p95/RAM/energia/płynność na Nubii i kalibracja z geometrią.

Backlog BS: trzy ustawienia czasu — do pierwszego zaznaczenia, podgląd do usunięcia (350 ms), przerwa do kolejnego zaznaczenia (200 ms). Zachować zaakceptowane przeciąganie i cykl do podniesienia palca. Polskie opisy, wyszukiwanie, backup/reset.

## 6. Weryfikacja i rzeczy niezweryfikowane

Lokalnie 16 testów stdlib PASS: powtarzalność przypadków; globalny glosariusz; zachowanie źródeł/form/ranków; brak ręcznych znaczeń i wycieku odpowiedzi; instrukcja dociera do trzech adapterów; konserwatywne nieznane kody; identyczne stare plain/raw wejścia; sparowane budżety; poprawki/regresje; błędne przewidywania są odrzucane. Kompilacja Python, YAML/actions i manifest PASS. Sześć zależności zgadza się z Git blob SHA poprzedniego freeze.

[Run 37221672371](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37221672371): kontrakt SUCCESS. Wszystkie trzy zadania modeli pobrały i bajtowo zweryfikowały v5; przy ostatnim odczycie instalowały zależności. Faktyczne wyniki modeli są oczekujące. PR contract 37221675129 SUCCESS; nie wykonuje inferencji.

Monitorowanie zakończono po 34 sekundach. Nie odpytywać runu dalej przed informacją użytkownika o zakończeniu. Nie ma nowego APK, zmiany klawiatury, wyniku instrukcji, pomiarów telefonu ani dowodu poprawy jakości.

## 7. Gałęzie historyczne i ich role

Runtime `docs/source-variants-integration-v1`, draft PR #1: v15 code `4e51c3b45285fdbfdc93531bd80e228444601818`, workflow-only HEAD `6b3b2580094170384e1e0f9a4b72138546ebd884`. Producer v5 `feature/source-variants-trial-v1`: `041b28ae4587c531ef73e62933e9151cadb84c33`.

Poprzednia próba SI freeze `00a7bf5999e8f6419a68c1884919e699c744a927`, wyniki `6c468719da474408b8ebadfcb03ebc184c32afda`. Wcześniejsze source-category wyniki `90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52` są odrębną historią. Nie scalono żadnej gałęzi, nie wydano wersji ani nie promowano kodu na main.

## 8. Artefakty, SHA i punkty integracji

[Nowy protokół](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/bc5c4f46895a4bd8a64d5c0736d3d58357ef12a7/experiments/ai_metadata_v5/PROTOCOL.md), `render_metadata.py`, `glossary.json`, `cases.json`, nowe adaptery, testy i manifest są zamrożone przed inferencją.

Manifest SHA256 `afdddc6b3141fab3b6bd6b09bce8d24299d737017680a69eaaddcfd4ab10e8d6`; payload `b6359d31ef5b8127530a77ba5f4f51af9d909942252b3611cfa2088602c4a038`.

116 przypadków: 84 powtórzone i 32 nowe; dwa okna × pięć warunków = 1160 zapytań/model. Oczekiwane artefakty `ai-metadata-v5-herbert/minilm/qwen/comparison` zachowają surowe przewidywania i raport. Brak jednego modelu blokuje pełne porównanie. Wagi nie są publikowane.

Źródło v5 to nadal ZIP SHA256 `aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb`, run 37202645255. Snapshot `05270f8ae2c6d88bb8209cb00c83ff3d66ba788544f524ed27fbb5e0b4666794`. Rewizje modeli są identyczne z poprzednią próbą.

## 9. Ograniczenia i znane luki

32 nowe konteksty napisano po obejrzeniu poprzednich wyników i dla znanych 16 kluczy. Są oddzielnie raportowaną diagnostyką, nie ślepym korpusem ani niezależnym dowodem generalizacji. Pozostałe 84 przypadki jawnie mają etykietę reused w ewaluacji; etykieta nie trafia do modeli. Interpunkcja jest poza nową próbą.

Form top 3 jest nasycone dwoma wariantami także bez SI; default top 1 = 32/64 reused i 16/32 new. Historyczne osiem top-5 slates nie jest nowym dekodowaniem v5 ani kalibracją geometrii. Metadane są morfologią i klasami nazw, nie pełnym słownikiem znaczeń.

Pięć warunków pary dostaje ten sam kontekst. Budżety 512 MLM/NLI i 1536 Qwen; usuwać można tylko najstarszy kontekst i logować zmianę, nigdy opisy/polecenie. Nieprawidłowy budżet zatrzymuje scoring. Hostowe CPU float32/dwa wątki i RSS nie opisują telefonu.

## 10. Następny uzasadniony krok

Po zgłoszeniu zakończenia sprawdzić status/logi, pobrać artefakty, zweryfikować SHA, kompletne 1160 zapytań/model i odtworzyć raport z raw predictions. Raportować osobno new/reused oraz plain→raw, raw→explained, explained→guided, plain→plain_guided i plain_guided→guided. Nie utożsamiać lepszego wyniku z udowodnionym rozumieniem schematu.

Jeżeli wystąpi błąd wykonania, zapisać przyczynę i nowe zamrożenie przed ponowną inferencją. Nie zmieniać kryteriów po wynikach. Na każdy build monitorowanie maksymalnie 60 sekund łącznie, potem informacja użytkownika. Gemini/PAL waiver obowiązuje; nie uruchamiać subagentów bez jawnego zlecenia.

## 11. Różnica względem poprzedniego kamienia milowego

Poprzedni checkpoint zapisał kompletne wyniki porównania i shortlistę HerBERT. Ten etap odpowiada na pytanie użytkownika o znajomość schematu: dodaje globalne objaśnienia, instrukcję, kontrolę instrukcji bez danych i 32 nowe konteksty. Zachowuje wcześniejsze źródła/metody/wyniki, a nowa inferencja pozostaje oczekująca. Aplikacja i langpack nie zmieniły się.
