# HerBERT V4 — odmiana, następnie kapitalizacja; pomiar rozpoczęty

## 1. Stan i identyfikacja
2026-10-10 UTC. Main przed checkpointem: CleverKeysPL2f22ca399805e5cb06105fa8fce7cd53d85f7a41; CleverKeys-langpack-plabdb305d2bd24a2549276c80c2532a081a83361e. Ten checkpoint dodaje wyłącznie ten dokument do obu main; starsze checkpointy zachowane, kod runtime bez zmian. Użytkownik autoryzował kontynuację diagnostyki. Brak merge/release/tag/version bump.

## 2. Architektura i bieżąca aplikacja
Geometric ocenia geometrię gestu i dostarcza kandydatów. Oryginalny HerBERT FP32 opt-in obecnie ocenia mean log probability; compact-case-v4 zachowuje alternatywy.
Runtime trial/herbert-live-v1 nadal3f48e456f0d8f411e80be3857f1846e4b2cd139e, draft PR4. Deadline350ms, default32 słów (16/32/64), tożsamość request/editor/settings, prywatność i słownik niezmienione. V4 to host diagnostic, nie wdrożony dwustopniowy scorer.

## 3. Przyjęte ustalenia
Hipoteza V4: SI najpierw ocenia zgodność formy gramatycznej w kontekście, potem kapitalizację wybranej formy. Geometrii nie ocenia ten model.
Nie generować rdzeni/odmian/opisów ręcznie ani duplikować kluczy słownika. Wszystkie już dostarczone warianty pozostają dostępne. Przyjęto tylko wykonanie diagnostyki, nie jej jakość.
Dwie ostatnie obserwowane jednostki leksykalne są identycznymi maskowanymi targetami dla wszystkich widocznych kandydatów; cały pozostały kontekst pozostaje wejściem. To nie skrócenie całego kontekstu SI do dwóch słów.

## 4. Odrzucone i niezatwierdzone
V2 global sum odrzucony (25 napraw/25 regresji historii,1 regresjaTop3). V3 context gain odrzucony: history Top1157→167/224,29 napraw/19 regresji,1Top3 regresja; Form2418→17,1 naprawa/2 regresje; newCase2420→21,3 naprawy/2 regresje. Nadal wybierał Pracą zamiast Praca.
Brak fitted alpha, wyjątku Praca, raw mieszania geometrii/SI, zgadywanego progu małych miejscowości. Nie wdrażać V4 przed wynikami gates i niezależną oceną kosztu/jakości na Androidzie.

## 5. Nowa implementacja diagnostyki
Nowy katalog experiments/herbert_agreement_v4: agreement.py,measure.py,source.py,test_agreement.py,new-forms.json,source-fixture.json,PROTOCOL.md,freeze-manifest.json; osobny workflow herbert-agreement-v4.yml.
Scope<=2lowerkeys/4source surfaces z dokładnym wspólnym lemma/POS albo istniejącym polskim diacritic fold; większe/niepowiązane slates pomijają etap1. Samodzielna kapitalizacja bez odmian pozostaje starym mean.
Etap1: ostatnie dwa alfabetowe słowa kontekstu, każde maskowane osobno; kandydat widoczny po kontekście. Ten sam target IDs/count/positions w każdym porównaniu. Case pooling logmeanexp z normalizacją liczby wariantów, następnie średnia dwóch probes. Jeden native batch B<=8/S<=512/T<=32.
Etap2: oryginalny mean dla case wariantów wybranego key, osobny batch B<=2. Native mean i sum muszą odtwarzać full baseline w0.001 i zachować case rank. Potem zachowujemy dokładny dotychczasowy case/tie-order.
Prezentacja: jedna najlepsza kapitalizacja perkey w kolejności nowych form, potem pozostałe w oryginalnym mean order. Osobne porównania do flat mean i identycznej prezentacji z mean wybierającym formę. Ordinal scores tylko dla metryk, nie model confidence.

## 6. Wykonane kontrole i oczekujące
Lokalnie V4 18 testów PASS, istniejące V1 13/V2 7/V3 18 PASS; transitive freeze chain i nowe cases24/source relations/pełne warianty/no overlap PASS.
Re-extraction z rzeczywistego zaufanego langpacka PASS:21 pełnych metadata entries i binary keys/ranks, stare9 identyczne. Nowe12entries dają6par jagoda/jagodą,róża/różą,kruk/krukiem,kot/kotem,piła/piłą,buk/bukiem; po4 przypadki nom/inst lower/upper.
Portable tokenizer preflight wszystkich304requests PASS:240case-only,16outside scope,32eligible_fold,16eligible_source_lemma_pos;48aktywnych, maxB/S/T8/14/3. AST/YAML PASS. To przygotowanie feeds, NIE lokalna inferencja.
CI zaplanowano: mobile13+portable5 i wszystkie starsze contracts,2471 tokenizer vectors/232 native batches,score/rank reprodukcje wszystkich280 wcześniejszych requests, fast/portable nowego wejścia,middle-mask single/batched native parity oraz mean/sum case-stage parity.
Wyniki faktycznej V4 inferencji i jakości PENDING. Nie twierdzić, że18 lokalnych testów dowodzi jakości SI.

