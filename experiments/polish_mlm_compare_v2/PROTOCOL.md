# Polski MLM v2 — dwa mniejsze modele, 16/32 słowa

2026-10-05. Osobny eksperyment po zakończeniu v1 FAILURE. Użytkownik autoryzował
poszukiwanie kolejnego lekkiego modelu. Wcześniejszy kod/dane/gates/wyniki v1 niezmienne.
Wybrano dwa istniejące sześciowarstwowe oryginalne pretrained MLM, bez treningu.

| Nazwa | Oryginalny model | Rewizja | Licencja/status |
|---|---|---|---|
| geotrend_distil | Geotrend/distilbert-base-pl-cased | 9002d311e35aac14575bf53ad4fa3d8f8b853c2b | Apache-2.0 wg karty |
| distilherbert | BartekK/distilHerBERT-base-cased | 7276461b7a8fd668aaf30313c03a68bd11aad642 | brak deklaracji licencji wag; bez redystrybucji |

Geotrend config: DistilBertForMaskedLM, dim768/6/12heads/vocab22397; API safetensors
60737405 parametrów, oryginalny header zawiera transform/layernorm/projector bias
oraz tied embedding. Header odczytany bounded HTTP Range, nie pełne wagi.
To nie potwierdza jeszcze loading/parity/accuracy/Android. distilHerBERT config:
BertForMaskedLM, 6/768/12heads/vocab50000, oryginalny HerbertTokenizerFast.
Rzeczywistą liczbę parametrów distilHerBERT ustali runner, nie szacunek z nazwy.
Nie zakładamy, że licencja HerBERTa automatycznie obejmuje cudze wagi po destylacji.
Bez model weights w Git/artifact/APK; publikujemy tylko małe wyniki i źródłowe identyfikatory.

## Tani screening przed wagami

experiments/polish_mlm_screen_v2/screen_tokenizers.py używa oryginalnego AutoTokenizer
Transformers4.57.6/tokenizers0.22.2, trust_remote_code=False; bez Torch i wag.
Pełny pack v5 SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
dictionary SHA a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a,
sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
106363 CKDT klucze,16199 wpisów sidecar,16117 wielowariantowych kluczy,
122480 unikalnych źródłowych form. Wyłącznie istniejące formy/atrybuty, bez ręcznych opisów.

- distilHerBERT: zero unknown form/empty/collapsed pairs,384 requests/836 target spans PASS.
- Geotrend Distil i Geotrend BERT: wszystkie wielowariantowe wpisy i384 requests PASS;
  pełny zbiór nie ma100% coverage: samodzielne źródłowe ą/ę są unknown. Nie usunięto ich
  z raportu. Pojedyncze znaki ąęńĄĘŃ również unknown; nie są tym samym co całe słowa
  z tymi znakami. Wszystkie źródłowe pary rozpoznane i rozróżnione, nie uniwersalny Unicode.
- Geotrend BERT12warstw/103266173 F32params plus512 I64buffer: rezerwa, nie ładowany.
- ORIS Small C: karta25.41M, research gated/custom code. API odmówiło401, plików i wag
  nie pobrano; dostęp/licencja/MLM oraz własna architektura wymagają osobnego etapu.
- sdadas/polish-distilroberta v1 nadal odrzucony dla Łódź/Łotysz; nie retry.

W v2 do oceny trafiają tylko te same wszystkie384 requests; ŻADNE target unknown,
invalid budget/span ani collapsed pair nie jest tolerowane. Znane dwa samodzielne
wpisy nie występują w zapytaniach oceny par; nie dodajemy wyjątków do encode().
Przyszła SI powinna fallbackować na źródłowe propozycje przy niewspieranym wejściu;
ten eksperyment nie implementuje fallbacku ani nie zalicza go jako trafność SI.

Runtime runner najpierw pobiera oryginalny tokenizer pinnedrevision, wymaga exact
backend SHA lokalnego screeningu, sprawdza wszystkie384 wejścia i zapisuje
tokenizer-validation.json BEFORE weights. Dopiero później pełne wagi i model.

## Dane, metoda i historyczna referencja

Te same192 cases i384 queries16/32 z v1, bez nowego authoring/zmiany gold/slate/metadata.
Zmieniony tylko identyfikator protokołu żądania na v2; wejściowe teksty/formy/order/IDs
identyczne. V1 HerBERT już widziany i zapisany; to diagnostyka porównawcza znanych
kontekstów/leksemów, nie ślepy niezależny benchmark. Wybór modeli oparty na rozmiarze,
dostępności i tokenizerze przed oglądaniem ich predictions.

