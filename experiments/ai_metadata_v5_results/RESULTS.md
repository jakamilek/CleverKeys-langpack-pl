# Objaśnienie metadanych i instrukcja — wyniki v5

2026-10-04. [Run 37221672371](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37221672371) zakończony SUCCESS: kontrakt, trzy modele i collector. Freeze przed inferencją: `bc5c4f46895a4bd8a64d5c0736d3d58357ef12a7`. Wyniki poprzedniej próby pozostają odrębne w `experiments/ai_compare_v5_results`.

**Wniosek: nie potwierdzono, że objaśnienie pól i ta instrukcja dają globalną korzyść na nowych kontekstach. HerBERT bez tekstowego opisu metadanych, z dłuższym kontekstem, pozostaje pierwszym kandydatem do dalszej niezależnej walidacji i próby mobilnej.** Metadane nadal określają dopuszczalne warianty jednego wpisu słownika, ich źródła i defaulty. Nie wybieramy warunku osobno dla słów po obejrzeniu pomyłek.

To wynik modeli z konkretnymi adapterami, bez dodatkowego treningu. Nie dowodzi bezużyteczności metadanych, niemożności wykorzystania ich przez model ani tego, że model ich nie czytał. Instrukcja i opis zmieniają odpowiedzi; obecna próba nie wykazała przewagi takiego sposobu użycia nad samym kontekstem.

## Potwierdzenie wykonania

Każdy model wykonał rzeczywistą inferencję dla wszystkich 1160 zapytań: 116 przypadków, dwa okna, pięć warunków. Pobrano cztery artefakty, ich ZIP SHA256 zgadzają się z metadanymi GitHub. Surowe przewidywania ponownie oceniono zamrożonym collectorem lokalnie: cały obiekt comparison.json jest identyczny z CI.

Potwierdzono model revision/preset, commit kodu, hash freeze/request/source, kompletność i skończoność ocen wyłącznie dla dozwolonych kandydatur, kontrolę wag i parytet projekcji. Brak missing/mismatched/error; HerBERT ma wyłącznie cztery wcześniej dozwolone nieużywane wagi poolera/SSO. Nie obcięto żadnego kontekstu. Maksymalny budżet rzeczywistych wejść: HerBERT 321, MiniLM 387, Qwen 761 tokenów.

Porównano po 336 pełnych rankingów plain/raw powtórzonych przypadków każdego modelu z poprzednią próbą: wszystkie są identyczne, bez ponownego mieszania wyników obu badań. Przed freeze przeszło 16 testów stdlib. Nie zmieniano danych/metod po bieżących wynikach, nie wykonano kolejnej inferencji.

## Nowe 32 konteksty — poprawna forma na pierwszym miejscu

| Model | Bez opisów | Surowe metadane | Objaśnione | Objaśnione + instrukcja | Sama instrukcja |
|---|---:|---:|---:|---:|---:|
| HerBERT | 25/32 | 24/32 | 24/32 | 24/32 | 23/32 |
| MiniLM | 16/32 | 16/32 | 17/32 | 13/32 | 15/32 |
| Qwen3-0.6B | 21/32 | 17/32 | 16/32 | 17/32 | 19/32 |

Wszystkie wartości dotyczą długiego kontekstu. Default v5 ma 16/32. HerBERT bez opisów to dziesięć napraw i jedna regresja względem defaultu, 15/16 małych i 10/16 wielkich liter. Przy dwóch poprzednich słowach ma 20/32, przy długim oknie 25/32.

Top 3 = 32/32 dla wszystkich, również defaultu, z powodu dwóch dostępnych form jednego klucza. Nie jest to dowód przewagi SI ani zdublowanych wpisów CKDT. Nowe konteksty są napisane po analizie poprzedniej próby, dla znanych kluczy; to nowa diagnostyka, nie ślepy korpus i nie niezależny dowód generalizacji.

## Oddzielny wpływ formatu, instrukcji i danych

Pary na nowych formach w długim kontekście, naprawy/regresje względem warunku po lewej:

| Model | Raw → objaśnione | Objaśnione → z instrukcją | Bez opisów → sama instrukcja | Sama instrukcja → instrukcja z opisami |
|---|---:|---:|---:|---:|
| HerBERT | 0 / 0 | 1 / 1 | 2 / 4 | 1 / 0 |
| MiniLM | 3 / 2 | 4 / 8 | 5 / 6 | 9 / 11 |
| Qwen | 0 / 1 | 3 / 2 | 4 / 6 | 1 / 3 |

HerBERT z instrukcją i opisami jest o jeden przypadek lepszy niż sama instrukcja, lecz nadal słabszy od plain. MiniLM ma drobną korzyść z samego objaśnienia i pogorszenie po instrukcji. Qwen ma jedną naprawę netto po dodaniu instrukcji do objaśnionych pól, lecz jest słabszy niż plain i niż sama instrukcja. Nie ma podstaw, żeby z tych pojedynczych zmian wnioskować o trwałej korzyści lub mechanizmie rozumienia schematu.

Opisy są generowane z tych samych lemma/POS/NAME/labels/surfaces; rozwinięcia kodów są globalne. Nie dopisano owocu/pojazdu/miasta ani znaczeń per słowo. HerBERT i MiniLM otrzymują instrukcję jako tekst, bez uczenia wykonywania poleceń. Qwen otrzymuje ją w istniejącym komunikacie użytkownika przy niezmienionym system task i scoringu.

