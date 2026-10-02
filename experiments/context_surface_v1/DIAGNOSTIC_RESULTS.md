# Diagnoza kontekstu, modelu i punktowania — 2026-10-02

Wykonano realną inferencję dwóch gotowych modeli, bez treningu, według
zamrożonego [DIAGNOSTIC_PROTOCOL.md](DIAGNOSTIC_PROTOCOL.md). Dłuższy kontekst
pomaga w kontrolowanej próbie. Model i metoda oceny zmieniają konkretne
błędy; nadal nie ma podstaw do integracji produkcyjnej.

## Główna próba v2

32 oceniane przypadki: po 8 direct, previous, distant_retained i conflicting.
Pozostałe 16 z 48 przykładów to osobne kontrole lub tekst bez jednoznacznego
znaczenia. Dane są ręcznie skonstruowane za pomocą szablonów po analizie v1,
nie niezależnym benchmarkiem jakości ani rzeczywistymi slates użytkowników.

| Model | Metoda | 2 słowa | Do 64 słów | Naprawione / zepsute po wydłużeniu |
|---|---|---:|---:|---:|
| Polbert | wwm | 20/32 | 23/32 | 8 / 5 |
| Polbert | pll_variant | 19/32 | 22/32 | 6 / 3 |
| Polbert | pll_full_mean | 20/32 | 23/32 | 4 / 1 |
| HerBERT | wwm | 18/32 | 21/32 | 6 / 3 |
| HerBERT | pll_variant | 17/32 | 20/32 | 3 / 0 |
| HerBERT | pll_full_mean | 18/32 | 21/32 | 6 / 3 |

Neutralny lowercase default: 16/32 dla obu okien. Oczekiwany klucz i
alternatywny zapis dostępne we wszystkich 32 przypadkach.

W previous/distant/conflicting każda para proper/common ma identyczne
ostatnie dwa słowa. Krótkie wejście nie rozróżnia pary: przy deterministycznym
wyborze maksimum wynosi 4/8 w każdej z tych kategorii, czyli 20/32 w całej
głównej próbie nawet przy idealnych 8/8 direct. Polbert wwm osiąga ten limit
dla krótkiej historii; długi kontekst przekracza go. To dowód przydatności
starszej informacji w tym kontrolowanym zestawie, bez wniosku o optimum 64.

## Gdzie długi kontekst nadal zawodzi

Trafienia przy długim oknie:

| Model / metoda | Direct | Previous | Distant retained | Conflicting |
|---|---:|---:|---:|---:|
| Polbert wwm | 8/8 | 6/8 | 5/8 | 4/8 |
| Polbert pll_variant | 8/8 | 5/8 | 5/8 | 4/8 |
| Polbert pll_full_mean | 8/8 | 6/8 | 5/8 | 4/8 |
| HerBERT wwm | 6/8 | 5/8 | 5/8 | 5/8 |
| HerBERT pll_variant | 5/8 | 5/8 | 5/8 | 5/8 |
| HerBERT pll_full_mean | 7/8 | 5/8 | 5/8 | 4/8 |

Największa luka to sprzeczne opisy: model otrzymuje jawne rozróżnienie
poprzedniego i aktualnego opisu, lecz wyniki 4–5/8 pozostają słabe. Polbert
popełnia też błędy Malina/Jagoda/Róża jako nazw własnych, gdy wskazówka jest
wcześniej lub dalej w historii. Nie ustalono, czy wynika to głównie z priorytetów
częstości, możliwości łączenia zdań czy szablonu zadania. Nie przypisujemy
przyczyny wewnętrznym mechanizmom modelu bez osobnego pomiaru.

## Pierwotny błąd Łódź — znana próba legacy v1

14 wcześniejszych przykładów oceniono osobno. Wszystkie konfiguracje mają
13/14 poprawnych kluczy: case012 nadal nie zawiera właściwego kandydata.

| Model / metoda | Powierzchnia, 2 słowa | Powierzchnia, długie | Case001 przy długim |
|---|---:|---:|---|
| Polbert wwm | 12/14 | 12/14 | łódź — błąd |
| Polbert pll_variant | 12/14 | 12/14 | łódź — błąd |
| Polbert pll_full_mean | 12/14 | 13/14 | Łódź — poprawnie |
| HerBERT wwm | 12/14 | 13/14 | Łódź — poprawnie |
| HerBERT pll_variant | 11/14 | 13/14 | Łódź — poprawnie |
| HerBERT pll_full_mean | 12/14 | 13/14 | Łódź — poprawnie |

Wnioski potwierdzone kontrolami:
- Błąd case001 nie wynikał z braku formy, utraty starszego tekstu ani różnej
  liczby subwordów: łódź/Łódź mają po jednym tokenie w obu modelach.
