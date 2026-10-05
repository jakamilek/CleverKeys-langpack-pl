# Kamień milowy: zweryfikowane wyniki mniejszych polskich MLM v2
Data: 2026-10-05 (Europe/Warsaw). Status: kontrole techniczne PASS; jakość mieszana.

## 1. Zweryfikowane repozytoria i zakres
Main przed tym dokumentem: CleverKeysPL 09c79257bda8d6e146593c630b99f509bb558475;
CleverKeys-langpack-pl b1e0fbec66fef40e0938e603040492aa55769b39. Zweryfikowane przez API branches.
Wyłącznie identyczny docs-only checkpoint na obu main, bez promocji kodu.
Producer experiment/polish-mlm-16-32-v2: zamrożony kod 56b7d0f213fcdda1a8a5c245555bd3307fcc2133,
archiwum wyników a729fd780241a581f9cac153c0a6d926d8bfa1c1.
Runtime trial/herbert-fp32-benchmark-v1 docs-only 16eb460f16ca588272e8ff37d68a4940fef1c0c5.
Użytkownik zgłosił zakończenie runów; odczyt i archiwizacja autoryzowane.

## 2. Utrzymana architektura
Geometric dekoduje; jeden klucz słownika ma źródłowe formy/atrybuty/default.
Nie dublujemy kluczy ani nie dopisujemy ręcznych opisów znaczeń. Obie formy dostępne.
Przyszła SI porządkuje parę kapitalizacji pierwszego kandydata; Shift, sentence caps,
wybór ręczny, stale fallback i prywatność zachowują priorytet. Live SI nadal off.
Default 32/max64/4096 UTF-16 z bieżącego pola, z case/interpunkcją, bez globalnej historii.

## 3. Nowe zaakceptowane ustalenia
distilHerBERT jest kandydatem do dalszej weryfikacji kapitalizacji, nie wyborem produkcyjnym.
Nowe naturalne formy: HerBERT 24/32, Geotrend 21/32, distilHerBERT 25/32.
Starsze formy: 50/64, 40/64, 46/64. Nowa interpunkcja: 20/24, 11/24, 16/24.
distilHerBERT: nowe małe 16/16, wielkie 9/16, 9 napraw defaultu, zero jego regresji.
Przechodzi zamrożony wstępny screen >=23/32 i <=3 regresji defaultu; Geotrend FAIL.
Nie ukrywamy starszych regresji ani nie sumujemy różnych populacji w jeden wynik.

## 4. Odrzucone i rezerwowe rozwiązania
Geotrend Distil nie przechodzi obecnej bramki jakości; metoda/tokenizer bez retuningu.
sdadas DistilRoBERTa v1 nadal odrzucona: Ł staje się unk, 26 spans w 22/384 requests.
HerBERT FP32 pozostaje referencją; wcześniejszy INT8 FAIL pozostaje bez zmian.
Geotrend BERT12 rezerwa, bez ładowania wag. ORIS Small C gated research/custom code,
API401, bez pobrania modeli/akceptacji warunków. Nie przyjęto licencji nauczyciela za ucznia.

## 5. Wdrożone i niewdrożone
Archiwum producer experiments/polish_mlm_compare_v2_results/: pełne predictions/requests/
report/validation/tokenizer-validation i environment obu modeli, comparison JSON/MD i RESULTS.md.
15 plików, wszystkie Git blob SHA zweryfikowane przed commit. Wagi nie opublikowane.
Runtime canonical spec/todo/TOC zaktualizowane i dokładnie odczytane; draft PR9 przepisany
wokół wyników końcowych, nadal draft, baza v1. Brak nowego APK/eksportu/kwantyzacji/live SI.
Trzy opcje czasu stacjonarnego Backspace pozostają backlogiem.

## 6. Zweryfikowane i niezweryfikowane
Run 37359525824 SUCCESS, kod 56b7d0f213fcdda1a8a5c245555bd3307fcc2133.
Contract 111930329726, distilHerBERT 111930393764, Geotrend 111930393996,
collector 111930931001 — PASS. 11 starych + 8 nowych testów kontraktu.
Oba: strict full-weight load bez missing/mismatch/unexpected/error, oryginalny tokenizer
przed wagami, 384/384 requests. Oryginalna pełna głowica/projection parity:
Geotrend 0.0, distilHerBERT max 0.0000343323. Trzy ZIP size/SHA z API potwierdzone.
Przeliczenie niezmienionym zamrożonym collectorem dokładnie równe comparison.json i MD.
Niezależna jakość, ONNX i native tokenizer, Android RAM/energia/latencja nadal niesprawdzone.

