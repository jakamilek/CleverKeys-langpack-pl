# Porównanie SI v5 — wyniki i kandydat do próby mobilnej

Data: 2026-10-04. Wszystkie trzy modele wykonały rzeczywistą inferencję.
Run [37218630239](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37218630239): SUCCESS, w tym kontrakt, trzy modele i porównanie.
Kod, dane, adaptery i kryteria były zamrożone przed inferencją w commicie `00a7bf5999e8f6419a68c1884919e699c744a927`.

**Rekomendacja: HerBERT bez tekstowego prefiksu metadanych, z dłuższym kontekstem, jako pierwszy kandydat do niezależnej walidacji i pomiarów mobilnych.** To wybór do dalszej próby, nie zatwierdzony silnik produkcyjny. Geometric pozostaje dekoderem; alternatywy źródłowe pozostają w słowniku i pasku wyboru.

## Weryfikacja wykonania

Pobrano cztery artefakty przez konektor GitHub. Ich ZIP SHA256 zgadzają się z logami upload/download. Lokalnie ponownie wykonano zamrożony collector na surowych przewidywaniach: cały obiekt `comparison.json` jest identyczny z wynikiem CI.

Każdy model ma dokładnie 376 kompletnych zapytań, skończone oceny wyłącznie dla dozwolonych kandydatur, zgodny commit kodu, identyczny payload wejść, snapshot i manifest zamrożenia. Loading nie ma brakujących lub niedopasowanych wag; HerBERT ma wyłącznie cztery uprzednio dozwolone nieużywane wagi poolera/SSO. Sprawdzono zgodność zoptymalizowanej projekcji z pełnym forward dla HerBERT i Qwen. Żadne wejście nie wymagało skrócenia kontekstu do budżetu tokenów. Nie dostrajano danych, promptów ani metod po wynikach.

104 przypadki to diagnostyka napisana przed nową inferencją: 64 formy, osiem historycznych rankingów gestów, sześć kontroli jednej formy, cztery przypadki niejednoznaczne bez etykiety poprawnej odpowiedzi, dwie kontrole brakującego klucza i 20 prób przecinka.

## Wybór kapitalizacji: 64 przypadki, długi kontekst

| System | Poprawna forma na miejscu 1 | Naprawy / regresje wobec defaultu v5 |
|---|---:|---:|
| Default v5 | 32/64 | — |
| HerBERT bez tekstu metadanych | 50/64 | 21 / 3 |
| HerBERT z tekstem metadanych | 49/64 | 25 / 8 |
| MiniLM bez tekstu metadanych | 28/64 | 23 / 27 |
| MiniLM z tekstem metadanych | 29/64 | 26 / 29 |
| Qwen3-0.6B bez tekstu metadanych | 36/64 | 23 / 19 |
| Qwen3-0.6B z tekstem metadanych | 35/64 | 27 / 24 |

Top 3 wynosi 64/64 dla wszystkich, również defaultu, ponieważ każdy przypadek zawiera dwa warianty jednego klucza. Jest to własność konstrukcji testu i nie dowodzi przewagi SI. Baseline dotyczy faktycznych wariantów jednego wpisu v5; nie zakłada zdublowanych wpisów CKDT.

HerBERT bez tekstu metadanych poprawił się z 41/64 przy dwóch poprzednich słowach do 50/64 przy pełnym kontekście. W długim oknie trafił 29/32 małych i 21/32 wielkich liter. Nadal myli niektóre nazwy własne: np. jeden kontekst miasta Łódź, nazwiska Tutaj i odmiana imienia Ale. Ma trzy regresje zwykłej pisowni: lub, sowa, zając. Wynik nie uzasadnia punktowych wyjątków dla tych słów.

MiniLM w długim oknie bez metadanych trafił tylko 5/32 małych liter i 23/32 wielkich. Qwen odpowiednio 13/32 i 23/32. To wyniki konkretnych zamrożonych modeli z adapterami; nie ocena wszystkich modeli NLI ani całej rodziny Qwen.

## Wpływ metadanych

W bezpośrednim porównaniu HerBERT z/bez metadanych, przy długim kontekście, metadane naprawiły sześć odpowiedzi i pogorszyły siedem. Dla MiniLM było to dziesięć napraw i dziewięć regresji, a dla Qwen pięć napraw i sześć regresji. To porównanie sparowane; różni się od porównania każdego warunku z defaultem.

Metadane pomogły HerBERTowi np. przy części nazw Łódź, Jagoda, Róża, Warszawska, Lis i Kruk. Jednocześnie niektóre zwykłe jagoda/róża podniosły do wielkiej litery oraz pogorszyły dwie odpowiedzi Lub. Nie potwierdzono więc globalnej korzyści z doklejania pełnego opisu pól źródłowych do wejścia modelu.

**Metadane pozostają potrzebne do dopuszczalnych form, ich powiązań źródłowych i defaultów.** Wynik dotyczy ich konkretnego tekstowego podania modelowi bez dodatkowego treningu. Nie dowodzi, że słownik należy pozbawić atrybutów ani że model nauczony korzystać z nich nie może zyskać. Nie dobieramy warunku metadanych osobno dla każdego słowa po zobaczeniu błędów.

