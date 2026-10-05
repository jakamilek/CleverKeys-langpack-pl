# Polski MLM 16/32 — zakończona próba v1

2026-10-05. Decyzja: **DistilRoBERTa w badanej rewizji odrzucona dla tego zadania.**
HerBERT pozostaje referencją, bez wdrożenia SI ani zmiany domyślnego okna.

## Tożsamość i wynik wykonania

- Kod/protokół zamrożony przed inferencją: `769fc46579e910f50ff40f5546f0d5ae5643de5b`.
- [Run 37355290211](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37355290211): **FAILURE**.
- Contract job 111916039568: PASS, 11 testów. HerBERT job 111916106489: PASS, 384/384 zapytania.
- DistilRoBERTa job 111916106480: FAIL na walidacji celu, przed oceną jakości.
- Collector job 111916788104: FAIL, prawidłowo odrzucił brak kompletnego drugiego modelu.
- SHA-256 wejścia: `a859aac5acf8dc950c07df415873aced44a46f9a4585818504e3f2af6377449b`.
- HerBERT artifact 11364382538, ZIP 48265 B, SHA-256
  `8ec495775b30b8552cf39da70c0f62eccabac3b90d092e0cf906ee1fe7cb0f02`.
  Pobrano, sprawdzono SHA i ponownie przeliczono kompletny report.json z predictions.json;
  identyczny wynik, zgodność commit/request/freeze. Pliki zachowane w `herbert/`.
- Distil partial artifact 11363564619, ZIP 8992 B, SHA-256
  `ffeddb34435913b747487fe0cb19a0ed4ad13c31830bf097dcae873e696ce4e8`.
  Requests/środowisko, bez ukończonych predictions/validation/raportu porównania.

## Przyczyna odrzucenia DistilRoBERTa

Model `sdadas/polish-distilroberta`, rewizja
`849b664fa3134beae84095d28a184c145c6a3aa5`. W CI wczytał oryginalne wagi
MLM bez brakujących/niedopasowanych/niewyjaśnionych wag; nie doszedł do kontroli
parity projekcji, ponieważ wcześniejsza walidacja wszystkich wejść zatrzymała próbę.

Oryginalny tokenizer zwraca ID **3 (`<unk>`)** dla dużego **Ł** w `Łódź` i `Łotysz`.
Małe `łódź` ma poprawny token 35612. Lokalna diagnoza użyła dokładnego tokenizer.json
z tej samej rewizji, tokenizers 0.22.2 i tej samej funkcji target_positions co protokół;
bez ładowania modelu i bez inferencji. SHA-256 tokenizer.json:
`108af881c403092a16ee515c2ad4a9a72122a3846cfd5c9f2bb860a3fd2bdafa`.

W zamrożonych 384 zapytaniach jest 836 fragmentów kandydatów; **26 fragmentów
w 22 zapytaniach** zawiera nieznany token celu. Dotyczy to również nowych prób
naturalnych i dystansowych, nie tylko historycznych regresji.
Pełne IDs/offsets/przypadki: `distil-tokenizer-diagnosis.json`.
Osobny test pojedynczych liter pokazał `<unk>` także dla Ą, Ć, Ę, Ń, Ó, Ź, Ż;
Ś było rozpoznane. Nie jest to wyczerpujący test wszystkich wyrazów z tymi literami.

To ograniczenie oryginalnego tokenizera tej rewizji, nie dowód błędu Androida/ONNX
ani wyniku trafności modelu. Ocena `<unk>` nie rozróżnia wymaganej pisowni.
Usunięcie Łodzi z próby, zamiana na małą literę, zamiana tokenizera lub ręczne
dopisanie tokenu nie zapewnią oryginalnych wytrenowanych reprezentacji.
W przyszłej aplikacji fallback zachowałby obie formy ze źródła, ale nie oznaczałby,
że SI oceniła poprawnie ten główny przypadek. Nie zmieniono protokołu/gold/danych,
nie osłabiono bramki i nie uruchomiono próby v2 z pomijaniem trudnych kandydatów.

## Ukończona referencja HerBERT — trafność pierwszej pozycji

`allegro/herbert-base-cased`, rewizja `50e33e0567be0c0b313832314c586e3df0dc2297`.
Pełne head/tokenizer/projection checks PASS; 124494416 parametrów.

| Osobna populacja/zadanie | Próby na okno | Źródłowy default top1 | HerBERT 16 | HerBERT 32 |
|---|---:|---:|---:|---:|
| Historyczne formy v5 | 64 | 32 | 50 | 50 |
| Historyczny replay, bez kalibracji geometrii | 8 | 3 | 7 | 7 |
| Nowe naturalne formy | 32 | 16 | 24 | 24 |
| Sztuczny dystans wskazówki | 32 | 16 | 16 | 18 |
| Historyczny przecinek/brak znaku | 20 | 8 | 15 | 15 |
| Nowy przecinek/brak znaku | 24 | 12 | 20 | 20 |

Nowe naturalne formy: 14/16 małych i 10/16 wielkich poprawnie; 10 napraw defaultu,
2 pogorszenia (małe formy). Nowa interpunkcja: 11/12 przecinków i 9/12 bez znaku,
11 napraw oraz 3 pogorszenia. To diagnostyka przecinka przed znanym słowem,
nie bezpieczne automatyczne wstawianie dowolnej interpunkcji.
Jedna dopuszczalna forma: 6/6 z definicji; brakujący gold w dekoderze: 0/2,
nieosiągalny; cztery przypadki niejednoznaczne bez gold, bez accuracy.

Naturalne konteksty mają **6–14 słów**, historyczne 1–13, nowa interpunkcja 2–3.
Wejście dla limitów 16/32 jest więc identyczne w tych populacjach. Równe wyniki
nie dowodzą, że odcięcie dłuższego rzeczywistego kontekstu do 16 jest bezstratne.
Tylko sztuczna populacja dystansowa ma 23–25 słów i różne wejścia. Okno 32 zmieniło
8 pierwszych pozycji: 5 napraw i 3 pogorszenia względem 16. Celowo osobny stress test.

Top3 przy parze dwóch form jest nasycone z konstrukcji listy również bez SI;
nie używamy go jako dowodu jakości SI. To autorskie konteksty znanych leksemów,
nie zewnętrzny ślepy benchmark ani ocena użytkowego dekodowania całych list.

## Koszt i następny krok

HerBERT peak host RSS 1426.48 MiB, CPU Torch FP32 2/1. Naturalne przypadki total
p50/p95: 16 = 84.9/96.6 ms, 32 = 84.3/96.5 ms (identyczne wejście).
Dystans: 16 = 99.9/106.7 ms, 32 = 127.5/136.6 ms. To host CI, **nie** PSS telefonu,
koszt samego modelu, oszczędność Androida ani pomiar energii. Brak kosztu porównawczego
DistilRoBERTa: model nie ukończył próby. Dane hosta nie zastępują raportu Nubii.

Następny kandydat musi najpierw przejść tani test oryginalnego tokenizera na całym
źródłowym zbiorze form, rozróżnianie case i wybranych polskich znakach; potem kontrolę
oryginalnej wytrenowanej głowicy. Dopiero wtedy nowy zamrożony eksperyment jakości,
eksport/parity i RAM/opóźnienia na telefonie. Gdyby wymagał treningu nowego head lub
zmiany słownika tokenów, byłby osobnym projektem, nie łatwą zamianą gotowego modelu.

Bez nowego APK, SI w IME, zmiany default32/max64, merge/release/tag/version bump.
HerBERT FP32 pozostaje referencją; jego wcześniejsze INT8 nadal FAIL.
