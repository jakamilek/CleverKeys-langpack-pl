# Kamień milowy: screening źródłowych form i porównanie mniejszych MLM v2
Data: 2026-10-05 (Europe/Warsaw). Status: coverage/tokenizer PASS dla par; modele v2 w CI.

## 1. Zweryfikowane repozytoria i zakres
Main przed tym dokumentem: CleverKeysPL b4fd4b549f6b3e0e3f10b80f31e0497ad66bc848;
CleverKeys-langpack-pl 7b305410d110ebd9a38e9f52cfbbb84e83ccb965. Odczyt branches z GitHub.
Ten dokument dopisuje wyłącznie checkpoint na obu main, bez promocji kodu.
Producer experiment/polish-mlm-16-32-v2 HEAD56b7d0f213fcdda1a8a5c245555bd3307fcc2133,
parent9162d9a9f2ac3b94f4212a773cf9be80e1cb632a. Runtime trial/herbert-fp32-benchmark-v1
docs-only HEAD18f252d7bf211bddf9eaebecea2eb17a07c14cea, parent74bbc601...
User autoryzował szukanie kolejnego lekkiego modelu po zakończonym v1.

## 2. Architektura utrzymana
Geometric pozostaje dekoderem; source pair expansion i jedna ścieżka prezentacji/commit.
Jeden klucz ma źródłowo poświadczone powierzchnie/atrybuty/default; nie dublujemy słownika
i nie dopisujemy ręcznych opisów znaczenia. SI nadal off, brak live editor dispatcher.
Default32/max64/4096UTF16 przyszłego kontekstu z pola zachowującego case/interpunkcję;
nie stara2-word lowercase history. Brak nowego APK/ustawienia/tokenizera Androida.

## 3. Zaakceptowane nowe ustalenia
Przed dużymi wagami sprawdzić ORYGINALNY tokenizer, źródłowe formy/case/Unicode/head metadata.
Pełny authenticated v5 pack:106363 CKDT klucze,16199 sidecar entries,16117 wielowariantowe,
122480 unikalnych form. Bez nieznanych/collapsed source pairs u3 screened modeli.
distilHerBERT zero unknown całego zbioru. Geotrend tylko standaloneą/ę unknown:
fullSourceCoveragePass=false, nie maskować tej luki. Wszystkie384requests/836targetspans PASS.
Dwa sześciowarstwowe modele wybrane do diagnostycznego v2; to nie akceptacja produkcyjna.

## 4. Odrzucone i rezerwowe rozwiązania
sdadas/polish-distilroberta v1 rev849b664fa3134beae84095d28a184c145c6a3aa5 nadal odrzucony:
Ł w Łódź/Łotysz ID3,26spans22requests; żadnego wykluczania przypadków/osłabienia bramki.
Geotrend BERT12 rev5c87e45fdc3ce85e1dc718daddc39c9e3d3dbf40,103266173F32 +512I64buffer:
rezerwa, większy niż jego Distil; wagi nie wczytane. ORIS Small C karta25.41M/research gated/
custom_code; API401 bez dostępu, nie pobrano config/tokenizera/wag i nie zaakceptowano warunków.
HerBERT FP32 referencja, INT8 wcześniejszyFAIL niezmienny. Mapped-vs-path pamięć rezerwa.
Nie wyprowadzamy rozmiaru PSS telefonu z parametrów/kart/GPU danych.

## 5. Wdrożone przygotowanie, niewdrożone dalej
W producer19nowych plików: pełny reproducible screening/report/header metadata,
v2contract/runner/projection/collector/tests/freeze/protocol/workflow. V1 code/data/results
niezmienne; mlm.py byte-identical. DistilBERT adapter udostępnia oryginalny trained chain
transform→activation→layernorm→projector, deleguje full forward; bez nowych weights/head.
Tokenizer backend hash i wszystkie384input sprawdzane BEFORE weights; strict loading_info
bez missing/mismatch/error/unexpected,3parity probes allclose1e-4/1e-5. FP32CPU2/1.
Nie wdrożono eksportu/kwantyzacji/Android tokenizer/integracji/predykcji interpunkcji/nowych opcjiBS.

## 6. Zweryfikowane i niezweryfikowane
Coverage wykonane actual Transformers4.57.6/tokenizers0.22.2 bez Torch na pinnedassets;
źródłowy pack/dictionary/sidecar SHA sprawdzone. Geotrend header odczytboundedRange:
12688B Distil/23888B BERTJSON+8B length, nie pełne wagi. Model head loading/parity pending.
Geotrend pojedynczeąęńĄĘŃ teżunknown, pełne źródłowe pary poprawne; nie universalUnicode.
8nowych lokalnych puregate tests PASS; 7PythonAST PASS; 19uploadedGitblobSHA potwierdzone.
Contract-only PR run37359531859 SUCCESS (actual contract step; inference/comparison skipped),
workflow obejmuje11v1+8v2 tests. Push run37359525824 w ostatnim odczycie in_progress.
Native original-head/full weight checks, quality/results i faktyczneparams distilHerBERT pending.
Żaden wynik syntetycznych unit fixtures nie zaliczany do trafności modelu.

