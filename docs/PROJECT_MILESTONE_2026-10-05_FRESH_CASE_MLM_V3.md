# Kamień milowy: świeże konteksty kapitalizacji i porównanie MLM v3
Data: 2026-10-05 (Europe/Warsaw). Stan: próba zamrożona i uruchomiona; jakość v3 nieznana.

## 1. Zweryfikowane repozytoria i zakres
Main przed dokumentem: CleverKeysPL a0f457ffcfce4683790e6d4a163c35b1cafb8bc5;
CleverKeys-langpack-pl 8380d6534e98f79325149f466428004dae60bd60.
Odczytane przez GitHub API 2026-10-05. Ten zapis jest docs-only na obu main.
Producer experiment/polish-mlm-fresh-v3 kod c1e9d3a7895f2a380bc75772985c88a53db32a4b,
parent a729fd780241a581f9cac153c0a6d926d8bfa1c1; draft PR10 baza v2.
Runtime trial/herbert-fp32-benchmark-v1 docs-only 0367b334f770d4ad2b1925dc445850e9c19e9b78,
parent16eb460f16ca588272e8ff37d68a4940fef1c0c5. Bez promocji eksperymentu do main.
Użytkownik: „ok, działaj. na razie nie przejmujmy się licencją”.

## 2. Utrzymana architektura
Geometric pozostaje dekoderem. Jeden klucz ma źródłowe powierzchnie/default/atrybuty;
brak duplikatów słownika i ręcznych opisów znaczeń. Metadane określają dozwolone formy,
nie są nowym promptem modelu. Obie formy pozostają do wyboru.
Live SI off; przyszły dispatcher pola/identity/privacy/stale fallback nadal niewdrożony.
Default32/max64/4096UTF16 zachowany, kontekst przyszłości z pola z case/interpunkcją.
Ręczny wybór, Shift, caps i sentence capitalization mają priorytet.

## 3. Zaakceptowane ustalenia
Sprawdzanie licencji ODŁOŻONE na wyraźną prośbę użytkownika. Kontynuujemy techniczne
porównanie; ta zgoda nie jest deklaracją licencji ani praw redystrybucji wag.
64 świeże autorskie przypadki, 8 znanych/8 nowych kluczy, short4–6/long21–26 słów,
po małej/wielkiej formie; cztery osobne populacje po16 przypadków, osiem gold lower/upper.
64 historyczne forms v5 zachowane dokładnie, włącznie z wszystkimi znanymi regresjami.
128cases/256requests na model. Oba oryginalne pinned HerBERT/distilHerBERT rerun,
bez historycznego zastępowania reference scores. 32 różne pary wejść16/32 w nowych długich tekstach.
Nowe klucze koza/wrona/sikora/kula/mucha/wierzba/orzeł/ryś nie były forms gold v1/v2.

## 4. Odrzucone i rezerwowe rozwiązania
V2: Geotrend Distil jakościowy screen FAIL21/32, HerBERT24/32, distilHerBERT25/32.
Starsze forms50/64 vs40/64 vs46/64; nowa interpunkcja20/24 vs11/24 vs16/24.
DistilHerBERT wynik mieszany, nie wybór produkcyjny; starsze regresje nie ukryte.
DistilRoBERTa v1 odrzucona przez unknown Ł; żadnych wyjątków/dataset/gate zmian.
Geotrend BERT12/ORIS rezerwa; ORIS gated/custom/API401 bez pobrania/akceptacji warunków.
HerBERT FP32 referencja. Wcześniejszy INT8 FAIL niezmieniony. CTC poza tym zakresem.

## 5. Wdrożone przygotowanie i niewdrożone
16 nowych plików producer: authored build_cases/cases/source-snapshot, protocol/NOTICE,
contract/runner/collector/freeze/manifest/tests, niezmieniony mlm.py/projection/deps,
lokalny tokenizer preflight i workflow. Każdy uploaded Git blob SHA zweryfikowany.
Wpisy nowych kluczy są dokładnymi kopiami z fullv5; brak nowych źródłowych opisów.
Runtime spec/todo/TOC zaktualizowane i dokładnie odczytane. Licencja review deferred w backlogu.
Nie wdrożono ONNX/Android tokenizera/fixtures/model bundle/APK/liveSI/interpunkcji.
Trzy czasy stacjonarnego Backspace nadal backlog.

## 6. Zweryfikowane i niezweryfikowane
27 lokalnych pure contract tests PASS:11v1+8v2+8v3;8AST PASS.
Oryginalny distil tokenizer Transformers4.57.6/tokenizers0.22.2:256requests/512spans PASS,
wszystkie wybrane source pairs rozróżnialne, max39inputtokens. Wagi lokalnie niewczytane.
Backend SHA94193cdc17926964a0946b7b2c3a2bb80f48080c7c2620b5499475dcc65c2dc1.
Requests SHAa20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d.
Push run 37363474711 w ostatnim dozwolonym odczycie queued, kod c1e9d3a7895f2a380bc75772985c88a53db32a4b.
PR contract-only run37363478784 queued przy odczycie. NIE deklarować CI PASS z testów lokalnych.
Pełne strict native load/head/parity/quality/collector v3 pending; żadna jakość syntetycznych testów.
Odczyt obu canonical docs/main checkpoints dokładny wymagany po zapisie.

