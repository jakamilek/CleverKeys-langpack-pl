# Polski MLM: HerBERT / DistilRoBERTa, 16 / 32 słowa — protokół v1

2026-10-05. Użytkownik zatwierdził porównanie po pomiarze dużego PSS HerBERTa na Nubii.
To izolowana próba hosta CI, bez APK, treningu, kwantyzacji lub aktywnej SI.

## Modele i źródła

| Model | Stała rewizja | Metoda |
|---|---|---|
| allegro/herbert-base-cased | 50e33e0567be0c0b313832314c586e3df0dc2297 | oryginalny MLM BERT |
| sdadas/polish-distilroberta | 849b664fa3134beae84095d28a184c145c6a3aa5 | oryginalny MLM RoBERTa |

Rewizję DistilRoBERTa odczytano z API autora przed inferencją. Pobrana konfiguracja
deklaruje RobertaForMaskedLM, 6 warstw, hidden 768, vocab 50001 i max positions 514.
Oryginalny tokenizer.json: Unigram, NFKC, WhitespaceSplit/Metaspace, RobertaProcessing.
Nie używamy tokenizera HerBERTa dla RoBERTa ani jego mobilnego adaptera.
Licencje kart: CC BY 4.0 / Apache-2.0; NOTICE.txt. Wagi nie są redystrybuowane.

Pełne loading_info wymagane: brak missing/mismatched/error i niewyjaśnionych
unexpected weights. HerBERT dopuszcza tylko swoje cztery historyczne wagi
poolera/SSO; DistilRoBERTa żadnych. Sprawdzić config commit/architekturę/warstwy,
case preservation każdego źródłowego wariantu i brak unknown target token.
Wybrane projekcje MLM wymagają allclose z pełnym pretrained forward, atol1e-4,
rtol1e-5. Brak losowego nowego head, trust_remote_code=False.

## Dane zamrożone przed inferencją

192 przypadki, 384 zapytania na model (dwa okna), 768 wyników łącznie:

- 104 oryginalne przypadki v5, bez zmian gold/kontekstów. W tym 64 formy,
  8 historycznych niekalibrowanych replay, 6 jednej formy, 4 niejednoznaczne,
  2 gold nieobecne w dekoderze i 20 przecinków. Raport jako regression_v5.
- 32 nowe naturalne autorskie konteksty, te same 16 kluczy, po jednej małej
  i wielkiej literze: new_natural. Nie zewnętrzny ślepy zbiór ani nowe leksemy.
- 32 nowe kontrolowane konteksty odległej wskazówki: new_distance_control,
  po obu formach tych samych kluczy. Długość >16 i <=32 słów; 32 zachowuje cały
  tekst, 16 usuwa początkową wskazówkę. Celowo wspólny neutralny łącznik;
  sztuczny stress test, nigdy nie łączyć z naturalnymi, żeby podnieść accuracy.
- 24 nowe próby przecinek/brak znaku, po 12 każdej etykiety: new_punctuation.
  Tylko znak PRZED znanym kolejnym słowem, nie cała interpunkcja/koniec zdania.

Źródłowe formy i metadane z niezmienionego source-snapshot v5 (blob 6682a95b);
pack SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecar 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d.
Rodzic ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3; wcześniejsze wyniki niezmienne.
Wszystkie nowe gold par muszą być źródłowo dopuszczalne. Brak ręcznych opisów
znaczenia w słowniku; autorskie wskazówki dotyczą tylko tekstów diagnostycznych.
Badamy plain, bo poprzednie prefix/instrukcja nie ustaliły korzyści. Metadane
nadal kontrolują dopuszczalne formy i default, nie są porzucone.

## Wejście, scoring i kolejność

Okna 16/32 ostatnich słów, <=4096 znaków; zachowujemy dokładny sufiks tekstu,
case, polskie znaki i interpunkcję. Token budget 512; przekroczenie/nieznany
target zatrzymuje całą próbę, bez dodatkowego skracania/wyłączania trudnych przypadków.
Requests zawierają tylko id/caseId/window/context/candidates, żadnego gold/populacji,
semantycznych kategorii czy contextType. Model otrzymuje wyłącznie polski tekst
i maski; same request IDs nigdy nie są częścią wejścia neuronowego.

