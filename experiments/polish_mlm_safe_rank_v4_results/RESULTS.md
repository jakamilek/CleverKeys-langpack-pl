# Ostrożny ranking v4 — wynik negatywny na nowych kontekstach
Data: 2026-10-06, Europe/Warsaw.
Run37502851581 SUCCESS, wszystkie4jobsSUCCESS:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37502851581
Frozen executable7d7d3ec4f7be31476df11f198dfcc2b21d813e5b.
256 requests/model. TrzyZIP SHA256 PASS; komplet obu modeli, tokenizer/loading/
original-head/full-forward parity/trace PASS. Lokalny collector z tym GITHUB_SHA
odtwarza comparison.json i Markdown dokładnie.

## Primary: nowe64 konteksty, window16
| Metoda | Top1 | Naprawy źródłowego defaultu | Błędne nadpisania poprawnego defaultu |
|---|---:|---:|---:|
| Źródłowy default |32/64|0|0|
| HerBERT raw |50/64|19|1|
| distilHerBERT raw |48/64|17|1|
| distilHerBERT próg0.25 |46/64|15|1|

Gated16 overrides16, utility repairs−4*regressions=11 vs raw13.
6 z7 kryteriów PASS, utilityAtLeastRaw FAIL -> exploratorySafeCandidate=false.
Nie zmieniamy progu ani kryterium po holdout. W tej próbie próg usuwa dwie
trafne poprawki i nie zatrzymuje jedynej błędnej poprawki; brak poprawy bezpieczeństwa.
To wynik nowej walidacji kontekstów, nie development calibration.

## Konkretne rozbieżności primary
- „Rozliczenie podpisał właściciel pan”: goldKoza, rawKoza, gatedkoza; margin0.0495.
- Kontekst sprzedawcy z nazwiskiem na identyfikatorze: goldKot, rawKot, gatedkot;
  margin0.1947.
- Kontekst zwierzęcia w kapuście: goldzając, rawZając i gatedZając; margin0.4602.
Wyższa przewaga score nie gwarantuje poprawności. Nie jest pewnością/probability.
Brak wyjątków per-word i brak dalszego strojenia na tych tekstach.

## Secondary window32
HerBERT48/64 (regresje6), rawdistil47/64 (regresje2),
gated46/64 (regresje2, repairs16, overrides18, utility8).
Nie dobieramy window po wynikach. Default32 aplikacji bez zmian.

## Development replay, NIE nowa walidacja
Historical64 rawHerBERT50/64, rawdistil46/64, gated46/64 w obu oknach.
Rawdistil: repairs16/regressions2; gated: repairs14/regressions0.
Gated na znanych danych eliminuje2 regresje i pomija2 trafne zmiany, top1 bez zmian.
Stary referencyjny próg>=49 nadal FAIL dla rawdistil.
Calibration na256 requests poprzedniego v3 wybrała0.25, development
216->214 top1 i8->4 regresje; nie dowodzi nowego bezpieczeństwa.

## Zakres i koszt
Źródłowe dwie formy zawsze zachowane. Top3 jest nasycone już bezSI;
nie przedstawiać tego jako korzyści modelu.
Nowe teksty autorskie po v3, znane16 kluczy, context holdout, nie key holdout,
bez zewnętrznego anotatora/humanblind. Brak statystycznej oceny produkcyjnej.
Parametry HerBERT124494416/distil81967184.
Host peakRSS1427.91MiB/950.45MiB z osobnych jobs, nie AndroidPSS.
Brak liveSI, model weights, APK, eksportu lub phone testu distil.
License review odłożony przez użytkownika, nie założono licencji.
Słownik i czasy stacjonarnegoBS nadal backlog.

## Decyzja i następny krok
Nie kwalifikować prostej reguły margin0.25 do wdrożenia na podstawie v4.
Nie stroić kolejnej granicy na tych samych przypadkach i nie nazywać tego walidacją.
Ten FAIL dotyczy konkretnej reguły/rankingu i małego zbioru, nie dowodzi,
że każda SI lub każdy sposób wykorzystania distilHerBERT jest nieskuteczny.
Przed kolejnym eksperymentem rozstrzygnąć cel: kontekstowe rozróżnianie źródłowych
form i metadanych potrzebuje bardziej odpowiedniej metody niż utożsamienie
score MLM z pewnością. Nowa metoda/model wymaga osobnego protokołu i nowych danych.
Nie wykonano nowego runa, ONNX/INT8 lub wyboru modelu do produkcji.

## Proweniencja i odtwarzanie
Request SHA84ec2282a35f0e96b4020c42c6e9bca8376b00b712d7653adf2148f4541a3f60.
Freeze file SHA256 5c16b760927e70d89131a0d2a10a5c5d6bce90d9ac9985f09a68d5afc5705a07.
Raw files i artifact-provenance.json zachowane bez wag.
Collector odtwarzać z frozen executable7d7d3... i GITHUB_SHA7d7d3...;
późniejszy commit archiwum nie jest commitem inferencji.
