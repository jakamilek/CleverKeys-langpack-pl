# HerBERT V4 — wyniki zweryfikowane, metoda zgodności odmiany odrzucona

## 1. Stan i identyfikacja
2026-10-10, po „Zakończone” o 14:09 Europe/Warsaw. Main przed checkpointem: CleverKeysPL 2a568f9a8e5a6520e4089e4f3523b5e460cefce0; CleverKeys-langpack-pl b5b208856c776ac9d18c912a49195b6e1da0500b. Ten commit dodaje wyłącznie nowy dokument do obu main; starsze checkpointy i kod zachowane.

## 2. Architektura i aktualna aplikacja
Geometric ocenia ślad palca i dostarcza kandydatów. Live opcjonalny oryginalny HerBERT FP32 nadal używa mean log probability i compact-case-v4.
CleverKeysPL trial/herbert-live-v1 nadal3f48e456f0d8f411e80be3857f1846e4b2cd139e, draft PR4. Nie zmieniono scorer/runtime/APK/model/langpack/deadline350ms/context32 (16/32/64)/editor identity/prywatności. V4 pozostaje tylko diagnostyką hostową.

## 3. Sprawdzone wyniki
Run38050273413 completed SUCCESS na ca2b8e347edba036f2be2d9af3a8e2984a0d32ea. Wszystkie jobs/steps PASS. Jakościowo qualityGatePassed=false, allPreservationPassed=false, hasFormImprovement=true.
304requests raportowane osobno; oba comparatory mają identyczne aggregate accuracy/regression counts.
History232,224labelled: Top1157→157,0napraw/0regresji; rawTop3218→218. History216case-only+16outside scope pomija etap odmiany.
Form24: exactTop118→19,3naprawy/2regresje; formTop120→19,3naprawy/4regresje; rawTop323→23,0Top3regresji.
CaseControl24: Top120→20,rawTop324→24; stare case preference zachowane by construction.
NewForms24: exactTop120→17,1naprawa/4regresje; formTop123→20,1naprawa/4regresje; rawTop323→23,0Top3regresji.
Conditional case w goldform bez zmian: history144/200,form22/24,case controls20/24,newforms21/24. To nie nowy zysk kapitalizacji. Nie łączyć datasetów jako general accuracy i nie kompensować regresji naprawami.

## 4. Odrzucone i niezatwierdzone
V4 observed-context score jako zastępstwo live mean odrzucony. Wcześniejsze global sum V2 i context gain V3 nadal odrzucone. Brak wdrożenia, fitted threshold/alpha, wyjątku Praca, ręcznych odmian/opisów/rdzeni, duplikatów lub raw miksu geometry/SI.
Brak nowego exportu/modelu/APK/uczenia, merge/release/tag/version bump. Nie uruchomiono kolejnej próby.

## 5. Przebadana metoda i istotne przykłady
Ostatnie dwa alfabetowe słowa istniejącego kontekstu maskowane osobno; kandydat widoczny. Każdy probe ma identyczne target IDs/count/positions we wszystkich wariantach. Pełny pozostały kontekst zachowany, nie zmiana context limit na2.
Stage1: logmeanexp po case wariantach perlowerkey, średnia po dwóch probes, jeden batch B<=8. Stage2: oryginalny mean case wybranego key, osobny batch B<=2; native mean/sum odtwarzają full baseline i rank. Wszystkie warianty zachowane; jedna najlepsza kapitalizacja perkey przed resztą. Porównano flat mean i identyczną prezentację z mean wybierającym formę.
„Gdzie leży wieś ” nadal Pracą, potem Praca,praca,pracą; key scores praca−9.975818310055748,pracą−9.641812208952356. Trzy inne nominative Praca poprawione.
Regresje exactTop1: „Spotkam się z panią ” Maliną→Malina; „Rozmawiam z panem ” Laską→Laska. Dodatkowe formregressions pracy→praca po „obok wsi ”/„od wsi ”, gdzie case error był już wcześniej.
New regressions: „Do klasy dołączyła uczennica o imieniu ” Jagoda→Jagodą; „Stolarz tnie deskę ostrą ręczną ” piłą→piła; „Trasa przebiega między Poznaniem a ” Piłą→Piła; „Wykład wygłosi dziś profesor ” Buk→Bukiem. New repair: „Nowym trenerem został pan ” Kotem→Kot.

