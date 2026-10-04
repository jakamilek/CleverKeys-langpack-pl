# Kamień milowy — wyniki objaśnień metadanych v5

Data weryfikacji: 2026-10-04. Stan: inferencja zakończona SUCCESS, wyniki pobrane i odtworzone.

## 1. Zweryfikowany stan repozytoriów

Main przed zapisem: CleverKeys-langpack-pl a8321e6131dbb4f5019314cb913547ed5e2e100d; CleverKeysPL e247f4c0e8cf78b406ec95381a673a9518dbe7e3. Main otrzymuje wyłącznie ten dokument.

Producer experiment/context-surface-window-v1, draft PR #4: wyniki c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b, rodzic/freeze bc5c4f46895a4bd8a64d5c0736d3d58357ef12a7. Sześć nowych plików w experiments/ai_metadata_v5_results; zamrożone kryteria, kod i wcześniejsze wyniki zachowane. Poprzedni checkpoint: PROJECT_MILESTONE_2026-10-04_METADATA_GUIDANCE_V5.md.

## 2. Aktualna architektura

Geometric pozostaje dekoderem. Jeden klucz v5 dostarcza dopuszczalne warianty i źródła bez powielania CKDT. Metadane nadal służą wariantom i defaultom. Modelowe rankingi są tylko eksperymentem offline. Runtime nadal ma krótki kontekst; dłuższe okno przetestowano wyłącznie offline.

Pięć warunków: plain, raw, explained, guided, plain_guided. Globalne objaśnienia POS/NAME zachowują lemma/labels/surfaces; brak ręcznych znaczeń per słowo. HerBERT/MiniLM otrzymują tekst, bez uczenia wykonywania instrukcji; Qwen otrzymuje ją w istniejącym komunikacie użytkownika.

## 3. Ustalenia zaakceptowane

Nowe 32 konteksty, długie okno, poprawna forma top 1 (plain/raw/explained/guided/plain_guided):
- HerBERT: 25/24/24/24/23.
- MiniLM: 16/16/17/13/15.
- Qwen3-0.6B: 21/17/16/17/19.
Default: 16/32. HerBERT plain: 10 napraw / 1 regresja względem defaultu; krótkie okno 20/32, długie 25/32.

HerBERT plain pozostaje pierwszym kandydatem do niezależnej i mobilnej walidacji, nie wyborem produkcyjnym. Obecne tekstowe objaśnienie/instrukcja nie uzyskały przewagi nad plain na nowych kontekstach. Źródłowych metadanych nie usuwamy. Telefon potwierdzony przez użytkownika: Nubia Z60 Ultra LV 12/512 GB; Android/SoC nie są domyślane.

## 4. Rozwiązania odrzucone lub odłożone

Brak podstaw do globalnego wdrożenia obecnego prefiksu, wyboru warunku per słowo, wyjątków Ale/Lub/Tutaj albo strojenia na tych samych przypadkach po wynikach. Nie wnioskujemy, że metadane są bezużyteczne lub modele nie mogą ich wykorzystać.

Top 3 form jest nasycone dwoma wariantami także bez SI; nie przedstawiać tego jako przewagi SI ani zdublowanych wpisów. CTC poza tym etapem. Bez merge/release, nowego APK i promocji kodu na main.

## 5. Zaplanowane, jeszcze niewdrożone

Mobilny eksport/kwantyzacja HerBERT, kontrola jakości po konwersji, niezależne rzeczywiste konteksty i szersze rankingi geometric. Następnie start/p50/p95/RAM/energia/płynność na telefonie i kalibracja z geometrią.

Uczony adapter/ranker z cechami źródłowymi to ewentualny osobny kierunek; jego jakości i kosztu nie badano. Backlog BS: czas do pierwszego zaznaczenia, podgląd do usunięcia (obecnie 350 ms), przerwa do następnego zaznaczenia (200 ms); zachować zaakceptowany gest. Polskie opisy, wyszukiwanie, backup/reset; inne tłumaczenia do późniejszej poprawy.

## 6. Weryfikacja i rzeczy niezweryfikowane

[Run 37221672371](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37221672371): kontrakt, HerBERT, MiniLM, Qwen i collector SUCCESS. Każdy model wykonał 1160 zapytań. Cztery ZIP SHA256 zgadzają się z GitHub; cały lokalnie odtworzony comparison.json jest identyczny z CI.