## 7. Gałęzie, PR i run
Producer experiment/herbert-form-diagnostic-v1 HEADca2b8e347edba036f2be2d9af3a8e2984a0d32ea; parent186f116ff79c7317d3578dd40fd142114682357d. Dziewięć wyłącznie nowych plików; SHA każdego Gitblob zgodny z lokalnym UTF8, wszystkie wcześniejsze blob bez zmian.
Draft PR13 https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 opis zaktualizowany do pełnego aktualnego zakresu V1–V4 i odrzuconych scorerów. Base experiment/herbert-fp32-benchmark-v1 ebbe16b2cea2a924a7fef4feb635b2cf44ebbed3.
V4 https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38050273413 zarejestrowany in_progress na dokładnym SHA; nie czekać i nie monitorować do końca. Limit60s total/run, użytkownik zgłosi „Zakończone”.
Runtime draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 niezmieniony.

## 8. Artefakty i zaufanie
Model original artifact11312693984/run37230171787; SHA-256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2,651798883B,ORT1.21.1CPU2/1. Wszystkie7bundle files rehash przed inference.
Dictionary artifact11303920512/run37202645255 source commit041b28ae4587c531ef73e62933e9151cadb84c33, outerZIP10341499B SHA66e0480ea158385bb3cdb5bd2e4efda7c3d16ae5b5ae5ec6f114b0f6454ba740.
Inner pack1713402B SHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb. BinarySHAa32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a; sidecarSHA5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d. CI musi re-extract identyczny fixture21585B,CKDT106363keys/metadata16199entries.
V3 archived raw scores.json496135B SHAcd125b04f67a69aa0f185a9151e4448dc8f58c134cc40c7a30e5e9487b1f9b76 zachowany verbatim i zamrożony jako baseline.
Ostatni APK run38040432033/artifact11665712630, SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. Brak nowego APK; V4 ma zachować tylko reports, nie model export.

## 9. Ograniczenia i backlog
304requests osobno:history232 (224labelled,8unknown,4missingGold),form24,newCaseControl24,newForms24. History mostly bypass; case-only zachowany by construction, nie dowodzi nowych grammar/case gains. Gold i konteksty authored przed inference, słowa znane; brak blind gold/general accuracy. Full candidate-group Top3 nie jest phone-strip Top3.
Gate: brak Top1/Top3/form/case regresji w KAŻDEJ grupie obu comparatorów plus co najmniej1form repair wobec same-presentation baseline. SUCCESS CI nie oznacza gatePASS.
Case pooling może nadal wpływać na formy; observed-word score nie jest parserem ani pełnym sentence probability. Dwa sequential native calls do8+2rows zwiększają koszt. Hostp50/p95 stage i pipeline obejmuje diagnostic token-parity checks, NIE Android latency/deadline/RAM. Baseline i extra validation calls poza primary timing.
RAMFP32 nadal wysoki. Odłożone braki swipe dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam; kapitalizacją/kapitalizacje. Source frequency/population layer małych miejscowości nadal planowana, niewdrożona. Polskie tłumaczenie priorytetowe, inne błędy językowe backlog. Gemini/PAL waiver pozostaje.

## 10. Następny krok po „Zakończone”
Odczytać faktyczny status jobs/steps, pobrać/re-hash report artifact, niezależnie przeliczyć wszystkie304identities/form/case/Top3 metrics, feed shapes/target equality/native parity i host koszty. Sprawdzić Praca/Pracą oraz nowe różne rodziny, nie tylko aggregate.
Jeśli gateFAIL, pozostawić stabilny runtime mean i zapisać regresje; bez strojenia na tym samym gold. Jeśli gatePASS, niezależne przypadki i rzeczywisty koszt/quality na telefonie przed propozycją runtime. Brak automatycznej release/merge.

## 11. Delta wobec poprzedniego checkpointu
V3 rejection pozostaje. Dodano odrębny zamrożony przed inference test gramatycznej zgodności observedcontext z visiblecandidate, wyraźne dwa etapy i48aktywnychrequests. Dwanaście źródłowych kluczy i24nowe przypadki rozszerzają formę zamiast case-only. Zarejestrowano V4 run; jakość jeszcze nieznana. Aplikacja i słownik bez zmian.