## Historyczne rankingi gestów: osiem kontekstów, długie okno

| System | Dokładna forma top 1 | Dokładna forma top 3 |
|---|---:|---:|
| Default v5 | 3/8 | 7/8 |
| HerBERT bez metadanych | 7/8 | 8/8 |
| HerBERT z metadanymi | 7/8 | 8/8 |
| MiniLM bez metadanych | 2/8 | 3/8 |
| MiniLM z metadanymi | 0/8 | 1/8 |
| Qwen bez metadanych | 2/8 | 3/8 |
| Qwen z metadanymi | 2/8 | 4/8 |

HerBERT z długim kontekstem bez metadanych ma cztery naprawy i zero regresji wobec defaultu w tej części. Jedyny błąd top 1 to klisz zamiast kosz; kosz pozostaje drugą podpowiedzią. Metadane zmieniły dwie odpowiedzi top 1: jedna naprawa i jedna regresja, bez zmiany wyniku 7/8.

To historyczne top 5 i scores z logu użytkownika, z nowymi kontekstami. Brak surowych punktów gestu i świeżego replay v5. Modelowe sortowanie nie zawiera skalibrowanego połączenia z geometrią. Osiem przypadków nie wystarcza do potwierdzenia jakości produkcyjnego rankingu.

## Możliwość rozszerzenia o interpunkcję

| System | Przecinek / brak znaku przed znanym słowem |
|---|---:|
| Default bez przecinka | 8/20 |
| HerBERT | 15/20 |
| MiniLM | 12/20 |
| Qwen | 8/20 |

HerBERT ma dziewięć napraw i dwie regresje wobec braku przecinka. Nadal pominął przecinek w trzech przypadkach i dopisał go w dwóch zbędnie. MiniLM wybierał przecinek we wszystkich 20 przypadkach; Qwen nie wybierał go w żadnym. Ich wyniki nie dowodzą kontekstowej zdolności w tej próbie. HerBERT jest obiecującym kandydatem do dalszego badania tej funkcji, lecz 15/20 nie uzasadnia automatycznego wstawiania znaków.

Badamy tylko dwa warianty przed znanym kolejnym słowem. Nie badamy całej interpunkcji, końca zdania ani wspólnego wyboru słowa i znaku. Docelowy moduł może wymagać innej głowicy lub osobnego modelu.

## Koszt wykonania: host CI, CPU float32, dwa wątki

| Model | Liczba parametrów w załadowanym modelu | p50/p95 formy, długi kontekst bez metadanych | Szczytowy RSS procesu hosta |
|---|---:|---:|---:|
| HerBERT | 124 494 416 | 116/141 ms | 1451 MiB |
| MiniLM | 106 995 075 | 14/15 ms | 1042 MiB |
| Qwen3-0.6B | 596 049 920 | 1456/1548 ms | 4850 MiB |

HerBERT z metadanymi: 296/466 ms; ocena wielokluczowego replay bez metadanych: 432/473 ms. Ten prosty adapter osobno ocenia warianty i nie jest zoptymalizowaną ścieżką Androida. RSS obejmuje cały proces, również ładowanie i biblioteki. Modele działały na oddzielnych hostach; nie jest to ścisły pomiar na identycznym sprzęcie ani prognoza pracy telefonu. Liczby parametrów pochodzą z faktycznie załadowanych obiektów, nie nazw modeli lub metadanych serwisu.

Nubia Z60 Ultra LV 12 GB / 512 GB nie była mierzona. Jej pamięć nie rozstrzyga płynności, energii ani opóźnienia. Potrzebny jest test eksportu/kwantyzacji i realnego runtime mobilnego przed integracją.

## Następny krok

1. Utrzymać HerBERT bez prefiksu metadanych jako kandydata, zachowując atrybuty i wszystkie formy v5.
2. Zaplanować nową niezależną próbę z rzeczywistymi kontekstami i szerszymi rankingami geometric; ustalić kryteria przed inferencją. Nie dostrajać wag na obecnych ośmiu replay.
3. Sprawdzić eksport i kwantyzację mobilną oraz jakość po konwersji. Następnie zmierzyć start, p50/p95, pamięć, energię i płynność na telefonie użytkownika.
4. Dopiero po tych wynikach zaproponować opcjonalną integrację. Interpunkcja wymaga osobnej dalszej walidacji.

## Trwałe pliki i artefakty

Obok tego dokumentu zapisano surowe `herbert/predictions.json`, `minilm/predictions.json`, `qwen/predictions.json`, odtworzone `comparison.json` i `artifact-manifest.json`. Zamrożone wejścia odtwarza `experiments/ai_compare_v5/contract.py`; wyników nie trzeba ponownie inferować.

Artefakty runu: HerBERT 11309790672, MiniLM 11309850447, Qwen 11309861780, comparison 11309302947. Manifest zawiera SHA256 pobranych ZIP i trwałych plików; każda predykcja zapisuje hashe faktycznych plików modelu i środowisko. Wagi nie są publikowane. Aplikacja, CKDT, langpack v5 i zamrożone kryteria są niezmienione. PR pozostaje draft, bez merge/release.
