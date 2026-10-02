# Zamrożony protokół diagnostyczny v2

Przed inferencją zamrażamy 48 przypadków i 96 requests. Nie jest to niezależny
benchmark jakości: powstał po zobaczeniu błędu v1, z kontrolowanymi szablonami.
Nie dostrajamy wag ani progów, nie wybieramy tylko zwycięskiej metody.

## Pytania i kryteria

1. Czy wcześniejsze zdanie poprawia trafienia? Liczymy paired naprawy/zepsucia
   dla 2 słów vs do 64 słów, osobno po kategorii i modelu/metodzie.
2. Czy model zmienia wynik? Porównujemy Polbert i HerBERT na identycznych
   requests. Inne tokenizatory są częścią porównywanych systemów, nie izolacją
   samych wag/model architecture.
3. Czy sposób punktowania zmienia wynik? Porównujemy trzy zamrożone metody.
   Przy jednym tokenie WWM i PLL_variant mają dokładnie tę samą wartość z tego
   samego logitu, co pozwala wykluczyć sam sposób agregacji subwordów w łódź/Łódź.
4. Czy model reaguje na sprzeczne wskazówki i odległość? Zestaw ma 8 przypadków
   każdej kategorii direct, previous, distant_retained oraz conflicting: 32
   główne próby, po 16 common/proper. Starszy opis w conflicting jest przeciwieństwem
   aktualnego opisu; gold dotyczy jawnie wskazanego nowego opisu.
5. Kontrole: 8 context_lost (wskazówka wypada poza 64 słowa) raportujemy osobno,
   nie zaliczamy do głównej jakości. 8 ambiguous/ambiguous_short nie ma gold
   labels i nie otrzyma sztucznej oceny poprawności. Raportujemy wybór i margin.
6. Legacy v1 (14 przykładów) odtwarzamy osobno jako znaną próbę diagnostyczną,
   nie łączymy jej z mianownikiem v2 i nie używamy do wyboru hiperparametrów.

## Wejścia i modele

Klucze łódź, malina, jagoda, róża mają lowercase/proper warianty w przykładowym
sidecarze. Model otrzymuje tylko tekst okna i dopuszczalne powierzchnie.
PairId, kategoria, wskazówki semantyczne w metadanych i expected pozostają
wyłącznie w evaluatorze. Żadnego tekstu użytkownika po kursorem ani nowego
kandydata. Klucz i engineScore są niezmienne. Neutralny default jest lowercase.

Modele:
- dkleczek/bert-base-polish-cased-v1,
  fed744e81ebd16cf099b5c64c40688bc3e6ace67, AutoModelForPreTraining;
- allegro/herbert-base-cased,
  50e33e0567be0c0b313832314c586e3df0dc2297, AutoModelForMaskedLM,
  [model card](https://huggingface.co/allegro/herbert-base-cased), CC BY 4.0,
  autorzy Mroczkowski, Rybak, Wróblewska, Gawlik (2021).

Preflight obu tokenizerów i ładowania odbył się przed wynikami jakości.
HerBERT ma pełną pretrained głowicę MLM; brakujące/niedopasowane klucze są
odrzucane. Jedyny jawnie dozwolony zestaw unused weights: bert.pooler.dense
bias/weight i cls.sso.sso_relationship bias/weight, bo factory MLM nie używa
poolera ani osobnej pretrained głowicy SSO. Niczego nie losujemy ani nie trenujemy.
Polbert nie może mieć unused weights. Licencja dystrybucji Polbert pozostaje
nieustalona; żadnych wag nie dodajemy do repozytorium.

## Metody

- **wwm**: wszystkie subwordy wariantu zamaskowane jednocześnie; suma ich
  log prawdopodobieństw (jak v1, bez normalizacji długości).
- **pll_variant**: maskujemy po jednym tokenie wariantu, pozostawiając inne
  jego tokeny widoczne; suma log prawdopodobieństw rekonstrukcji wariantu.
  Może premiować przewidywalność wewnątrz słowa. Nie jest joint probability.
- **pll_full_mean**: w tekście "lewy kontekst + wariant" maskujemy pojedynczo
  wszystkie tokeny tekstu (bez CLS/SEP) i dzielimy sumę przez ich liczbę.
  To sprawdza zgodność całego fragmentu, także rekonstrukcję kontekstu przy
  widocznym wariancie. Nie korzysta z tekstu po kursorem. Mean wybrano przed
  pomiarem; to inna diagnostyczna funkcja celu, nie skalibrowana pewność.

PLL opiera się na istniejącej metodzie: Salazar et al. (2020),
[Masked Language Model Scoring](https://aclanthology.org/2020.acl-main.240/).
Nie implementujemy własnego modelu językowego. Adapter wiąże gotową inferencję
z kontraktem powierzchni. Każda metoda i oba okna będą raportowane.

## Budżety, koszt i decyzja

Do 64 słów/4096 znaków, maksymalnie 512 pozycji z CLS/SEP. Ta sama grupa
wariantów używa identycznego suffixu tokenów kontekstu (rezerwujemy długość
najdłuższego wariantu). CPU float32, 2 wątki, batch 8; eval/inference_mode.
PLL jest kosztowną metodą diagnostyczną, nie obietnicą latencji klawiatury.
Tokenizacja, truncation, rewizje, SHA runnera i kompletne wyniki są zapisywane.
Pusty kontekst zachowuje default jak v1.

Nie ma progu wdrożenia na podstawie tych szablonów. Wynik może uzasadnić
wybór kandydata do oddzielnej ewaluacji z rzeczywistymi slates, ale nie
promocję do main/runtime. Różnic nie wolno nazywać statystycznie istotnymi
ani wskazaniem jednej przyczyny wszystkich błędów.

## Uruchomienie

Istniejące przypięte torch/transformers/numpy z v1 oraz sacremoses==0.1.1.

```bash
python3 experiments/context_surface_v1/build_diagnostic_fixture.py
python3 -m unittest discover -s experiments/context_surface_v1 -p 'test_*.py'
.venv-model/bin/python experiments/context_surface_v1/diagnostic_runner.py --model polbert --requests experiments/context_surface_v1/diagnostic-requests.json --legacy-requests experiments/context_surface_v1/results-2026-10-02/requests.json --output-dir build/context-surface-diagnostic
.venv-model/bin/python experiments/context_surface_v1/diagnostic_runner.py --model herbert --requests experiments/context_surface_v1/diagnostic-requests.json --legacy-requests experiments/context_surface_v1/results-2026-10-02/requests.json --output-dir build/context-surface-diagnostic
```