## 7. Istotne gałęzie historyczne
experiment/polish-mlm-16-32-v1 HEAD9162d9...: frozen769fc465... i zakończony run37355290211FAILURE,
HerBERT384PASS i odrzucony DistilRoBERTa, archiwizacja/przeliczenie referencji.
experiment/herbert-fp32-benchmark-v1 ebbe16b...: starsze v5 i metadata experiments.
trial/herbert-fp32-benchmark-v1: accepted phase-v2 AndroidAPK db88fd28..., późniejsze tylko docs.
Main kod niezmieniony tym etapem. DraftPR9 baza v1, head v2; brak merge.
DraftPR8 archiwizuje v1 wynik, nie wdrożenie odrzuconego modelu.

## 8. Źródła, artefakty, SHA i integracja
Geotrend/distilbert-base-pl-cased rev9002d311e35aac14575bf53ad4fa3d8f8b853c2b,
Apache2.0 wg karty,6layers/768/vocab22397,API60737405F32params.
BartekK/distilHerBERT-base-cased rev7276461b7a8fd668aaf30313c03a68bd11aad642,
6/768/vocab50000,originalHerbertTokenizerFast; brak deklaracji licencji wag,
nie zakładamy dziedziczenia CC-BY nauczyciela. Brak redystrybucji/deployment approval.
Pack SHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecar5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d,
dictionarya32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a.
Nowy label-free request SHA3cd36f0b230e1b5abb70df44dc1bd992828e48495c1c3cb17bf3f23bf07a7da2.
Freeze wiąże nowe executables/screen/results i immutable v1/v5/historyczne reference.
Integracja eventual w SuggestionHandler/SwipeSurfaceVariants przed publikacją, nie wdrożona.

## 9. Ograniczenia eksperymentu
192cases/384queries na model, te same już znane authored v1 teksty/gold/source, tylko nowyprotocolID.
Osobne104old/32natural/32distance/24punctuation. Nie externalblindholdout.
Natural6–14words:16/32 IDENTYCZNE, bez decyzji o skróceniu realnego kontekstu.
Sztuczny dystans23–25words i przecinek przed znanym słowem raportowane osobno.
Top3 par nasycone z definicji, nie dowód jakościAI. Frozen exploratory screen case-only:
natural32>=HerBERT-1 i baseline regressions<=HerBERT+1; przy referencji24/32 i2 to>=23/<=3.
Collector wymaga obu kompletnych currentcommitów + jawny historyczny Herbertcommit
769fc465...; oryginalna reference recomputation identyczna. Stare czasy/RSS nie pairedperformance.
Weights/phone energy/PSS/export/legal availability niezależne od takiego screeningu.

## 10. Następny uzasadniony krok
Użytkownik zgłasza zakończenie https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37359525824.
Odczytać pełne tokenizer/head/parity, kompletnycollector/raw predictions, wszystkie naprawy/regresje.
Nie zmieniać metody po zobaczeniu wyników; FAIL utrwalać z diagnozą.
Obiecujący legalny model dopiero: niezależne konteksty, export/parity i actualphone RAM/p50/p95/energia.
Exact tokenizer/projection/custom-license concerns nie omijać. HerBERT remains reference, no forced choice.
Actions monitoring<=60s TOTAL/run, brak czekania/watch/sleep. SIdefault off32/max64 zachowane.

## 11. Różnica wobec poprzedniego checkpointu i dokumenty
Poprzedni docs/PROJECT_MILESTONE_2026-10-05_POLISH_MLM_16_32_V1.md: odrzucenie DistilRoBERTa.
Teraz rzeczywiste full-source cheap preflight3nowych kandydatów,2wybrane do frozen v2,
jawne Geotrend coverage wyjątki i licencja distilHerBERT, pierwszy contractCI PASS.
Producer experiments/polish_mlm_screen_v2/README.md/results i polish_mlm_compare_v2/PROTOCOL.md;
runtime canonical docs/specs/polish-context-ai.md,memory/todo.md,TOC exactreadback potwierdzone.
Ten dokument identyczny na obu main, docs-only; exactreadback po zapisie wymagany.
Bez merge/tag/release/version bump/modelAPK/subagentów; inheritedGemini/PAL waived.
Polski UI priorytet, inne języki backlog; trzy stationaryBS timing settings nadalbacklog.