Sprawdzono kompletność, rewizje/presety, freeze/request/source, skończone oceny dozwolonych form, loading i parytet projekcji. Brak błędów wag; cztery nieużywane HerBERT pooler/SSO były dozwolone przed freeze. Zero obciętych kontekstów; maksimum tokenów 321/387/761. Po 336 reused plain/raw rankingów każdego modelu jest identycznych z poprzednią próbą. Przed freeze 16 testów stdlib PASS.

Reused 64, long top 1 w pięciu warunkach: HerBERT 50/49/51/48/46; MiniLM 28/29/33/29/30; Qwen 36/35/35/37/39. Nie łączyć z nowymi 32. Historyczne osiem rankingów: HerBERT plain 7/8 top 1 i 8/8 top 3, guided 6/8 i 8/8.

## 7. Gałęzie historyczne i ich role

Runtime docs/source-variants-integration-v1, draft PR #1: v15 code 4e51c3b45285fdbfdc93531bd80e228444601818; workflow-only HEAD 6b3b2580094170384e1e0f9a4b72138546ebd884. Producer feature/source-variants-trial-v1: v5 041b28ae4587c531ef73e62933e9151cadb84c33.

Pierwsza próba modeli: freeze 00a7bf5999e8f6419a68c1884919e699c744a927, wyniki 6c468719da474408b8ebadfcb03ebc184c32afda. Wcześniejsze source-category wyniki 90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52 są odrębną historią.

## 8. Artefakty, SHA i punkty integracji

[Raport i trwałe wyniki](https://github.com/jakamilek/CleverKeys-langpack-pl/tree/c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b/experiments/ai_metadata_v5_results): RESULTS.md, comparison.json, trzy predictions.json, artifact-manifest.json. Manifest zawiera pełne SHA256 ZIP i plików.

Artefakty: comparison 11312225106 (f35be46a6d1e5d6612e78c4e3d36756c822ef549ce8be4e977d4c21366d8c103); Qwen 11311776435 (f9426b69ab0d6099f2b1e078133bdf0687482ff801ad94dd4b186b0e52389e3e); MiniLM 11310541139 (98ed96fe2edd6aa07777069ae6d218b051a0363b6782ac0f52480554ebfc7f8b); HerBERT 11310334856 (12cdd2d8040bb87a49a4eb1d963dbceb44b60068791a1d19c5ba2201f41f8b45).

Freeze SHA256 afdddc6b3141fab3b6bd6b09bce8d24299d737017680a69eaaddcfd4ab10e8d6; payload b6359d31ef5b8127530a77ba5f4f51af9d909942252b3611cfa2088602c4a038. V5 ZIP aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb; snapshot 05270f8ae2c6d88bb8209cb00c83ff3d66ba788544f524ed27fbb5e0b4666794. Wagi nie są publikowane.

## 9. Ograniczenia i znane luki

32 nowe autorskie konteksty dotyczą znanych 16 kluczy i powstały po wcześniejszych wynikach; nie są ślepym niezależnym korpusem. Historyczne top 5 nie mają punktów gestu i nie są nowym dekodowaniem v5. Nie ma skalibrowanego połączenia ocen z geometrią. Interpunkcji nie powtarzano w tej próbie.

Host CPU float32, dwa wątki, oddzielne maszyny: nowe long plain/guided p50/p95 — HerBERT 101/115 i 430/646 ms; MiniLM 18/23 i 74/114 ms; Qwen 1223/1308 i 3731/5329 ms. RSS całego procesu około 1389/1151/4741 MiB. Inferencja wszystkich zapytań około 359/64/3015 s. To nie pomiary Nubii ani zoptymalizowanego Androida.

## 10. Następny uzasadniony krok

Ocenić eksport/kwantyzację i przygotować niezależną walidację rzeczywistych kontekstów oraz szerszych rankingów; dopiero później proponować integrację. Obecna próba nie wymaga rerunu. Nie zmieniać jej danych, kryteriów ani zamrożonych metod.

Monitorować Actions maksymalnie 60 sekund łącznie na build, potem czekać na informację użytkownika. Gemini/PAL waiver obowiązuje; bez subagentów bez jawnego zlecenia.

## 11. Różnica względem poprzedniego kamienia milowego

Zamiast oczekujących wyników są kompletne, zweryfikowane i odtworzone wyniki trzech modeli. Instrukcja wpływa na odpowiedzi, lecz nie daje globalnej przewagi; HerBERT plain nadal najlepszy kandydat. Dodano raport błędów i kosztu oraz surowe przewidywania. Aplikacja, langpack v5 i wcześniejsze wyniki nie zmieniły się.