Tokenizacja całego context + spacja + wariant przez oryginalny fast tokenizer
z offsets. Maskujemy wszystkie subwordy dopisywanego wariantu jednocześnie;
token nie może obejmować niebiałego znaku z końca kontekstu. Nie analizujemy
tekstu po kursorze. Przecinek jest częścią maskowanego celu „, słowo”.
Oryginalna projekcja pełnego vocabulary i log_softmax; score to średnia logp
tokenów celu. Suma/token IDs/positions również w trace. To ustalona normalizacja,
nie idealna izolacja efektu tokenizacji ani skalibrowana pewność.
Batch obejmuje kandydatury żądania; projekcja tylko na pozycjach celów, bez
pełnej macierzy logitów wszystkich słów podczas scoringu. Parity forward jest
obowiązkowe przed zapisem jakichkolwiek wyników jakości.

Wszystkie wejścia walidowane przed głównym scoringiem; loading/files/projection
validation.json zapisane przed oceną. Trzy rozgrzewki. Okno pierwsze zmienia się
naprzemiennie między przypadkami, kolejność wariantów deterministycznie odwracana
bez gold. Remisy zachowują source/geometric default. Nie blendujemy score MLM
z engineScore; historyczny wielokluczowy replay pozostaje wyłącznie eksperymentem.

PyTorch CPU2.8.0, transformers4.57.6, numpy2.2.6, sentencepiece0.2.1,
sacremoses0.1.1, float32, threads2/1, eval/inference_mode. Oba modele na osobnych
runnerach; porównania host timing/RSS nie są izolowanym identycznym sprzętem.
Raport prepare/inference/total p50/p95 per populacja/zadanie/okno, faktyczne
parametry i szczyt RSS całego procesu. Zawiera download/load/runtime, nie RAM
samego modelu. Pełny pip freeze, faktyczne pliki wag/tokenizera i SHA256.
Brak Androida, energii i gwarancji RAM z liczby parametrów.

## Ocena i screening następnej próby

Collector musi mieć oba kompletne modele, zgodny commit/freeze/request payload,
384 wyników każdy, finite scores dokładnie dozwolonych wariantów. Przelicza
raport z raw predictions; nie ufa gotowemu report.json ani samemu summary.
Nowe naturalne, dystans, przecinki i stare regresje raportowane oddzielnie.
Top1, zwykłe małe litery/nazwy, comma/noComma, baseline, paired repairs/regressions;
pełne rankingi i różnice 16/32 i Distil/HerBERT. Top3 par nasycone konstrukcją,
nie dowód poprawy SI. Kontrole bez gold nie wliczane do accuracy; missing_key
nie może zostać „naprawiony” dodaniem formy spoza slatu.

Exploratory screening do mobilnej próby case-only, nie wdrożenia: new_natural/32
Distil top1 >= HerBERT top1 minus1 oraz regresje wobec defaultu <=HerBERT plus1.
Raport ma sprawdzić to jawnie; brak przejścia nie oznacza sukcesu „bo jest mniejszy”.
To mała diagnostyka, nie statystycznie potwierdzona noninferiority.
16 może zostać kandydatem dopiero przy new_natural16 >=32 minus1 i co najwyżej
jednej dodatkowej regresji zwykłej małej litery; straty dystansu pokazać jawnie.
Interpunkcja osobna: bez automatycznego wstawiania nawet przy lepszym wyniku.
Budżety Android pamięci/latencji i niezależne rzeczywiste konteksty przed integracją.

## Zamrożenie i wykonanie

freeze-manifest.json wiąże MODELS/revisions, kanoniczny requests SHA i wszystkie
skrypty/protokół/NOTICE/deps/dane, odziedziczony source contract i workflow.
Kod i manifest atomowo commitowane PRZED inferencją; obowiązkowy freeze check
w contract i runnerze/collectorze. Canonical digest obiektu manifestu w wynikach.
Każda naprawa wykonania wymaga nowego jawnego commita i refreeze; zmiana metody/
danych po wynikach jest nową próbą, nie skrytym naprawieniem kontraktu.

Brak merge/release/tag/version bump, zmian langpacka/APK/live SI. INT8 HerBERT
pozostaje FAIL. Nie uruchamiamy modelu w zwykłych podpowiedziach. Monitorowanie
Actions <=60 sekund TOTAL/run; po tym użytkownik zgłasza zakończenie.
