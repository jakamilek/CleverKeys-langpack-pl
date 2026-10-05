# Kamień milowy: przegląd mniejszych alternatyw polskiej SI
Data: 2026-10-05. Status: przegląd źródeł; kandydat do nowej próby, bez inferencji.

## 1. Zakres i motywacja
Użytkownik kwestionuje dalsze skupienie na HerBERcie z powodu dużego PSS telefonu;
wcześniej zaproponował kontekst 16 słów. Przegląd nie jest wyborem produkcyjnym.
Runtime trial/herbert-fp32-benchmark-v1, dokumentacja 35278adb3904d42ab16ba81e2cf5bb6bac8d6809.
Model/producer code d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c pozostają niezmienione.

## 2. Zachowane dowody telefonu
HerBERT phase-v2 db88fd28, CI 37348519387 PASS i natywna próba Nubii PASS.
Baseline 346,2 MiB → loaded 2121,0 → workload max 2132,1 → closed 1336,8.
Główny koszt już przed inferencją; PSS całego procesu nie rozdziela źródeł ani leak.
Raport: docs/eval/2026-10-05-herbert-fp32-nubia-phase-v2.md.

## 3. Nowa shortlista
Pierwszy nowy kandydat: sdadas/polish-distilroberta, autor deklaruje około 82M
parametrów, sześć warstw, polski MLM, Apache-2.0; istniejące wagi, bez budowy od zera.
Źródła: https://huggingface.co/sdadas/polish-distilroberta
https://github.com/sdadas/polish-roberta

## 4. Granice potwierdzenia
Nie pobrano modelu/wag, nie zamrożono rewizji, nie sprawdzono pełnego pretrained
head/tokenizera ani case preservation w ładowaniu. README karty pusty; odczyt
config/tokenizer WWW niedostępny. Parametry/warstwy nie prognozują dokładnego RAM.
Brak wyniku jakości, ONNX, telefonu i interpunkcji tego kandydata.

## 5. Wcześniejsze modele
Zamrożone ai_compare_v5: HerBERT plain 50/64 form top1, MiniLM NLI 28/64,
Qwen3-0.6B 36/64. Przecinek 15/20, 12/20, 8/20. Są to modele+adaptery i znane klucze,
autorskie dane; top 3 nasycone parą form. Wyniki nie dowodzą jakości całych rodzin.
DistilmBERT 134M nie jest automatycznie mniejszy od faktycznego HerBERT 124M.
Nie powtarzamy tej samej próby MiniLM/Qwen jako nowego dowodu.

## 6. Inne rozważone ścieżki
Przycięty polski Qwen3 ma niezgodne z naszą identyfikacją liczby bazowe w karcie;
brak weryfikacji poprawności i RAM. Embeddingi wymagają uczonego rankera/head,
nie są gotowym MLM zamiennikiem. Qwen3.5 pozostaje wcześniejszym kandydatem,
niezweryfikowanym w tym przeglądzie. Nie obiecujemy gotowej małej SI na podstawie nazwy.

## 7. Metadane i rozszerzalność
Źródłowe warianty jednego wpisu, atrybuty/defaulty pozostają. Bez ręcznych opisów
miasta/owocu i bez punktowych wyjątków. Nowy MLM można badać na tych samych
wariantach pisowni, interpunkcję osobno. Brak dowodu gotowej głowicy interpunkcji
lub korzystania z metadanych bez treningu. Geometric pozostaje dekoderem.

## 8. Nowa kolejność pracy
Najpierw potwierdzić pełny model/tokenizer/revision DistilRoBERTa i zamrozić protokół
16/32 słowa, HerBERT referencja, te same formy i oddzielne niewidziane konteksty.
Znane dane tylko regresje, nowe etykiety przed inferencją, bez zmian metod perword.
Porównanie mapped/path HerBERTa pozostaje rezerwowym eksperymentem.

## 9. Bramki mobilne
Po obiecującej jakości: ONNX FP32 parity, osobna kwantyzacja i pełne oryginalne
bramki nowego modelu, następnie PSS/timing/energia na telefonie w osobnych procesach.
Ustalić budżety przed wynikami. INT8 HerBERT nadal FAIL; nie rozluźniać jego bramki
ani traktować go jako porażki kwantyzacji wszystkich modeli.

## 10. Dokumenty i weryfikacja
Przegląd: docs/eval/2026-10-05-polish-ai-alternatives.md.
Spec i todo odzwierciedlają plan, TOC wskazuje przegląd. Dokładny readback dokumentów
i tego identycznego checkpointu na obu main wymagany. Bez nowego CI/APK w tym etapie.
Dotychczasowe wyniki/kontrakty/model trust niezmienione.

## 11. Decyzje utrzymane
HerBERT pozostaje działającą referencją; nie inwestujemy automatycznie w jego
integrację jako jedyny wybór. Kandydat DistilRoBERTa wymaga próby i może nie wystarczyć.
Domyślnie 32 słowa do dowodów 16/32; live SI off, bez merge/release/tag/version bump.
Oba main wyłącznie dokumentacja. Monitoring Actions <=60 sekund TOTAL/build.
Opcje czasów Backspace i niezależna jakość pozostają backlogiem.