## 7. Gałęzie i historia
Nowa branch experiment/polish-mlm-fresh-v3 c1e9d3a7895f2a380bc75772985c88a53db32a4b; draft PR10, bez merge.
V2 experiment/polish-mlm-16-32-v2 a729fd780241a581f9cac153c0a6d926d8bfa1c1:
zamrożony56b7d0..., run37359525824SUCCESS, techniczne PASS, mixed quality, raw archiwum.
V1 experiment/polish-mlm-16-32-v1 9162d9...:769fc465... frozen,
run37355290211FAILURE, unknown DistilRoBERTa, HerBERT384PASS i historyczna referencja.
Runtime trial/herbert-fp32-benchmark-v1 0367b334f770d4ad2b1925dc445850e9c19e9b78: jedynie docs względem poprzedniego.
Zaakceptowany APK code db88fd28cca21ba2aa1e99b38e3886f1f147b5d6 niezmieniony.
DraftPR8 historia v1, PR9 v2, PR10 v3. Brak release/tag/version bump.

## 8. Źródła, SHA i przyszły punkt integracji
HerBERT allegro rev50e33e0567be0c0b313832314c586e3df0dc2297,12layers,124494416params.
distilHerBERT BartekK rev7276461b7a8fd668aaf30313c03a68bd11aad642,6layers,81967184params.
Publiczna deklaracja licencji wag nieznaleziona, review deferred, nie dziedziczy automatycznie nauczyciela.
V5pack SHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb,
sidecarSHA5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d,
106363keys/122480surface/16117multivariant. Źródła nazw i leksyki w pack NOTICE.
V3manifest wiąże nowe pliki i wszystkie niezmienione zależności v1/v2/źródłowe/source screen.
Workflow polish-mlm-fresh-v3.yml; artifacts nazwy polish-mlm-fresh-v3-16-32-*,
tylko outputs/environment, żadnych wag. Przyszła integracja w SuggestionHandler/
SwipeSurfaceVariants przed publikacją, nie retroaktywne przepisywanie tekstu.

## 9. Ograniczenia i bramki
Świeże teksty autorskie przygotowane po analizie v2; gold asystenta, brak niezależnego
anotatora/humanblind lub external benchmark. Nie nazywać tego niezależną trafnością produkcyjną.
Długie21–26słów bez sztucznego filleru; 16ucina początek,32całość; bez prywatnych rozmów/>32słów.
Top3 par nasycone bez SI, tylko top1 rozróżnia diagnostic ordering. Bez interpunkcji/multi-key.
Frozen exploratory per-fresh-stratum32 top1>=bieżącyHerBERT-1, baseline regressions<=HerBERT+1;
oddzielna historyczna64forms gate top1>=HerBERT-1. Stary46vs50 sugeruje możliwyFAIL:
nie luzować bramki po wyniku, technicalSUCCESS może mieć qualityFAIL.
Oryginalny v1 WWM/fullvocabmeanlogp niezmieniony; strict weights info, pinned config,
trzy originalforward parity (krótki/długi/Unicode), allclose1e-4/1e-5 i maxabs<=.001.
Collector obie pełne currentcommit tożsamości, preflight przed wagami, hashedweights,
finite alignedtoken traces, report dokładnieprzeliczony, wszystkiepairedregressions.
HostjobRSS nie jest AndroidPSS/energią. Telefon HerBERT:baseline346.2/load2121.0/max2132.1/
close1336.8MiB; mniej słów nie usuwa fixedload kosztu. 34%mniej params nie gwarantuje telefonRAM.

## 10. Następny uzasadniony krok
Użytkownik zgłasza zakończenie https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37363474711.
Odczytać pełne nativechecks, pobraćsprawdzić artefakty, dokładnieprzeliczyć collector,
ocenić wszystkie freshstrata/historycznefailures i16/32oddzielnie. Nie zmieniać metody po wyniku.
Dopiero uzasadniony dalszy export/parity/nativefixtures i pomiar load/PSS/latency na Nubii.
Sprawdzanie licencji odłożone teraz; brak kontaktu z autorami. Brak produkcyjnego zatwierdzenia.
Actionsmonitoring <=60s TOTAL/run; zakończone, bez watch/sleep do końca i dalszego sprawdzania.
Nie zmieniaćdefault32/liveSI/interpunkcji/INT8FAIL w tym etapie.

## 11. Różnica i dokumenty
Poprzedni docs/PROJECT_MILESTONE_2026-10-05_SMALLER_MLM_V2_RESULTS.md archiwizował v2.
Teraz zamrożone świeże naturalne teksty i nowe klucze z poświadczonych source entries,
rzeczywiste różne16/32 wejścia, bieżący HerBERT reference rerun i zachowane64regressions.
Licencja odłożona decyzją użytkownika, testy lokalne/preflightPASS, CI rozpoczęte bez oczekiwania.
Protocol: https://github.com/jakamilek/CleverKeys-langpack-pl/blob/c1e9d3a7895f2a380bc75772985c88a53db32a4b/experiments/polish_mlm_fresh_v3/PROTOCOL.md
Runtime docs/specs/polish-context-ai.md,memory/todo.md,docs/TABLE_OF_CONTENTS.md exactreadback.
Ten dokument identyczny na obu main, tylko docs. PolskiUIpriorytet, inne języki backlog.
Bez subagentów; inheritedGemini/PAL wymóg nadal uchylony.
