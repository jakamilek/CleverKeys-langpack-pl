# Kamień milowy: zweryfikowane wyniki MLM v3 loading-fix
Data weryfikacji: 2026-10-06, Europe/Warsaw.

## 1. Repozytoria
Main przed zapisem: CleverKeys-langpack-pl cc9ff26d23a58bb1d8f51a14a51612db6fbf1c54;
CleverKeysPL 90cb1071e979b28dc367705a8b88d3767559a9d8.
Ten dokument identyczny na obu main, docs-only. Raw archiwum na izolowanej gałęzi.

## 2. Architektura
Geometric + importowany polski słownik ze źródłowymi wariantami/default/metadata.
SI Android jest osobnym benchmarkiem, live ranking off; default32/max64/4096UTF16.
V3 host test: oryginalne FP32 MLM, bez promptów opisowych/nowych wag.
Metadata ograniczają dozwolone formy/default, nie są semantyczną instrukcją modelu.

## 3. Ustalenia
Run37500235605 completed SUCCESS: contract, oba inference i comparison SUCCESS.
Oba modele dały komplet256 requests. Loading/tokenizer/head/parity checks PASS.
Niezależny collector z GITHUB_SHA83fa31... reprodukuje comparison.json i Markdown
dokładnie. Techniczne SUCCESS nie oznacza jakości PASS.
DistilHerBERT nie przechodzi wcześniej zamrożonej kwalifikacji:
wszystkie4 fresh32 strata PASS, historical64 46vs50 HerBERT, wymagane>=49 -> FAIL.
Nie obniżamy bramki. Brak wyboru do produkcji/eksportu na telefon.
Słownik ODŁOŻONY przez użytkownika i musi zostać naprawiony później; licencja odłożona.

## 4. Odrzucone podejścia
Brak strojenia progów/wyjątków po gold i ponownego nazywania tego niezależnym testem.
Nie mieszać wyników failed v3 z nowym commitem. Nie utożsamiać host RAM z phonePSS.
Nie przedstawiać nasyconego top3 dwóch form jako poprawy SI.
DistilRoBERTa unknown Ł, HerBERT INT8 wcześniejszy FAIL i Geotrend v2 screen FAIL
pozostają odrzucone. DistilHerBERT jest obiecujący, lecz nie zatwierdzony.

## 5. Wykonane i plan
Poprawiona dokładna bramka unused pooler/SSO HerBERT, wspólna runner/collector.
30 testów PASS i niezmieniony request SHA przed CI.
Oba modele rerun,14 raw files zapisane w GitHub z kontrolą blob SHA,
trzy ZIP SHA zweryfikowane. DraftPR11 uaktualniony wynikiem.
Następnie analiza rozbieżnych przypadków oraz możliwości ostrożnego rankingu;
ewentualna nowa metoda wymaga nowego protokołu i oddzielnej walidacji,
nie ad-hoc gold exceptions. Telefon ONNX/INT8 nadal niewykonany.

## 6. Wyniki i niewiadome
Trafność top1:
fresh64 window16: HerBERT62/64, distil63/64;
fresh64 window32: HerBERT57/64, distil61/64;
historical64 windows16/32: HerBERT50/64, distil46/64.
Fresh32 short_known:15vs16; short_new16vs16; long_known13vs15; long_new13vs14.
Historical32: distil traci7 poprawnych HerBERT i naprawia3.
Straty: nazwisko Warszawska po pani, Lub jako forma imienia Luba, wilk zwierzę,
Kruk po doktor, Buk po nazwisko brzmi, dwa Zając po pan.
Naprawy: imię Jagoda, pospolite lub, zając zwierzę.
Historical32 lower HerBERT29/32, distil30/32; upper21/32vs16/32.
Fresh32 upper31/32vs32/32: nie jest to globalny brak kapitalizacji.
96 par okien identyczne,32 fresh long różne;16->32:
HerBERT5 pogorszeń/0 napraw, distil2 pogorszenia/0 napraw.
Default16 nie zatwierdzony na podstawie małej autorskiej próby.
Parametry HerBERT124494416, distil81967184 (około34% mniej).
Peak hostRSS1380.54MiB vs952.75MiB z osobnych jobs; nie kontrolowany pomiar telefonu.
Phone distilPSS/latency/energy i szersza jakość nieznane.

