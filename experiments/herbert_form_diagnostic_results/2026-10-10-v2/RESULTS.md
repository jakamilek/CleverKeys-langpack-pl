# HerBERT diagnostic V2 — wynik i decyzja, 2026-10-10

Run [38045114375](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38045114375) zakończył się SUCCESS na 90a8398495cd119afce9038f5f55c454db2d6960. Oba jobs contract i measure oraz wszystkie wymagane kroki PASS. Testy: mobile 13, portable 5, V1 13, V2 7. Oryginalna zgodność i odtworzenie V1: PASS.

**Warunek zachowania poprawnych wyników NIE przeszedł: preservationPassed=false.** Status SUCCESS oznacza wykonanie pomiaru, nie zatwierdzenie sum jako scorera.

232 sparowane żądania pochodzą ze 116 wcześniejszych przypadków, każde z krótkim i długim kontekstem. 224 żądania mają gold (w 4 gold nie znajduje się w paczce); 8 niejednoznacznych pozostaje bez gold. Pełne dane są zachowane verbatim w scores.json.

| Grupa | Gold | Mean Top1 | Sum Top1 | Naprawy | Regresje Top1 | Regresje Top3 |
|---|---:|---:|---:|---:|---:|---:|
| forms/reused/short |64|41|40|6|7|0|
| forms/reused/long |64|50|46|4|8|0|
| recorded_replay/reused/short |8|2|6|4|0|1|
| recorded_replay/reused/long |8|7|8|1|0|0|
| single_variant/reused/short |6|6|6|0|0|0|
| single_variant/reused/long |6|6|6|0|0|0|
| ambiguous/reused/short |0|0|0|0|0|0|
| ambiguous/reused/long |0|0|0|0|0|0|
| missing_key/reused/short |2|0|0|0|0|0|
| missing_key/reused/long |2|0|0|0|0|0|
| forms/new/short |32|20|20|5|5|0|
| forms/new/long |32|25|25|5|5|0|

Opisowo w całej historii: Top1 157→157/224, raw group Top3 218→219/224; 25 napraw, 25 regresji Top1, 1 regresja Top3, 60 zmian pełnego rankingu. To nie 232 niezależne nowe zdania ani argument do łączenia grup w jedną ocenę jakości.

Przykłady pogorszeń:
- „pękła dojrzała”: poprawne jagoda → Jagoda.
- „usiadł czarny”: poprawne kruk → Kruk.
- „Znam dwie kobiety o imieniu Luba. Nie pamiętam adresów obu”: poprawne Lub → lub.
- replay-4/short/plain, „się bardzo”: miękko spada z miejsca 2 na 5.

Nowe 24 przypadki V1 odtworzono: mean 18/24, sum 22/24, raw group Top3 23/24 w obu. Cztery naprawy Praca nie równoważą historycznych regresji. Dwa błędy Pracy→pracy pozostają.

## Sprawdzenie i pochodzenie
ZIP artifact 11667083213, 35017 B, SHA-256 c82bccad37fa8e7e5ba1a69ed7e018862fee0091f4bcf08cc81031504d852ab7: pobrany i rehashowany.
scores.json: 188790 B, SHA-256 daeba444338ea0e6ffd012f1a28e29a016d6fdd639b5cb6347c769f5f5034443.
Niezależnie sprawdzono kompletność 232 ID, wyrównanie powierzchni/wyników/liczb tokenów, wartości skończone, mean*targetCount=sum oraz wszystkie 12 grup i metryki. Sprawdzono oba logs i pełny fresh24 replay. Trusted oryginalny model i tokenizer bez zmian.

## Decyzja i kolejny krok
Pozostawić live mean i obecny APK. Odrzucić globalne przełączenie na sum, bez wyjątku dla Praca.
Kolejny eksperyment powinien osobno sprawdzać dobór formy i kapitalizacji oraz odporność na różną tokenizację. Musi zachować te historyczne poprawne wyniki i używać nowych źródłowych rodzin słów. Nie wybrano jeszcze innego scorera ani współczynnika na podstawie tego raportu.
Authored/history gold i raw group Top3 nie zastępują niezależnej oceny ani rzeczywistego paska telefonu. Brak nowego APK, zmiany modelu, merge/release/tag/version bump.