- Przy jednym tokenie wwm i pll_variant to dokładnie ta sama ocena wariantu.
  Samo przestawienie agregacji subwordów nie naprawia tego przypadku.
- Przy tym samym Polbert zmiana oceny na cały fragment naprawia case001.
  Przy tej samej metodzie wwm zmiana modelu na HerBERT też go naprawia.
  To potwierdza wpływ modelu i funkcji celu, nie jedną uniwersalną przyczynę.
- HerBERT poprawia legacy, a w większej próbie jest słabszy od Polbert.
  Nie należy wybierać rozwiązania według jednego przykładu albo samych 14 znanych cases.

## Utrata informacji i niejednoznaczność

8 context_lost: wskazówka wypadła poza 64 słowa, obie wersje pary mają
identyczny suffix. Wszystkie konfiguracje dają 4/8 dla obu okien, zgodnie
z limitem dostępnej informacji. Nie zaliczamy tego do głównej jakości AI.

8 ambiguous/ambiguous_short: brak gold labels i brak sztucznej accuracy.
Modele mimo braku rozstrzygającej wskazówki wybierają konkretny zapis.
Przykład HerBERT wwm dla generic Jagoda/jagoda: margin proper−common = 4.597,
mimo że tekst nie określa, czy chodzi o osobę czy owoc. Margin nie jest
skalibrowaną pewnością; w tym modelu warianty mają też różną długość tokenizacji.
To argument za zachowaniem alternatywy i osobną kalibracją, nie za ustawieniem
progu na podstawie tych ośmiu przykładów.

## Walidacja, wykonanie i proweniencja

- 47/47 testów stdlib PASS lokalnie.
- Zamrożony fixture/kryteria: 98badb06118353a1c504bb47d04733624c63ebff.
- Kod ukończonej inferencji: 50e66f77a07ef7a00b3b7e8e27f3695a4c659275.
- [Push CI 37050195897](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37050195897)
  dla kodu inferencji: completed/success; PR run 37050203517 success.
  CI testuje kontrakt, inferencja jest lokalna na CPU.
- Wszystkie wyniki obu okien i trzech metod przeszły walidator request hash
  oraz dopuszczalnych/kompletnych wariantów. Bez gold labels w requests.
- Modele mają pretrained głowice MLM bez brakujących/niedopasowanych wag.
  HerBERT ignoruje tylko jawnie wymienione w protokole wagi poolera/SSO.
- Projekcja wyłącznie ocenianych pozycji zgodna z pełnym forward:
  maksymalny błąd logitów 4.292e-6 Polbert, 3.052e-5 HerBERT.
- Odtworzenie v1 wwm Polbert: te same oceniane tożsamości, maksymalna
  różnica score 6.676e-6; te same decyzje. Nieukończona wolniejsza próba
  została zatrzymana i wyłączona; nie używano jej do ewaluacji.
- Polbert ukończył oba zestawy przed anulowaniem zbędnego uruchomienia HerBERT;
  wyznaczony osobny przebieg HerBERT ukończył się z exit 0.

Runner SHA256: 715f3d165130b486fb3fb74d42b33e4b783360013e2a68d772c853b89552db6d.
Requests UTF-8 SHA256: f8b0004b48b55154b1a87017cdd85a8ab5cc48422a9dc469444411ad00b15289.
Summary SHA256: 2489085be07f13b5801bbb9256937ae143975e86f2be0cea739a0d80f7ccfb02.

[diagnostic-results-2026-10-02](diagnostic-results-2026-10-02) zawiera wszystkie
scores, decyzje, summary, fixture/requests, metadata, environment-freeze,
manifest wag i SHA256 wszystkich artefaktów. Żadnych wag nie redystrybuowano.
HerBERT 124 494 416 parametrów MLM, Polbert 132 775 010; koszt PLL nie jest
kosztem klawiatury, a ślady czasu nie są kontrolowanym benchmarkiem latencji.

## Decyzja i dalszy krok

Zachować dłuższy kontekst i alternatywy jako kierunek. Nie wybrano zwycięskiego
produkcyjnego modelu/metody na tym zestawie; nie zmieniono rankingu kluczy,
Androida, CKDT ani 100k. Nie wdrożono jawnej interpretacji znaczeń z atrybutów
słownika. Licencja redystrybucji Polbert nadal wymaga wyjaśnienia.

Kolejny krok: sprawdzić model wykorzystujący znaczenia dopuszczalnych wariantów,
z przypisaniem sense do surface w danych eksperymentu i porównaniem z tym
baseline’em. Kryteria powinny obejmować sprzeczne wskazówki i niejednoznaczność.
Następnie niezależne zróżnicowane dane z realnymi slates, kalibracja zachowania
przy braku pewności i koszt na urządzeniu. Wyników szablonów nie wolno używać
jako jakości dla użytkowników ani zgody na promocję do main.