## 7. Gałęzie
Experiment/polish-mlm-v3-loading-fix-v1:
frozen executable83fa31fd6071ba48b8e7828c58bb28ff2d49f2f1;
archive commit b2c3342643a77ef01a04323034465acae8609c27.
DraftPR11 baza experiment/polish-mlm-fresh-v3, nie scalony.
Historyczny v3 code c1e9d3a7895f2a380bc75772985c88a53db32a4b/run37363474711
zachowane, HerBERT wtedy nieukończony wskutek bramki loading.
V2 rawresults a729fd780241a581f9cac153c0a6d926d8bfa1c1.
Runtime bazowyAPK code db88fd28cca21ba2aa1e99b38e3886f1f147b5d6 bez zmian.

## 8. Artefakty/proweniencja
Run https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37500235605
Request SHA a20cad29b09554a9718f1d520d68c4e695c9274aac0b708801463f498097f53d.
Freeze file SHA256 1ad6fba137949fcc2d6a87ef83ecf19cc8d2404d6efcfa83f0c2cfe07c8cdc4c.
Artifact11429830684 HerBERT ZIP SHA256
ed16a9230f1599a88ce97b3e1c4f5971e8d6c51e9d3f3a4ceb61fe630e6c13c8.
Artifact11428674453 distil ZIP SHA256
4b4742470903325fb0fcffc5466b113f5986ac52c9ea97a6b7468b2318144fc7.
Artifact11429616965 comparison ZIP SHA256
7f1ec7e72c2aa02f5d92d0825bfc03cc908bd14acf99d80e05168484ccbffa18.
Raw reports/predictions/validation/requests/environment i comparison oraz opis:
experiments/polish_mlm_fresh_v3_loading_fix_v1_results w producerze na b2c334....
artifact-provenance.json zapisuje źródła/SHA/expiry; bez wag.
Collector odtwarzać z code83fa31 i GITHUB_SHA83fa31, nie SHA późniejszego archiwum.

## 9. Ograniczenia
Fresh texts autorstwa asystenta po odczycie v2, bez niezależnego anotatora/humanblind.
Long21–26words, brak >32 i reprezentatywnych prywatnych rozmów.
Nie oceniono interpunkcji ani multi-key geometric replay.
FP32 HerBERT phone całoprocesowyPSS >2GiB nadal przeszkodą.
Brak nowego APK/export/live SI/default16; licenseReviewDeferred nie jest licencją.
Naprawa braków9 form swipe pozostaje backlog, nie poprawiona przez SI.

## 10. Następny krok
Omówić mixed wynik: lepsze fresh vs gorsze historical nazw własnych.
Analiza błędów/ostrożnego rankingu przed kolejnym etapem; nowy sposób oceny
musi oddzielać development od nowej frozen walidacji.
Nie kwalifikować do telefonu przez samo techniczneSUCCESS i nie luzować progu.
Monitoring<=60s TOTAL/run. Brak nowego runa.
Słownik, trzy ustawienia czasów stacjonarnegoBS i inne locale nadal backlog.

## 11. Różnica od poprzedniego kamienia
PROJECT_MILESTONE_2026-10-06_MLM_V3_LOADING_FIX_STARTED.md miał QUEUED/pending.
Teraz oba complete wyniki zweryfikowane i przeliczone, zapisano pełną proweniencję
i raw archive. Wykonanie SUCCESS, quality screenFAIL history64.
Main tylko dokumenty, bez merge/release/tag/version bump/subagentów.
Ten dokument exact readback w obu repo.
