# Zamrożony protokół: Polbert cased

Ustalony i commitowany przed inferencją, bez zmiany score po obejrzeniu wyników.

Model `dkleczek/bert-base-polish-cased-v1`, rewizja
`fed744e81ebd16cf099b5c64c40688bc3e6ace67`.
Autor: Darek Kłeczek, [model card](https://huggingface.co/dkleczek/bert-base-polish-cased-v1).
Gotowy model z pretrainingu MLM + NSP, whole-word masking. Ładujemy całe
AutoModelForPreTraining, korzystamy wyłącznie z prediction_logits MLM.
Nie ustalono jawnej licencji redystrybucji: wagi nie są dodawane do repo/pakietu;
licencja musi zostać wyjaśniona przed potencjalnym zastosowaniem produkcyjnym.
Preflight tokenizatora potwierdził łódź=[16772], Łódź=[17041]; formy malina/Malina
mają po dwa subwordy. Taki preflight nie ocenia jakości i nie używa gold labels.

1. Model widzi wyłącznie lewe okno kontekstu i maski w miejscu kandydata.
   Cała powierzchnia jest zamaskowana jednocześnie, także przy kilku subwordach.
   Nie używamy tekstu użytkownika po kursorem, gold labels ani atrybutów semantycznych.
2. Score = suma log prawdopodobieństw tokenów wariantu na ich pozycjach maski.
   To wynik zgodności MLM, **nie prawdopodobieństwo całego słowa**. Maski są
   oceniane równolegle; nie są autoregresywnym rozkładem łącznym.
3. Bez normalizacji długości. Różna liczba tokenów może sprzyjać krótszemu
   wariantowi. Zapisujemy dokładną tokenizację, nie wybieramy metody po wynikach.
4. Dla wariantów danego klucza dokładnie ten sam suffix kontekstu; budżet
   512 pozycji obejmuje BOS, EOS i największą liczbę masek w grupie.
   Nadmiar najstarszych tokenów jest odcinany i oznaczany w raporcie.
5. Wagi/głowica MLM muszą być kompletne: brakujące, dodatkowe lub niedopasowane
   klucze przerywają pomiar. Pinned pytorch_model.bin, torch 2.6.0,
   trust_remote_code=False, CPU float32,
   eval/inference_mode, 2 wątki. Zero treningu i losowej głowicy.
6. Wyniki porównujemy tylko między wariantami tego samego klucza. EngineScore
   i kolejność kluczy nie zmieniają się. Puste okno zachowuje słownikowy default;
   jednowariantowe grupy nie wymagają inferencji.
7. Te same 14 ręcznie zbudowanych przykładów i 28 requests: okna 2 i 64 słów
   zachowują case. To pomiar długości, nie emulacja lowercase historii Android.
8. Latencja obejmuje tokenizację i scoring istniejących wielowariantowych grup;
   bez zapisu JSON i bez ładowania modelu. Mierzymy środowisko serwerowe, nie telefon.

## Zatrzymana próba plT5

Pierwszy protokół w MODEL_PROTOCOL.md / commit
`39ce8a543a35018e030f6ac769fe3e8a206c4e4e` przerwał przed scoringiem:
opublikowany tokenizer ma extra_ids=0; standardowe `<extra_id_0/1>` mapują
na unk przy direct token lookup i nie są tokenami specjalnymi. Nie powstał
plik wyników inferencji plT5. Nie dodajemy nowych tokenów/embeddingów i nie
zgadujemy mapowania sentinel-i użytych w treningu. Wybór RoBERTa wynika z
jawnego kontraktu MLM, przed uzyskaniem wyników jakości. HerBERT opublikował
config z architecture=BertModel; w tym etapie nie sprawdzono jego wag MLM.
To nie dowód, że którykolwiek z tych modeli jest bezużyteczny.

## Zatrzymana próba Polish RoBERTa v2

Commit `175375420189d792b7c413ce01b6edaea2b9f96c` próbował tego samego
whole-word-mask score na sdadas/polish-roberta-base-v2, rewizji
4a0bda6ba39e467e204c913cd642700544fc4d3a. Model/głowica załadowały się bez
brakujących wag, ale published tokenizer.json koduje Łódź jako [12,3,4584],
czyli ['▁','<unk>','ódź']. Łódź nie jest poprawnie reprezentowana. Kontrola
odrzuciła wynik przed scoringiem pierwszego przykładu i zapisem JSON.
Nie traktujemy unk jako oceny pisowni; nie poprawiamy na ślepo tokenizatora.
Wybór Polbert nastąpił przed jakimkolwiek uzyskanym wynikiem jakości.

## Odtworzenie

Instalacja jak w MODEL_PROTOCOL.md, te same przypięte pakiety, następnie:

```bash
.venv-model/bin/python experiments/context_surface_v1/mlm_adapter.py --requests build/context-surface/requests.json --output build/context-surface/polbert-predictions.json
python3 experiments/context_surface_v1/prototype.py evaluate --cases experiments/context_surface_v1/cases-fixture.json --sidecar experiments/context_surface_v1/sidecar-fixture.json --predictions build/context-surface/polbert-predictions.json --output build/context-surface/polbert-report.json
```

Aktualny adapter znajduje się w mlm_adapter.py. plt5_adapter.py zachowano jako
zapis zablokowanej próby i kontrolę zgodności; nie należy cytować go jako
wykonanej inferencji ani uruchamiać z dodanymi losowo tokenami.