## 6. Weryfikacja
CI mobile13+portable5+V1 13+V2 7+V3 18+V4 18, łącznie74tests PASS. Transitive freezes,2471 tokenizer vectors/232 native batches/532 candidates,full fresh V1/V2 replay, actual source extraction21entries i middle-mask single/batched native parity PASS.
Pobrano report ZIP, sprawdzono size/SHA,7 bounded members,992634 aggregate uncompressed bytes (reports+environment; bez modelu), bez duplicate/traversal/symlink.
Niezależnie przeliczono wszystkie304 IDs/context/surfaces/gold,280 previous mean/sum/rank reproductions,freeze hashes,48 middle-mask feed shapes/target equality/mask/positions/padding/visible candidates,form pooling/rank i case-stage mean/sum reproduction. Przeliczono oba presentationorders, każde pole outcomes/groups/changes/quality gates i timing quantiles. To analiza gotowych wyników z oryginalnym portabletokenizer, nie nowa lokalna inferencja.
Recorded maxSingleBatchScoreError0; selected native case-stage reconstruction error0. Lokalna re-extraction z actual source pack i frozen contract PASS.

## 7. Gałęzie, PR i run
Producer experiment/herbert-form-diagnostic-v1 measured code ca2b8e347edba036f2be2d9af3a8e2984a0d32ea; result-only HEAD86ab57abecebcff3c290fc269fd78ab5e2a7cf60. Dwa nowe pliki scores.json/RESULTS.md; wszystkie wcześniejsze blob i modes bez zmian.
Draft PR13 https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 zaktualizowany do odrzuconych V2–V4 i wyników V4. Base experiment/herbert-fp32-benchmark-v1. Runtime PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 bez zmian.
Run https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38050273413 SUCCESS. Odczyt zakończonego runu; bez oczekiwania/monitorowania lub nowego runu. Limit60s total/run pozostaje.

## 8. Artefakty i pochodzenie
Artifact11669641343 herbert-agreement-v4-reports, ZIP93808B SHA25698b19809aa6cce328887598fceeeec0b4c445eb79673ffbeacc7fa279fa59b46.
Verbatim raw scores.json706925B SHA25616aa94eeac63cff130a411405685893e09c09a3e7f7afb18ee68c588852c1027, Gitblobddc56838a4c3dc02c40a7886c458469a78de9407, trwały katalog experiments/herbert_form_diagnostic_results/2026-10-10-v4.
Original model651798883B SHAf851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2,artifact11312693984/run37230171787,ORT1.21.1CPU2/1,numpy2.2.3,tokenizers0.22.2.
Source artifact11303920512/run37202645255 commit041b28ae4587c531ef73e62933e9151cadb84c33, innerpackSHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb.21fullentries/CKDTkeys re-extracted,stare9identyczne,6newformpairs.
Ostatni APK run38040432033/artifact11665712630 SHA b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f. Brak nowej aplikacji.

## 9. Koszt, ograniczenia i backlog
48activeformrequests,stage1 B8 + stage2 B2. Script528nativecalls:48baseline+96primary+384single-rowvalidation, oprócz osobnego V1/V2replay. Extra validation poza primarytiming.
Hostp50/p95: grammar batch80.64/114.76ms;case26.64/36.19ms;primary109.54/152.64ms. Batch timers conversion/native/checks; pipeline przygotowanie plus diagnostic fast/portable parity. Brak oddzielnego czystego preparation/inference decomposition i fair production speed comparison. Nie Android/phone latency/deadline/RAM. Dwa sequentialcalls i większy batch zwiększają pracę; gateFAIL już blokuje wdrożenie.
Case pooling nie daje pełnej niezależności od case, observed-word score nie jest parserem/calibrated sentence probability. Authored frozen gold,6newknownfamilies,bezblindgold. History8unknown/4missingGold; preserving case controls to construction. GroupTop3 nie jest całym phone strip; poprawny case nadal rank4 w niektórych wcześniejszych błędach.
FP32RAM wysoki. Odłożone braki swipe dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam i kapitalizacją/kapitalizacje. Globalna source-backed frequency/population kontrola małych miejscowości nadal planowana. Polish translations priorytet,other locale backlog;Gemini/PALwaiver.

## 10. Następny krok
Przedstawić negatywny wynik i pozostawić sprawdzony runtime. Schemat geometry→form→case pozostaje możliwy, ale ta konkretna ocena odmiany nie daje bezpiecznej poprawy. Następna metoda wymaga świeżych niezależnych danych i wykorzystania źródłowej morfologii; nie dobierać progu na tych48gold ani word-specificfix.
Przed kolejną implementacją SI rozważyć powrót do odłożonego audytu braków słownika zgodnie z wcześniejszym planem użytkownika. Nie uruchamiać w ciemno kolejnej kosztownej próby ani nie generować nowego APK dla odrzuconej metody.

## 11. Delta wobec poprzedniego checkpointu
V4pending zmienił się w zweryfikowany techniczny SUCCESS/jakościowyFAIL. Zachowano raw wyniki verbatim i sprawdzono wszystkie metrics/feeds. Metoda naprawiła3innePraca, lecz nie „Gdzie leży wieś”,pogorszyła2previouscorrect i4newcorrectTop1. ExistingformTop1 i newformTop1 spadły. Nie ma Top3/case regressions w grupach; nie uzasadnia to zmiany firstword rank. Aplikacja pozostaje bez zmian.