Osobno regression_v5=104,new_natural=32,new_distance_control=32,new_punctuation=24.
Naturalne6–14słów, stare1–13, nowa interpunkcja2–3:16/32 identyczne, żadnej decyzji
o skróceniu realnego kontekstu do16 z tych wyników. Sztuczna wskazówka23–25słów
różni okna: raportować pary i wszystkie regresje bez poolowania populacji.
Przecinek/brak wyłącznie przed znanym kolejnym słowem; nie ogólna interpunkcja.
Top3 dwóch form nasycone z definicji również bez SI, nie korzyść AI.

Referencja: oryginalny HerBERT384 predictions z kodu
769fc46579e910f50ff40f5546f0d5ae5643de5b, run37355290211/artifact11364382538,
ZIP SHA 8ec495775b30b8552cf39da70c0f62eccabac3b90d092e0cf906ee1fe7cb0f02.
Collector wiąże raw prediction/report/validation hashes przez manifest; wymaga
oryginalnego commit/request/freeze i dokładnej recomputation v1 report.
Historyczny commit jest jawnie inny od bieżącego dwóch nowych modeli; brak kolejnego
pobierania dużych wag HerBERTa. Paired quality porównuje te same cases/gold/baseline;
czasy/RSS różnych uruchomień/runnerów nie są kontrolowanym paired performance test.

Bez zmian scoringu: mlm.py byte-identical v1; całe maskowane target subwordy,
pełne oryginalne vocabulary logsoftmax,mean logp, sum/IDs/positions trace, right padding.
DistilHerBERT bez adaptera używa original model.bert/cls.predictions.
DistilBERT adapter tylko udostępnia oryginalne distilbert i dokładną sekwencję
vocab_transform→model.activation→vocab_layer_norm→vocab_projector. Pełny forward
delegowany do oryginalnego modelu, bez nowych parametrów/losowego head.
Wymagane3 parity allclose probes atol1e-4/rtol1e-5 z original full-vocab logits.
Jakiekolwiek missing/mismatched/error/unexpected w loading_info FAIL (żadnych wyjątków).
Wymagane revisions/config arch6layers hidden768, original head/tokens/budgets.

## Zamrożenie, wykonanie i kryterium

freeze-manifest wiąże v2 executables/workflow/docs/requirements, niezmienne v1,
v5 source/cases/contract, screening report+code i historyczne HerBERT raw wyniki.
Sam manifest nie hashuje siebie. Requests label-free: tylkoid/caseId/window/context/candidates;
model widzi text/mask, bez gold/kategorii/prompt/IDs. manifest/code przed predictions.
Zmiana metody po wyniku wymaga jawnej nowej próby, nie poprawy bramki.

CPU torch2.8.0/transformers4.57.6, FP32,2/1threads,3warmups,firstwindowalternatebycase;
deps transitive zapisane pipfreeze. Osobne CPUjobs, host timing/RSS perpop/window.
Collector wymaga obu nowych kompletnych384wyników, finite scores/times, tej samej
bieżącej40-hex codeidentity,request/freeze/model/tokenizer/prefight/projectionidentities.
Niepublikowane wagi,phoneMeasuredFalse. Brak jednego wyniku zatrzymuje collector.

Wstępny screen case-only zachowuje kryterium v1: new_natural32 top1>=HerBERT-1
i baseline regressions<=HerBERT+1 (referencja24/32 i2regresje, więc minimum23 i maksimum3).
To mały exploratory screen do rozważenia kolejnego etapu, nie statystyczna noninferiority
ani production approval. W2 zapisujemy tylko identicalShortInputsCheck zamiast sugerować,
że jednakowe krótkie wejścia potwierdzają jakość ograniczenia16. Punctuation i distance osobno.
Nawet PASS potrzebuje niezależnych realnych kontekstów, legalnego modelu, export/parity
i RAM/p50/p95/energii telefonu przed SI w IME. Fail nie oznacza zmiany geometric/słownika.

Monitoring Actions <=60seconds TOTAL/run, potem użytkownik podaje zakończenie; bez watch/sleep.
Brak merge/release/tag/version bump/APK/liveAI/default32 change. INT8 HerBERT pozostajeFAIL.
