# Kamień milowy: zamrożone porównanie polskich MLM, 16/32 słowa
Data: 2026-10-05. Status: run37355290211 FAILURE; HerBERT384/384 PASS, DistilRoBERTa tokenizer FAIL.

## 1. Autoryzacja i zakres
Użytkownik zatwierdził porównanie po przeglądzie RAM HerBERTa. Osobny producer
experiment/polish-mlm-16-32-v1, kod 769fc46579e910f50ff40f5546f0d5ae5643de5b,
parent ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3. Bez modyfikacji starego eksperymentu.
Wyniki producer 9162d9a9f2ac3b94f4212a773cf9be80e1cb632a; runtime dokumentacja
74bbc601aa35a9987b20d474b0a0d4d2c5652ed7; aplikacja niezmieniona.

## 2. Rewizje modeli
HerBERT allegro/herbert-base-cased 50e33e0567be0c0b313832314c586e3df0dc2297,
CC BY 4.0, 12 warstw. sdadas/polish-distilroberta
849b664fa3134beae84095d28a184c145c6a3aa5, Apache-2.0, 6 warstw, 768 hidden,
vocab50001. Rewizja z API i config/tokenizer pobrane przed inferencją.
Oryginalny Distil tokenizer: Unigram/NFKC/WhitespaceSplit/Metaspace/RobertaProcessing.

## 3. Pełna głowica i bezpieczeństwo jakości
AutoModelForMaskedLM, trust_remote_code=False, wymagane loading_info bez brakujących/
niedopasowanych/error/niewyjaśnionych wag. Tylko cztery historyczne pooler/SSO nieużywane
w HerBERcie dozwolone. Case variants muszą mieć różne token IDs; unknown target/budget
zatrzymuje próbę. Projection allclose z pełnym pretrained forward atol1e-4/rtol1e-5.
HerBERT wszystkie kontrole PASS. Distil load/arch/case checks PASS, ale unknown target
zatrzymał walidację przed projection/parity i oceną jakości. Brak complete validation/predictions.

## 4. Dane i populacje
192 przypadki/384 zapytania zaplanowane na model, tylko384 wyników HerBERT: v5 regression104,
new_natural32, new_distance_control32, new_punctuation24. Dwa okna16/32.
Nowe naturalne: po małej/wielkiej formie dla16 znanych kluczy; nie ślepy zewnętrzny
benchmark. Dystans kontrolowany: cue usunięte przy16, zachowane przy32, wspólny
neutralny łącznik i osobna populacja. Przecinek/brak znaku24 po12, przed znanym słowem.

## 5. Źródła i wejście
Source snapshot/contract/cases v5 odziedziczone byte-identical, blobSHA potwierdzone.
Formy jednego wpisu i rzeczywiste atrybuty/defaulty, bez ręcznych opisów słownika.
Requests tylko id/caseId/window/context/candidates. Żadne gold/population/contextType
nie trafiają do modelu. Dokładny suffix zachowuje case/punctuation, <=4096 znaków,
<=512 tokens, bez dodatkowego skracania trudnych przypadków.

## 6. Scoring i pomiary
Oba MLM: offsets całego kontekstu+wariantu, wszystkie target subwordy maskowane,
oryginalny pełny vocabulary logsoftmax, średnia logp, suma/IDs/positions w trace.
Batch kandydatur; projekcja tylko celów. Okna pierwsze naprzemienne, trzy warmupy,
stable source default ties. Historyczny replay bez kalibracji geometric, nie wdrożenie.
CPU torch2.8.0/transformers4.57.6 float32 threads2/1, osobne runnery. Host RSS/times
per populacja/okno, faktyczne parametry; brak telefonu/energii/kwantyzacji.

