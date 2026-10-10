# HerBERT V3 — wynik i odrzucenie metody, 2026-10-10

Run [38046863143](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38046863143) SUCCESS na 523d53e7b4e93db932030ca87a2e62730d7f5d03. Oba jobs i wszystkie wymagane kroki PASS. **allPreservationPassed=false**, każdy z trzech zbiorów nie przeszedł warunku zachowania poprawnych wyników.

Zamrożona metoda: sum_logp(context, same surface) − sum_logp(empty context, same surface). Model, tokenizer i graf pozostały oryginalne; live mean i APK pozostają bez zmian.

| Zbiór | Żądania / labelled | Mean Top1 | Gain Top1 | Naprawy | Regresje Top1 | Regresje raw Top3 |
|---|---:|---:|---:|---:|---:|---:|
| History |232 /224|157|167|29|19|1|
| Form24 |24 /24|18|17|1|2|1|
| New24 |24 /24|20|21|3|2|0|

Opisowe liczby zbioru nie zastępują oddzielnych suite/population/window w surowym raporcie. History to 116 przypadków, każdy short/long; 8 żądań bez gold, 4 labelled gold poza kandydatami. Nie traktować 232 jako tylu niezależnych nowych zdań. Raw group Top3: History218→219, Form24 23→23, New24 24→24; niezmieniony/netto lepszy licznik może maskować stratę konkretnego poprawnego wyniku.

| Zbiór | FormComparable | Mean→gain poprawna forma | Regresje formy | CaseComparable | Mean→gain case przy gold form | Regresje case |
|---|---:|---:|---:|---:|---:|---:|
| History |16|9→14|0|200|144→149|19|
| Form24 |24|20→18|2|24|22→22|1|
| New24 |0|0→0|0|24|20→21|2|

CaseGivenGoldForm porównuje case wyłącznie wewnątrz poprawnej formy; nie zalicza wielkiej litery błędnego wyrazu. FormComparable wymaga dostępnego gold i więcej niż jednego lower-key. Liczniki case/form nie są zamienne z joint ExactTop1.

## Przykłady
- „Gdzie leży wieś ”: mean i gain wybierają Pracą. Gain: Pracą3.166693, pracą0.023317, Praca−1.844588, praca−2.449965. Nie naprawiono problemu odmiany.
- „Odwiedzi nas pani ”: wcześniej poprawne Malina, gain błędnie Maliną.
- „Ta wieś nazywa się ”: wcześniej poprawne Laska, gain błędnie Laską.
- New24 „Nad polem przeleciał wielki czarny ” i „Ten ptak o czarnym dziobie to ”: wcześniej kruk, gain Kruk.
- Gain poprawia niektóre nazwiska Kruk i jeden przypadek Pracy, ale te poprawy nie uzasadniają strat gdzie indziej.

## Zweryfikowane pochodzenie i kontrola
Testy CI: mobile13 + portable5 + V1 13 + V2 7 + V3 18 PASS. Transitive freezes i źródłowe24 nowe cases PASS.
Oryginalne 2471 tokenizer vectors,232 paczki/532 kandydatów, native parity, świeży Form24 i reprodukcja V2 PASS.
280 contextual/gain measurements,46 realnych neutral batches,195 dodatkowych wywołań native, maxSingleBatchScoreError0.
Pobrano ZIP artifact11668485090,89899B; SHA-256 716919e079f178d936de10540fc014698f1ef436f3112fdf9d9a823084f38b63.
Raw scores.json496135B SHA-256 cd125b04f67a69aa0f185a9151e4448dc8f58c134cc40c7a30e5e9487b1f9b76; zachowany verbatim.
Niezależna kontrola: wszystkie280 ID, źródłowe konteksty/pisownie/gold, pełne mean/sum/gain i rankingi, target IDs/counts,46 neutral feeds/attention/padding/positions/masks, sum=mean*count i gain=contextSum−neutralSum; wszystkie metryki każdej grupy i pełna reprodukcja historycznych wyników/frozen inputs PASS. Nie jest to lokalna nowa inferencja, lecz kontrola CI output.

## Decyzja
Odrzucić globalny gain scorer; pozostawić obecną klawiaturę i mean. Nie dobierać współczynnika na tym samym zestawie ani wyjątku dla Praca.
Dalsza hipoteza diagnostyczna: ocena zgodności obserwowanego fragmentu zdania z widocznym kandydatem (wspólne maskowane słowa kontekstu dla wszystkich kandydatów), z osobnym pomiarem kosztu. To niewdrożony pomysł, nie sprawdzony scorer ani obietnica poprawy. Wymaga osobnego zamrożonego protokołu, źródłowych form, historycznych gates i nowych rodzin odmian.
Dwa sprawdzone przeliczenia target scores — sum oraz gain — nie dały bezpiecznej poprawy. Nie oznacza to, że każda możliwa metoda oceny albo sam HerBERT musi zawieść.

## Ograniczenia
Authored/frozen gold, nie niezależny blind benchmark. New24 ma nowe konteksty znanych słów; Form24 tylko cztery rodziny. Pusty baseline zmienia pozycję i prior początku zdania; subtraction usuwa też użyteczną częstość. Host/cache bez dowodu phone latency/routing, full-strip Top3 lub ekonomicznej gotowości Androida.
Brak APK/model/langpack/live-threshold zmiany, merge/release/tag/version bump.
