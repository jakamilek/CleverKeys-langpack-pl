# Nowe zdania i wieloznaczne warianty — protokół v2

2026-10-02. Kryteria i dane zostają zamrożone w GitHub przed inferencją.
Izolowana próba offline, bez treningu i bez zmiany API produkcyjnego.

## Cel i poprawna pisownia

Kontynuacja zlecona przez użytkownika: łódź, malina, warszawska (ulica/nazwisko),
itp. Dodajemy łodzi, jagoda, róża, polska. Jeden lowercase surfaceKey ma dwa
warianty zapisu, ale dowolny wariant może mieć więcej niż jedno znaczenie.
Warszawska → nazwa ulicy **lub** nazwisko; warszawska → przymiotnik od Warszawy.
Polska → państwo, polska → przymiotnik. łodzi/Łodzi ma własny surfaceKey,
bez dopisywania niezrealizowanej lematyzacji.

Pisownię opieramy na aktualnych zasadach RJP:
https://rjp.pan.pl/app/uploads/2026/03/Zalacznik-do-komunikatu-11-25-wersja-ostateczna-jednolita.pdf
Rozdz. 8.1.1 (pierwszy wyraz zdania), 8.1.2 pkt 1 (imiona/nazwiska), pkt 16
(nazwy obiektów i wyjątek ulica), 8.2 pkt 4 (przymiotniki od nazw własnych).
Ulica Warszawska jako pełne wyrażenie na początku zdania ma wielkie U z powodów
składniowych; w środku zdania jest ulica Warszawska. warszawska ulica to
określenie położenia, nie automatycznie oficjalna nazwa ulicy.
Osoby i sytuacje w fixture są fikcyjne; nie poświadczamy obecności nazwisk
w bieżącym 100k ani w rejestrze nazwisk. To nie audyt coverage produkcyjnego.

## Dane i etykiety

64 nowe ręcznie napisane kontynuacje, po 16 natural_direct, natural_history,
natural_switch, natural_negation. W każdej kategorii 8 form lowercase i 8
capitalized. Sześć kluczy po 8 cases, warszawska 16 (dwa typy przymiotnikowych
kontekstów oraz ulica/nazwisko). Wszystkie konteksty główne są nowe, nie są
kopiami poprzednich fixtures. Zestaw powstał po wcześniejszej diagnozie, więc
nie jest zewnętrznym ślepym benchmarkiem ani reprezentatywną próbą użytkowników.

Osobno:
- 64 top3_probe, powtórzenia głównych kontekstów: poprawny klucz #2 po dwóch
  wariantach innego klucza; preferowana forma #3, alternatywa #4;
- 14 sentence_start: jawny mode autocap; pisownia na początku zdania nie
  stanowi dowodu wybrania znaczenia nazwy własnej;
- 8 ambiguous bez expected/expectedSenseIds, bez sztucznej accuracy;
- 7 missing_key: poprawnego słowa nie ma w slate, model nie może go wymyślić;
- 7 slot_limit: poprawny klucz #3 po dwóch wariantach pierwszego i drugim
  kluczu; najwcześniejsza poprawna forma #4, poza top 3 przy stałym lexical rank.

Łącznie 164 cases / 328 requests. Kontrole/powtórzenia nie zwiększają liczby
niezależnych kontekstów głównej próby. Slates są skonstruowane, nie realne swipe.
Gold opisuje zamierzoną interpretację autora przykładu; naturalny język może
mieć inne konteksty niż ten zamierzony. Przypadki bez rozstrzygnięcia są osobno.

## Zamrożone modele i warunki

NLI: MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli,
0a71e92a985b6e1ad1828cf67ce9c459639c1dca, ten sam pretrained model jak wcześniej.
Trzy warunki przy niezmienionych wagach:
- global_attributes: dokładna dotychczasowa hipoteza
  W tym kontekście słowo „{key}” oznacza {description}.