Przykłady zmian HerBERT plain → guided: poprawiono Jagoda w kontekście imienia i Zając w kontekście nazwiska, ale pogorszono jagoda, kruk i zając w kontekstach pospolitych. Poprawiono lub jako spójnik, jednocześnie pogarszając Lub jako odmianę imienia. To ilustruje konkurencję interpretacji i regresje, nie uzasadnia wyjątków dla konkretnych słów.

## Powtórzone 64 konteksty — oddzielna populacja

| Model | Bez opisów | Surowe metadane | Objaśnione | Objaśnione + instrukcja | Sama instrukcja |
|---|---:|---:|---:|---:|---:|
| HerBERT | 50/64 | 49/64 | 51/64 | 48/64 | 46/64 |
| MiniLM | 28/64 | 29/64 | 33/64 | 29/64 | 30/64 |
| Qwen | 36/64 | 35/64 | 35/64 | 37/64 | 39/64 |

Objaśniony HerBERT ma 51/64 na znanej populacji, ale 24/32 na nowych kontekstach wobec plain 25/32. Nie wybieramy go wyłącznie na podstawie lepszego wyniku znanych przypadków. Top 3 jest nasycone także tutaj. Nie łączymy populacji, żeby ukryć różnicę kierunku zmian.

## Historyczne osiem rankingów — długi kontekst

| Model | Plain top 1/top 3 | Raw | Objaśnione | Z instrukcją | Sama instrukcja |
|---|---:|---:|---:|---:|---:|
| HerBERT | 7/8 · 8/8 | 7/8 · 8/8 | 7/8 · 8/8 | 6/8 · 8/8 | 7/8 · 8/8 |
| MiniLM | 2/8 · 3/8 | 0/8 · 1/8 | 0/8 · 1/8 | 1/8 · 2/8 | 1/8 · 3/8 |
| Qwen | 2/8 · 3/8 | 2/8 · 4/8 | 2/8 · 4/8 | 2/8 · 4/8 | 2/8 · 5/8 |

To dokładna forma, nie tylko klucz. Historyczne top 5 z logu użytkownika, bez punktów gestu, nie są nowym dekodowaniem v5. Oceny modelu są sortowane bez skalibrowanego połączenia z geometrią. Wyniku ośmiu przypadków nie traktujemy jako potwierdzenia produkcyjnego rankingu.

Kontrole jednowariantowe i brakującego klucza nie wykazały wynajdywania wariantów spoza listy; to wymuszenie kontraktu, nie samodzielna zdolność modelu. Niejednoznaczne przypadki nie mają accuracy. Interpunkcji nie powtarzano w tej próbie.

## Koszt wykonania na hostach CI

CPU float32, dwa wątki, oddzielne hosty. P50/p95 dla nowych form, długi kontekst:

| Model | Bez opisów | Objaśnione + instrukcja | Szczyt RSS całego procesu |
|---|---:|---:|---:|
| HerBERT | 101/115 ms | 430/646 ms | 1389 MiB |
| MiniLM | 18/23 ms | 74/114 ms | 1151 MiB |
| Qwen | 1223/1308 ms | 3731/5329 ms | 4741 MiB |

Inferencja wszystkich 1160 zapytań trwała około 359 s HerBERT, 64 s MiniLM i 3015 s Qwen (około 50 minut). Cały proces obejmuje dodatkowo pobranie/ładowanie i przygotowanie. Brak obcięcia kontekstu oznacza, że większe czasy i różnice odpowiedzi nie wynikają tutaj z utraty starszych słów.

To pomiary hostów, nie telefonu ani docelowej zoptymalizowanej ścieżki. Nie zakładamy, że Nubia Z60 Ultra LV 12/512 GB uzyska te czasy lub RSS. Brak wyników eksportu, kwantyzacji, Androida i energii.

## Rekomendacja i następny krok

Pozostawić HerBERT plain z dłuższym kontekstem na shortliście. Zachować źródłowe metadane i obie formy; nie włączać domyślnie obecnego prefiksu/instrukcji. Ta próba nie uzasadnia dalszego strojenia promptów na tych samych 32/64 kontekstach ani wdrożenia modelowego rerankingu.

Następnie ocenić mobilny eksport/kwantyzację i jakość po konwersji oraz przygotować niezależną próbę rzeczywistych kontekstów i szerszych rankingów geometric. Dopiero potem test kosztu na telefonie i propozycja integracji. Jeśli wykorzystanie metadanych pozostaje celem, osobnym kierunkiem jest uczony adapter/ranker korzystający z cech źródłowych; jego koszt i jakość nie były tu badane i nie obiecujemy korzyści.

## Trwałe pliki

Surowe herbert/minilm/qwen/predictions.json, odtworzone comparison.json i artifact-manifest.json są zapisane obok raportu. Manifest zawiera SHA256 ZIP artefaktów i trwałych plików. Zamrożone wejścia odtwarza `experiments/ai_metadata_v5/contract_meta.py`. Wagi nie są publikowane. Aplikacja, langpack v5, wcześniejsze wyniki i metody są niezmienione; bez merge/release i nowego APK.
