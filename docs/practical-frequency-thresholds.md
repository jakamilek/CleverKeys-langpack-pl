# Porównanie progów dla 911 słów — 14.10.2026

Wyłącznie eksperyment selekcji na zamrożonych wynikach. Bez zmiany wag, v11,
zatwierdzeń, langpacka i APK. Wszystkie 911 ma zwykłe potwierdzenie SGJP,
ale nie przeszło dotychczasowej polityki częstości; testujemy niższy próg formy.
Warunek silnej rodziny nie dodaje tu żadnego słowa przy progu >=1, ponieważ
takie słowa już przeszły poprzednią selekcję i nie należą do tych 911.

| Minimalny Zipf | Przechodzi z 911 | Nadal odpada | Pozostałe miejsca po wcześniejszych 1336 i tym wariancie |
|---|---:|---:|---:|
| 2,0 | 0 | 911 | 4365 |
| 1,8 | 74 | 837 | 4291 |
| 1,5 | 220 | 691 | 4145 |
| 1,2 | 342 | 569 | 4023 |
| 1,0 | 422 | 489 | 3943 |
| 0,5 | 422 | 489 | 3943 |
| 0,0 (wyłączenie filtra) | 911 | 0 | 3454 |

## Co nadal tracimy

| Próg | Przykłady nadal odrzucone (Zipf) |
|---|---|
| 1,8 | grzałka 1,79; domówka 1,78; golarka 1,67; poziomica 1,59 |
| 1,5 | touchpad 1,49; szpachla 1,47; resetować 1,40; gigabajt 1,25 |
| 1,2 | uszczelniać 1,18; kalibrować 1,09; formatować 1,04; wkrętarka 1,03 |
| 1,0 i 0,5 | bezawaryjny, glukometr, podfolder, wylogowywać, anonimizacja, rekuperator — wszystkie 0,0 |

Dobór przykładów ilustruje potencjalną użyteczność, jest oceną praktyczną,
nie niezależnym pomiarem częstości. Nie dowodzi, że wszystkie pozostałe
słowa są zbędne. W zerowej grupie są też np. aksoida, amplidyna, ebulioskopia
i studwudziestoośmiobitowy: nie mają większego ani mniejszego wyniku niż
wylogowywać. Ten wskaźnik nie rozstrzyga więc ich względnej użyteczności.

Wśród 911 jest dokładnie 489 wyników 0,0 i zero wyników z przedziału (0;1).
Przy obniżaniu progu poniżej 1,0 nie otrzymamy stopniowo kolejnych grup.
Implementacja przypiętego wordfreq używa 0 jako domyślnego minimum również
dla słów bez zarejestrowanego wystąpienia. Sam odczyt 0,0 nie ustala, czy
konkretny klucz nie występuje w danych, czy znalazł się poniżej rozdzielczości.

Źródło semantyki API, funkcja zipf_frequency:
https://github.com/rspeer/wordfreq/blob/912caf64b657478d1dff1138efdc078947d54bb1/wordfreq/__init__.py

## Koszt i wniosek

422 propozycje przy progu 1,0 sumują się do 75968 bajtów i 4603 elementów JSON.
Całe 911: 160410 bajtów i 9710 elementów JSON. To suma zapisanych propozycji,
bez dodatkowego opisu etapu; nie nowy pomiar gotowego langpacka ani RAM.
Nie ma potrzeby podnoszenia limitów z powodu tej grupy.

Rekomendacja: 1,0 jako szersza pula do dalszej oceny, nie automatyczna zgoda
na instalację. Pozostałe 489 przenieść z etykiety sugerującej nieprzydatność
do osobnej ścieżki „brak rozstrzygającego sygnału częstości”. Nie odrzucać ich
wyłącznie z powodu 0,0. Zachować wymagania dotyczące pisowni, znaczeń,
kapitalizacji i źródeł. Nie przypisywać wszystkim równych wag.

Odtworzenie: uruchomić scripts/compare_practical_thresholds.py z parametrami
--decisions wskazującym pierwotne decisions.jsonl i --out wskazującym nowy katalog.
Wyniki zawierają pełne listy dla każdego progu oraz SHA-256 wejścia.