- current_attributes: nowa, zamrożona przed wynikiem hipoteza
  Ostatnie dopisywane słowo „{key}” w aktualnym zdaniu oznacza {description}.
- no_attributes: ta sama hipoteza poprawnej pisowni „{surface}” jak w v1.

Premise: dokładny tekst sprzed kursora + lowercase kandydat. Wszystkie
hipotezy dla jednego klucza/warunków otrzymują ten sam suffix przy budżecie
512 pozycji. Score = log softmax entailment. Wariant z wieloma znaczeniami
otrzymuje max ich scores; więcej znaczeń może sprzyjać takiemu wariantowi.
Nie interpretujemy tej skali jako skalibrowanej pewności. Oddzielnie zapisujemy
senseScores, by sprawdzić ulicę wobec nazwiska mimo identycznej pisowni.

Baselines na NOWYCH danych, z prawdziwą inferencją obu modeli:
- Polbert fed744e81ebd16cf099b5c64c40688bc3e6ace67;
- HerBERT 50e33e0567be0c0b313832314c586e3df0dc2297;
- neutralny dictionary default.
Tylko WWM: wszystkie subwordy wariantu masked jednocześnie, suma log prob,
ten sam scoring jak wcześniejsze wwm. Nie wybieramy nowych funkcji celu po
wyniku. Wagi/głowice kompletne, dozwolone unused HerBERT jak DIAGNOSTIC_PROTOCOL.
Reużywamy sprawdzony loader/projekcję maskowanych pozycji. Brak treningu.

## Metryki i granice wnioskowania

Główne kryterium użytkownika: poprawny klucz i dokładny zapis w top 3.
Top 1 dodatkowo; osobno reachable i meaningTop1 dla NLI z opisami. Bez opisów
oraz w MLM nie raportujemy fikcyjnej jakości wyboru znaczenia.
Wieloznaczne Warszawska: można mieć poprawną pisownię przy błędnym sensie;
obie liczby muszą pozostać oddzielne. Nie mierzymy semantic top3 (wszystkie
znaczenia byłyby automatycznie dostępne w małej puli).

Raportujemy główne 64 cases, powtórzony top3_probe i pozostałe kontrole osobno,
według kategorii i kluczy. Top3 64/64 w głównej próbie wynika z dwóch wariantów
pierwszego klucza, również bez modelu. Slot_limit i missing_key to ograniczenia
slate/resolvera, nie jakość interpretacji znaczeń przez model.
Case mode jest jawny, nie wdrażamy nowego detektora granic zdań/skrótów.

Kolejność kluczy/engineScore i alternatywy zachowane. Brak rankingowania
różnych słów, inferencji zza kursora, nowego importera lub generatora 100k.
Opisów/hipotez/etykiet nie strojimy po obejrzeniu wyników. Nie ustalamy progu
ship na tych zdaniach i nie dobieramy blendu po wyniku.

## Wykonanie

CPU float32, 2 wątki, batch 8, eval/inference_mode. Cache wyłącznie identycznych
wejść. NLI i dwie inferencje WWM niezależne. Czas nie jest benchmarkiem telefonu.
Gold/category/sourceId/expectedSenseIds nie wchodzą do model requests.
Przed inferencją: walidacja sidecara, testy kontraktu, kontrola świeżych danych
i freeze kodu/protokołu/fixtures. Po: pełne scores/decisions/summary/metadata,
środowisko, manifesty SHA256, GitHub CI kontraktu i readback wyników.

```sh
python3 experiments/context_surface_v1/natural_experiment.py prepare
python3 -m unittest discover -s experiments/context_surface_v1 -p 'test_*.py' -v
python3 experiments/context_surface_v1/natural_experiment.py nli
python3 experiments/context_surface_v1/natural_experiment.py polbert
python3 experiments/context_surface_v1/natural_experiment.py herbert
python3 experiments/context_surface_v1/natural_experiment.py evaluate
```
