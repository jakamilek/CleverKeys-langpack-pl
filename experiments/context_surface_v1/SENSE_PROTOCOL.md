# Eksperyment znaczenie → wariant pisowni, v1

Data zamrożenia: 2026-10-02. Izolowany eksperyment offline, bez treningu.
Rozszerzenie danych eksperymentalnych, **nie zmiana produkcyjnego API v1**.

## Cel i kryteria

Sprawdzić propozycję użytkownika: jeden lowercase surfaceKey, dopuszczalne
warianty pisowni i jawne znaczenia powiązane z wariantami. Model otrzymuje
kontekst oraz opisy znaczeń; rankuje warianty istniejących kluczy.

Główne kryterium użytkownika: poprawny klucz **i dokładny zapis** w pierwszych
**trzech** sugestiach. Top 1 jest kryterium dodatkowym. Osobno raportujemy
dostępność formy na dowolnej pozycji. Zachowujemy alternatywy i kolejność
kluczy dekodera; score modelu porównujemy tylko wewnątrz jednego klucza.

## Dane i jawne powiązanie

Ponownie wykorzystujemy 48 przypadków diagnostyki v2 z df65d22b59a865a77939cb00653ac54e5735fb38:
32 główne, 8 context_lost osobno, 8 ambiguous bez gold labels.
Nie są niezależnym benchmarkiem jakości. Nie zmieniamy ich kontekstów/etykiet.

Dodatkowe 32 top3_probe powtarzają konteksty głównej próby. W ich sztucznym
slate właściwy klucz jest drugi, pierwszy konkurent ma dwa warianty. Preferowana
forma celu trafia na miejsce 3, alternatywa na 4. Raportowane osobno, bez
dodawania do mianownika głównej próby; to test presji limitu UI, nie realne swipe.

Każdy wpis zawiera senses: id/kind/descriptionPl; wariant zawiera senseIds.
Id jest lokalne do klucza; dopuszczamy wiele znaczeń jednego wariantu.
łódź → boat/jednostka pływająca; Łódź → city/miasto. Pozostałe klucze:
malina/Malina (owoc/nazwisko), jagoda/Jagoda (owoc/imię), róża/Róża (kwiat/imię).
To ręcznie opisane dane diagnostyczne, nie potwierdzone coverage słownika PL.
Kapitalizacja na początku zdania jest oddzielnym display mode, nie nowym
znaczeniem słowa. SENSE_PROTOCOL nie zmienia generatora, CKDT ani ZIP-a.

## Gotowy model i metoda

MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli,
revision 0a71e92a985b6e1ad1828cf67ce9c459639c1dca.
Źródło: https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli
Karta deklaruje MIT, NLI w ponad 100 językach. Polski nie znajduje się w 15
językach XNLI z raportowanymi wynikami; jakość dla PL wymaga naszego pomiaru.
Nie wybieramy modelu produkcyjnego. Nie publikujemy wag.

Premise: dokładny suffix kontekstu + lowercase klucz kandydata. Nie ujawnia
wybranego case. Hypothesis (attributes):
`W tym kontekście słowo „{surfaceKey}” oznacza {descriptionPl}.`
Score: log softmax z trzech wyjść NLI, kolumna entailment. Dla wielu znaczeń
wariantu bierzemy max. To nie skalibrowana pewność poprawności pisowni.

Trzy warunki na tych samych wagach:
- attributes: właściwe opisy przypisane do wariantów;
- no_attributes: `W tym kontekście poprawną pisownią dopisywanego słowa jest „{surface}”.`;
- swapped_attributes: te same opisy zamienione między dwoma wariantami.

Swap to kontrola mechanicznego powiązania: przypisuje przeciwnej formie tę
samą ocenę modelu. Zmiana decyzji po swap nie jest samodzielnym dowodem
rozumienia kontekstu. Porównanie attributes/no_attributes zmienia także treść
hipotezy; to praktyczna ablacja, nie izolacja wszystkich czynników przyczynowych.

Baseline: neutralny default oraz wszystkie 6 zamrożonych wyników MLM v2.
Replay MLM zachowuje score celu; nowy konkurent w probe pozostaje neutralny
(nie udajemy nowej inferencji MLM dla niego). To nie test lexical rerankingu.

Okna: 2 i 64 słowa/4096 znaków; maksymalnie 512 pozycji NLI. W obrębie klucza
ten sam suffix we wszystkich warunkach, budżet po najdłuższej hipotezie.
Gold/category/sourceId nie wchodzą do requests. Brak tekstu po kursorze.

## Wykonanie i zabezpieczenie interpretacji

Factory AutoModelForSequenceClassification, pretrained głowica NLI; odrzucamy
missing/unexpected/mismatched/error weights i inne mapowanie etykiet.
CPU float32, 2 wątki, batch 8, eval/inference_mode. Cache tylko identycznych
wejść, bez zmiany matematyki. Pomiar czasu nie jest benchmarkiem telefonu.

Przed inferencją: testy kontraktu i structural preflight, freeze kodu/danych/
kryteriów w GitHub. Po inferencji: pełne scores, decyzje, summary, trace,
proweniencja i SHA256. Żadnego strojenia opisów/progów po obejrzeniu wyników.
Nie ustalamy sztucznego progu wdrożenia na tych szablonach.

Na głównej próbie top3 jest zapewnione przez dwa warianty pierwszego klucza,
więc 32/32 nie będzie dowodem korzyści AI. Ocenę znaczeń daje dodatkowo top1,
kategorie konfliktów i osobny top3_probe. Kontrolę context_lost i ambiguous
raportujemy oddzielnie, bez sztucznej accuracy dla niejednoznacznych tekstów.
Niezależne dane, rzeczywiste slates, koszt telefonu i interpunkcja później.

## Uruchomienie

```sh
python3 experiments/context_surface_v1/sense_experiment.py prepare
python3 -m unittest discover -s experiments/context_surface_v1 -p 'test_*.py' -v
python3 experiments/context_surface_v1/sense_experiment.py preflight
python3 experiments/context_surface_v1/sense_experiment.py infer
python3 experiments/context_surface_v1/sense_experiment.py evaluate
```

Środowisko modelu zgodne z requirements-diagnostic.txt; dodajemy tylko gotowy
checkpoint NLI, bez nowych bibliotek. Model musi być pobrany do cache przed
preflight/infer; loader używa local_files_only i przypiętej revision.
