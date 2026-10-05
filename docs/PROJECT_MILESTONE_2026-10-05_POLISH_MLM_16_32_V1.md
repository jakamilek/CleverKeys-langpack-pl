# Kamień milowy: zamrożone porównanie polskich MLM, 16/32 słowa
Data: 2026-10-05. Status: lokalny kontrakt PASS; prawdziwe modele i collector w CI.

## 1. Autoryzacja i zakres
Użytkownik zatwierdził porównanie po przeglądzie RAM HerBERTa. Osobny producer
experiment/polish-mlm-16-32-v1, kod 769fc46579e910f50ff40f5546f0d5ae5643de5b,
parent ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3. Bez modyfikacji starego eksperymentu.
Runtime dokumentacja 21431ce3d0181db4f0c1c6e3140d925fb02a1391; aplikacja niezmieniona.

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
Walidacja przed oceną, sha faktycznych plików/config/tokenizera/wag i środowisko zachowane.

## 4. Dane i populacje
192 przypadki/384 zapytania na model, 768 wyników razem: v5 regression104,
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

## 8. Weryfikacja i CI
11 lokalnych testów stdlib PASS: populacje/generator, label leakage/source forms,
word boundaries/distance, missing/duplicate/invalid outputs, identities/nonfinite,
quantiles/offsets, separate evaluation, freeze tamper i complete collector/screening.
13 uploadowanych blob SHA i3 odziedziczone źródłowe SHA potwierdzone.
Run https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37355290211
w ostatnim odczycie in_progress. To nie jest jeszcze PASS jakości/model load.

## 9. Raport i screening
Collector wymaga obu kompletnych modeli, obecnego commita, freeze/request i finite
scores. Przelicza raw predictions. Top1, lower/proper, comma/noComma, repairs/regressions,
paired16/32 i Distil/HerBERT; żadnego poolowania populacji ani przewagi z nasyconego top3.
Exploratory mobile case-only screen: new_natural32 top1>=HerBERT-1 i baseline
regressions<=HerBERT+1. 16 kandidat: natural16>=32-1 i lower regressions<=32+1.
Małe diagnostyczne kryteria, bez statystycznej noninferiority i automatycznej produkcji.

## 10. Następny krok i dokumenty
Po zakończeniu runu użytkownik zgłasza status. Zweryfikować obie głowice, kompletny
collector, rankingi/screening i artefakty. Dopiero obiecujący model: mobile export/parity,
oddzielna kwantyzacja i pomiar telefonu. Żaden model nie jest teraz włączony w IME.
Producer experiments/polish_mlm_compare_v1/PROTOCOL.md; runtime canonical spec/todo/TOC
uaktualnione. Ten checkpoint identyczny na obu main, dokładny readback wymagany.

## 11. Decyzje utrzymane
Geometric i aplikacja bez zmian, domyślnie32/max64 do dowodów16/32, SI off.
HerBERT referencja, failedINT8 pozostajeFAIL. Brak merge/release/tag/version bump.
Oba main tylko dokumentacja, brak nowego APK. Actions monitoring <=60 s TOTAL/run,
bez czekania na zakończenie; trzy czasyBS nadal backlog. Case/parity nie zastępują
niezależnej jakości, privacy/editor/session gating ani energii telefonu.
