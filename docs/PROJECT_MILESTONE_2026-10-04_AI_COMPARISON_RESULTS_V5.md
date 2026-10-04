# Kamień milowy — wyniki porównania SI v5

Data weryfikacji: 2026-10-04. Stan: kompletne wyniki trzech modeli, HerBERT jako kandydat do dalszej walidacji i próby mobilnej.

## 1. Zweryfikowany stan repozytoriów

HEAD main przed dodaniem tego dokumentu: CleverKeysPL `fa26b24a432e036d3902bb6d9956b05c2bfe09ee`; CleverKeys-langpack-pl `a1b65c9e7658d9ec43e273c77c9b136dcdb73c40`.

Gałąź `experiment/context-surface-window-v1` producenta: wyniki `6c468719da474408b8ebadfcb03ebc184c32afda`, zamrożony kod próby `00a7bf5999e8f6419a68c1884919e699c744a927`, draft PR #4. Zweryfikowano sześć nowych blobów z wynikami. Kod/dane/metody zamrożonej próby nie zmieniły się.

Ten punkt wejścia jest w obu repozytoriach: [runtime](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_AI_COMPARISON_RESULTS_V5.md), [langpack](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_AI_COMPARISON_RESULTS_V5.md). Poprzedni checkpoint: `PROJECT_MILESTONE_2026-10-04_AI_COMPARISON_V5.md`; szerszy stan aplikacji i v5: `PROJECT_MILESTONE_2026-10-04_GLOBAL_CASING_V5.md`.

## 2. Aktualna architektura

Geometric pozostaje dekoderem, langpack v5 przechowuje dopuszczalne warianty jednego klucza bez powielania CKDT. Nowa próba offline obejmuje HerBERT WWM, MiniLM NLI oraz Qwen3-0.6B z ograniczonym wyborem etykiety. Nie dodano SI do Androida.

Metadane v5 opisują warianty i źródła; warunek bez tekstu metadanych nadal korzysta z tych dopuszczalnych wariantów. Model otrzymuje kandydatury i kontekst, bez dodatkowego prefiksu źródłowego. Dłuższe okno zachowujące pisownię jest obecnie funkcją eksperymentu, nie runtime.

## 3. Ustalenia zaakceptowane i rekomendacja

Kryterium użytkownika: poprawna propozycja w pierwszej trójce. Oddzielnie oceniamy top 1 i regresje. Metadane muszą pochodzić z baz, bez ręcznych opisów każdego słowa.

Rekomendacja wynikająca z próby: HerBERT bez tekstowego prefiksu metadanych, z dłuższym kontekstem, jako pierwszy kandydat do niezależnej walidacji i mobilnego pomiaru. Nie jest to wybór produkcyjny ani potwierdzona wydajność na telefonie. Alternatywy i defaulty v5 pozostają.

Telefon użytkownika: Nubia Z60 Ultra LV, 12 GB RAM / 512 GB. Android i SoC nie są domyślane. Polski jest priorytetem tłumaczeń. Użytkownik ogólnie zaakceptował obecne zmiany klawiatury, co nie zastępuje szczegółowych pomiarów.

## 4. Rozwiązania odrzucone lub odłożone

W tej zamrożonej konfiguracji MiniLM i Qwen nie są preferowanymi kandydatami do kolejnej próby rankingu: mają gorszą jakość niż HerBERT, a oba obniżyły top 3 historycznych rankingów. Nie odrzuca to całych rodzin modeli lub innych adapterów.

Nie wybieramy wariantu z/bez metadanych osobno dla każdego słowa po zobaczeniu pomyłek. Nie poprawiamy wyników ręcznymi wyjątkami Ale/Lub/Tutaj. Pełne tekstowe doklejanie metadanych nie potwierdziło globalnej korzyści, ale nie usuwamy atrybutów słownika. Nie wdrażamy niekalibrowanego sortowania między kluczami ani automatycznej interpunkcji z tej próby. CTC pozostaje poza bieżącym etapem.

## 5. Zaplanowane, jeszcze niewdrożone

Nowa niezależna próba rzeczywistych kontekstów i szerszych rankingów geometric; kryteria ustalić przed inferencją. Eksport/kwantyzacja HerBERT i sprawdzenie jakości po konwersji. Następnie test na Nubii: start, p50/p95, RAM, energia, płynność pisania, opcjonalność modułu i kalibracja z geometrią.

Backlog przy kolejnych zmianach aplikacji: trzy czasy stacjonarnego backspace — przytrzymanie do pierwszego zaznaczenia, podgląd do usunięcia (obecnie 350 ms), przerwa do kolejnego zaznaczenia (obecnie 200 ms). Cykl do podniesienia palca; zaakceptowane przeciąganie zachować. Polskie opisy, wyszukiwanie, backup i reset.

## 6. Wyniki zweryfikowane i rzeczy niezweryfikowane

[Run 37218630239](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37218630239) SUCCESS: kontrakt, trzy rzeczywiste modele i collector. Każdy model wykonał 376 zapytań. Pobrano wszystkie cztery ZIP artefaktów, zweryfikowano SHA256 z logami oraz ponownie wykonano collector lokalnie. Cały `comparison.json` jest identyczny z CI. Kontrole commit/request/source/freeze, kompletności, dopuszczalnych skończonych ocen, ładowania wag i parytetu projekcji przeszły. Żadne wejście nie wymagało obcięcia kontekstu. Przed freeze przeszło 15 testów stdlib.