## 7. Istotne gałęzie i historia
Producer v2 wynik a729fd780241a581f9cac153c0a6d926d8bfa1c1, parent 56b7d0f213fcdda1a8a5c245555bd3307fcc2133.
V1 wynik 9162d9a9f2ac3b94f4212a773cf9be80e1cb632a; kod 769fc465...,
run 37355290211 FAILURE z odrzuconą DistilRoBERTa i pełną referencją HerBERT.
Runtime docs 16eb460f16ca588272e8ff37d68a4940fef1c0c5, parent 18f252d7bf211bddf9eaebecea2eb17a07c14cea.
Zaakceptowany na Nubii APK db88fd28cca21ba2aa1e99b38e3886f1f147b5d6 niezmieniony.
Draft PR8 historia v1; draft PR9 v2 wynik mieszany. Nie merge/release/tag/version bump.

## 8. Źródła, artefakty i tożsamość
distilHerBERT BartekK rev7276461b7a8fd668aaf30313c03a68bd11aad642:
81967184 parametry, oryginalny pytorch_model.bin327906539B,
SHA1c5ee904a62f92b249c427a1d542f8934295b1bff435914217b3c80aae60f36b.
Licencja wag niewyjaśniona; nie zakładamy dziedziczenia CC-BY nauczyciela.
Geotrend Distil rev9002d311e35aac14575bf53ad4fa3d8f8b853c2b:
60737405 parametry, model.safetensors242962316B,
SHAd58e76039a2d6664bf0f5b4bfdbb8227ffdcb0d498f3f054743572010a981574.
V5 pack SHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb:
122480 surfaces,16117 multivariant keys. distilHerBERT full coverage; Geotrend standalone
ą/ę unknown, pełne coverage false, wszystkie pary i384 requests/836 spans PASS bez wyjątków.
Comparison ZIP11366575092 SHA2eb6b871f73985a9145d489536978f244b36199aac02307cad2082414fab0b79;
Geotrend11366302106 SHA092e51daa590ad63b10a2084e3c6edb61c9ec361170e6b72c71c7860f56c4240;
distilHerBERT11365304288 SHA8491fdb59f4c24c230aabc4a15de51f863aa80889c670a0d6e25d6dfc1271a88.
Wagi nie w repo/ZIP wyników/APK; bajty oryginalnych wag nie oznaczają rozmiaru ONNX/APK.

## 9. Ograniczenia i regresje
192 znane autorskie cases/384 queries; nie ślepa niezależna ocena.
Starsze formy distilHerBERT vs HerBERT: 3 naprawy/7 regresji (Warszawska,Lub,wilk,Kruk,
Buk,Zając dwa konteksty), netto -4. Nowa interpunkcja 1 naprawa/5 regresji, netto -4.
Nowy Buk regresją wobec HerBERTa, Róża/Ale/Tutaj/Kruk/Buk/Zając/Kot błędnie za małą formą.
Top3 par nasycone z definicji także bez SI, nie dowód korzyści. Naturalne6–14 słów:
wejścia16/32 identyczne. Sztuczny dystans23–25: distilHerBERT16=16/32,32=19/32.
Starszy replay: HerBERT7/8, Geotrend1/8, distilHerBERT7/8; bez kalibracji z geometrią.
Starsza interpunkcja15/20,10/20,17/20 raportowana osobno.
Host peak RSS HerBERT1426.48/Geotrend605.48/distilHerBERT984.55MiB, oddzielne jobs/history;
nie kontrolowany pomiar telefonu. 34% mniej parametrów nie rozwiązuje potwierdzonego kosztu PSS.
Telefon HerBERT baseline346.2MiB → load2121.0 → max2132.1 → close1336.8 pozostaje dowodem.

## 10. Następny uzasadniony krok
Nowe niezależne konteksty, realne dłuższe teksty16/32, wszystkie znane regresje; licencja wag.
Dopiero uzasadniona redystrybucja: oryginalny FP32 export/parity/native fixtures i rzeczywisty
pomiar RAM/load/p50/p95/energii na Nubii. Brak kontaktu z autorami bez osobnej autoryzacji.
Nie zmieniać defaultu32 ani nie aktywować interpunkcji na podstawie tej małej próby.
Actions monitoring <=60 sekund TOTAL/run, bez watch/sleep; użytkownik zgłasza zakończenie.

## 11. Różnica i dokumenty
Poprzedni docs/PROJECT_MILESTONE_2026-10-05_SMALLER_MLM_SCREEN_V2.md miał CI pending.
Teraz complete native heads/preflight, quality + regressions, rzeczywiste parametry, host costs,
trzy sprawdzone ZIP i identyczne collector recomputation, trwałe surowe archiwum.
Raport: https://github.com/jakamilek/CleverKeys-langpack-pl/blob/a729fd780241a581f9cac153c0a6d926d8bfa1c1/experiments/polish_mlm_compare_v2_results/RESULTS.md
Runtime docs/specs/polish-context-ai.md,memory/todo.md,docs/TABLE_OF_CONTENTS.md exact readback.
Ten dokument identyczny na obu main, exact readback wymagany. Polski UI priorytet;
inne języki backlog. Brak subagentów; inherited Gemini/PAL wymóg uchylony przez użytkownika.