## 7. Zamrożenie
freeze-manifest wiąże 12 nowych plików wykonania/danych/dokumentacji i 3 odziedziczone
source contract/cases/snapshot (sam manifest nie hashuje siebie), workflow i revisions. Wyniki wiążą canonical manifest.
Request SHA a859aac5acf8dc950c07df415873aced44a46f9a4585818504e3f2af6377449b.
Protokół/kod/dane atomowo zapisane przed inferencją. Naprawy jawne/refreeze;
zmiana metod lub etykiet po wyniku to nowa próba. Bez weights w Git/artifact/APK.

## 8. Weryfikacja i zakończone CI
11 testów lokalnych i contract CI PASS; oryginalny HerBERT384/384 PASS.
Run https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37355290211
FAILURE: DistilRoBERTa unknown target token; collector prawidłowo odmówił brakującego
wyniku. Tokenizer tej rewizji nie rozpoznaje Ł w Łódź/Łotysz, ID3;26 fragmentów
w22/384 requests. Oryginalny tokenizer.json SHA256
108af881c403092a16ee515c2ad4a9a72122a3846cfd5c9f2bb860a3fd2bdafa.
Powtórzona diagnoza tokenizers0.22.2 i frozen target_positions, bez Torch/inferencji.
Pojedyncze ĄĆĘŃÓŹŻ również ID3;Ś rozpoznane, nie wyczerpujący test wszystkich słów.
Odrzucono model dla tego zadania/revision, nie Android/ONNX. Bez osłabienia bramki,
wykluczenia Łodzi, podmiany tokenizera czy ręcznych niewytrenowanych tokenów.

## 9. Ukończone wyniki i granice 16/32
HerBERT raw predictions/report/validation/environment archiwizowane w producer
experiments/polish_mlm_compare_v1_results/herbert. ZIP11364382538 SHA256
8ec495775b30b8552cf39da70c0f62eccabac3b90d092e0cf906ee1fe7cb0f02 potwierdzone;
pełny raport przeliczony identycznie, request/freeze/commit sprawdzone.
Nowe naturalne top1 24/32 (małe14/16,wielkie10/16),10napraw i2regresje defaultu.
Konteksty6–14 słów: oba okna identyczne, nie dowód bezstratnego odcięcia dłuższego tekstu.
Tylko sztuczny dystans23–25 słów: top1 16/32 przy16 i18/32 przy32;
8zmian,5napraw i3regresje32. Nowe przecinek/brak20/24,3regresje, bez automatycznej aktywacji.
Host RSS1426.48MiB i czasy nie są PSS/energią/latencją telefonu; brak porównania Distil.
Collector screening nieobliczony, bo wymaga dwóch kompletnych modeli. Top3 pary nasycone
z konstrukcji również bezSI; nie świadczy o jej trafności. Nie ślepy zewnętrzny benchmark.

## 10. Następny krok i dokumenty
Przed ładowaniem kolejnego mniejszego modelu: tani test oryginalnego tokenizera na
źródłowych formach/case i polskim Unicode. Potem wytrenowana oryginalna głowica,
nowy zamrożony protokół jakości, eksport/parity i pomiar telefonu. Kolejny model
nie został wybrany/wczytany; nie obiecywać oszczędnościRAM z samych parametrów.
Producer RESULTS.md i diagnose_tokenizer.py, canonical runtime spec/todo/TOC zaktualizowane.
Draft PR8 zawiera kod próby i jej faktyczny wynik, nie propozycję wdrożenia modelu.
Ten11-sekcyjny checkpoint identyczny na obu main; dokładny readback wymagany.

## 11. Decyzje utrzymane
Geometric i aplikacja bez zmian, domyślnie32/max64 do dowodów16/32, SI off.
HerBERT referencja, failedINT8 pozostajeFAIL. Brak merge/release/tag/version bump.
Oba main tylko dokumentacja, brak nowego APK. Actions monitoring <=60 s TOTAL/run,
bez czekania na zakończenie; trzy czasyBS nadal backlog. Case/parity nie zastępują
niezależnej jakości, privacy/editor/session gating ani energii telefonu.