Długi kontekst, 64 formy (top 1 bez/z tekstem metadanych): default 32/64, HerBERT 50/64 i 49/64, MiniLM 28/64 i 29/64, Qwen 36/64 i 35/64. HerBERT bez metadanych: 21 napraw/3 regresje wobec defaultu, 29/32 małych i 21/32 wielkich liter. Okno dwóch słów miało 41/64.

Historyczne osiem rankingów, długi kontekst: default top 1/top 3 = 3/8 i 7/8; HerBERT w obu warunkach 7/8 i 8/8; MiniLM bez metadanych 2/8 i 3/8, z nimi 0/8 i 1/8; Qwen 2/8 i 3/8, z nimi 2/8 i 4/8. HerBERT bez metadanych: cztery naprawy i zero regresji względem defaultu tej części.

Przecinek/brak znaku przed znanym słowem: HerBERT 15/20, MiniLM 12/20, Qwen 8/20, default 8/20. MiniLM wybierał przecinek zawsze, Qwen nigdy; nie wykazują tu kontekstowego rozróżniania.

Nie mierzono telefonu, eksportu, kwantyzacji, energii, Androida ani produkcyjnego blendu. Brak nowego APK. Wnioski to rekomendacja diagnostyczna, nie generalizacja korpusowa.

## 7. Gałęzie historyczne i ich role

Runtime trial `docs/source-variants-integration-v1`, draft PR #1: v15 code `4e51c3b45285fdbfdc93531bd80e228444601818`; workflow-only HEAD `6b3b2580094170384e1e0f9a4b72138546ebd884`. Producer v5 `feature/source-variants-trial-v1`: `041b28ae4587c531ef73e62933e9151cadb84c33`.

Wcześniejsze eksperymenty pozostają historią w `experiment/context-surface-window-v1`; wyniki kategorii `90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52` dotyczą innej próby. Nie scalać, nie wydawać ani nie promować kodu na main. Main obu repozytoriów otrzymuje wyłącznie dokumentację.

## 8. Artefakty, SHA i punkty integracji

[Trwały raport](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/6c468719da474408b8ebadfcb03ebc184c32afda/experiments/ai_compare_v5_results/RESULTS.md), surowe przewidywania trzech modeli, `comparison.json` i `artifact-manifest.json` są zapisane w `experiments/ai_compare_v5_results`. Wejścia odtwarza zamrożony `experiments/ai_compare_v5/contract.py`; nie trzeba inferować ponownie.

Manifest freeze SHA256 `c96cf08e5ffcb240bdbf39df5ed9c902eab1b65575031e52f139debba5b14996`; payload `1af08d48369a7179f39e214f5147f34c5a9c05029c0572f09b8f51995bbca991`; snapshot `05270f8ae2c6d88bb8209cb00c83ff3d66ba788544f524ed27fbb5e0b4666794`.

Artefakty: HerBERT 11309790672, MiniLM 11309850447, Qwen 11309861780, comparison 11309302947. Manifest wyników zawiera SHA256 ZIP i zapisanych plików. Każdy wynik zachowuje rewizję, hashe plików modelu i środowisko. Wagi nie są publikowane.

Źródłem jest wewnętrzny ZIP v5 SHA256 `aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb`, udany run 37202645255. Dokładne rewizje modeli i metody zawiera zamrożony protokół.

## 9. Ograniczenia i znane luki

Konteksty są ręczną diagnostyką napisaną przed inferencją, nie ślepym korpusem. Główne top 3 = 64/64 jest nasycone dwoma wariantami, również bez SI. To nie zdublowane wpisy CKDT i nie dowód jakości SI.

Historyczne top 5 z logu nie zastępuje nowych gestów v5; brak surowych punktów. Osiem rankingów nie wystarcza do kalibracji blendu. Interpunkcja to tylko 20 prób przecinka przed znanym słowem.

Sparowane metadane przy długim kontekście: HerBERT sześć napraw/siedem regresji, MiniLM dziesięć/dziewięć, Qwen pięć/sześć. Metadane pomogły części nazw i zaszkodziły części wyrazów zwykłych. Pełne pole źródłowe w tekście nie ma potwierdzonej globalnej korzyści; nie jest to dowód nieprzydatności danych źródłowych.

CI CPU float32/dwa wątki: formy długie bez metadanych p50/p95 HerBERT 116/141 ms, MiniLM 14/15 ms, Qwen 1456/1548 ms. Szczyt RSS całego procesu odpowiednio 1451/1042/4850 MiB. HerBERT replay: 432/473 ms. Oddzielne hosty nie są identycznym sprzętem; te liczby nie prognozują Nubii.

## 10. Następny uzasadniony krok

Przygotować niezależny test jakości i sprawdzenie mobilnego eksportu HerBERT. Zachować wybór użytkownika, wszystkie warianty źródłowe i geometric. Nie wdrażać SI przed oceną jakości po konwersji i rzeczywistych opóźnień na telefonie. Interpunkcję walidować osobno.

Nie odpytywać ukończonego runu ponownie ani nie rerunować modeli bez nowej potrzeby. Na kolejny build obowiązuje limit monitorowania 60 sekund łącznie, potem użytkownik zgłasza zakończenie. Waiver odziedziczonego Gemini/PAL pozostaje; nie używać subagentów bez jawnego zlecenia.

## 11. Różnica względem poprzedniego kamienia milowego

Poprzedni checkpoint utrwalił protokół i oczekujące wyniki. Teraz wszystkie modele i collector zakończyły się poprawnie; zapisano i niezależnie przeliczono surowe przewidywania. HerBERT jest rekomendowany do następnej próby, a wpływ tekstowego podania metadanych, dłuższego okna i przecinka jest zmierzony. Nie wprowadzono zmian w klawiaturze, langpacku v5 ani kryteriach zamrożenia.
