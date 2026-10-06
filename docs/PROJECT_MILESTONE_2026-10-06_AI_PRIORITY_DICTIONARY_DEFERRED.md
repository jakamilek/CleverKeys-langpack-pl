# Kamień milowy: słownik odłożony, powrót do wyboru SI
Data weryfikacji: 2026-10-06 UTC.

## 1. Repozytoria
HEAD main przed zapisem: CleverKeysPL cae5c6feaa36dfbfe4b44ead0c5ad09056ee7adb;
CleverKeys-langpack-pl 4d07ff7a2989df566beacb46bc48dabcd3e84d7e.
Ten sam dokument na obu main, wyłącznie zapis audytu. Bez promocji kodu trial.
Szczegółowy wynik i odtwarzalny skrypt: CleverKeys-langpack-pl,
docs/audits/swipe-coverage-2026-10-06.json i docs/audits/audit_swipe_coverage.py.

## 2. Architektura
Geometric dekoduje ze słownika importowanego packa. Jeden klucz ma źródłowe
warianty/default/metadata; nie dublować kluczy z powodu kapitalizacji.
SI na telefonie pozostaje oddzielnym benchmarkiem, bez live ranking.
Default32/max64/4096UTF16; priorytet Shift/sentence caps/ręcznego wyboru bez zmian.
Dictionary.bin i lista unigrams.txt nie są tym samym zbiorem.

## 3. Ustalenia
Decyzja użytkownika 2026-10-06: naprawa słownika ma zostać zapamiętana i odłożona.
Aktualny priorytet: wybór SI. Nie kontynuować teraz naprawy słownika.
Użytkownik podał dodam, grzeje, kasami, nawilżane, odpowiadam, patrzysz,
poczekaj, podpowie, pozdrawiam i potwierdził typ wejścia: swipe.
Wszystkich 9 brak w canonical CKDT oraz pod znormalizowanymi kluczami
zarówno starego preview v2, jak i global-casing v5.
Brakujące formy nie mają ranków w tych paczkach.
Dodam i pozdrawiam są w unigrams.txt obu paczek, pozostałych 7 nie ma.
Porównanie wszystkich kluczy case-insensitive: 106363 -> 106363,
0 usuniętych, 0 dodanych, 0 zmienionych ranków. V5 zmienia pisownię/metadata,
nie zmniejsza tego zbioru. Potwierdzona luka istnieje przed próbami SI.
Nie dowodzi to wersji/importu paczki faktycznie aktywnej na telefonie.

## 4. Odrzucone podejścia
Nie przypisywać braków tym 9 słowom do SI ani samego rankingu.
Nie poprawiać pokrycia przez ręczne dopisanie wyłącznie tych 9 słów.
Nie usuwać danych aplikacji/słownika użytkownika ani reinstalować w ciemno.
Nie przedstawiać ASCII filtra jako udowodnionego powodu odrzucenia każdej formy.
Nie osłabiać bramek MLM w odpowiedzi na niepowodzenie referencji HerBERT.

## 5. Plan
Naprawa pokrycia odmian słownika: BACKLOG, obowiązek powrotu zachowany.
Zakres: globalny audyt źródłowej selekcji/fleksji z przypadkami 9 zgłoszonych słów;
nie ręczne dopisanie 9 słów. Pełen wynik audytu w poprzednim checkpoint.
Priorytet SI:
1. Naprawić kontrolę ładowania referencyjnego HerBERT na izolowanej gałęzi,
   zachowując wynik nieudanego v3 i nie zmieniając danych/gold/bramek jakości.
2. Dokończyć porównanie jakości distilHerBERT kontra HerBERT na tych samych
   przypadkach, osobno fresh/historical i konteksty 16/32.
3. Jeżeli distilHerBERT przejdzie ustalone bramki, przygotować ONNX FP32
   i oddzielny benchmark Android czasu, PSS i zgodności na Nubii.
   INT8 dopiero po zgodnym FP32 i z odrębną kontrolą utraty jakości.
4. Decyzja o integracji dopiero na podstawie jakości oraz pomiarów telefonu.
Nie ma wyboru modelu do produkcji ani nowej paczki/APK.

## 6. Weryfikacja i niewiadome
Skrypt odczytał nagłówek CKDT V2, wszystkie canonical/ranks,
cały normalized index i accent map, sprawdził granice sekcji, indeksy
oraz pełne zużycie bajtów. Nie znalazł aliasów 9 kluczy.
Zweryfikowano SHA z GitHub artefaktów oraz wewnętrznych ZIPów.
Workflow pl-preview.yml a1fa0193... buduje immutable core 100000,
dodaje moduły (+6363), generuje unigrams osobno --top-n 5000.
build_pl_preview.py na tym samym commit ma ASCII wymóg Hunspell AND AOSP,
filtry foreign/no-positive-evidence/typo i limit. To kandydaci przyczyn,
ale per-word drop reasons 9 słów nie są jeszcze odtworzone.
Nie zmierzono jakości gestów/załadowania słownika na urządzeniu.
Sprawdzono run_model.py v1 oraz v3 na c1e9d3a7895f2a380bc75772985c88a53db32a4b:
v1 wymaga dokładnego zbioru oczekiwanych niewykorzystanych kluczy,
v3 odrzuca każdy unexpected key. Naprawa powinna zachować ścisłość weryfikacji.

## 7. Gałęzie
Producer feature/source-variants-trial-v1 041b28ae4587c531ef73e62933e9151cadb84c33
zawiera v5; preview ops/baseline-sync-2026-09-20 a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307.
Producer experiment/polish-mlm-fresh-v3 c1e9d3a7895f2a380bc75772985c88a53db32a4b,
draft PR10. V2 results a729fd780241a581f9cac153c0a6d926d8bfa1c1.
Runtime trial/herbert-fp32-benchmark-v1 dokumenty 0367b334...,
bazowy APK kod db88fd28cca21ba2aa1e99b38e3886f1f147b5d6.
Nie scalono eksperymentalnych gałęzi do main.

## 8. Artefakty i integracja
Preview run36916501466 SUCCESS, artifact11189614575 cleverkeys-pl-preview:
outer SHA256 827a20f8489fad51023e1c0d58319dca030d304f7e213ef4973141251c3ad9ff;
inner SHA256 301b0b9c7c4c7b96ac7a2545bf27745b6ee38c87f5d04133ede490008d861945.
V5 run37202645255 SUCCESS, artifact11303920512 cleverkeys-pl-global-casing-trial:
outer SHA256 66e0480ea158385bb3cdb5bd2e4efda7c3d16ae5b5ae5ec6f114b0f6454ba740;
inner SHA256 aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb;
dictionary SHA256 a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a.
APK SHA256 c3d15aaf1ba26b8f2534199dda5a6b8835cb72e5233038f4e6f1292b57ed3dd9.
MLM v3 run37363474711 attempt3 zakończony:
contract SUCCESS, distilHerBERT SUCCESS, HerBERT FAILURE, comparison FAILURE.
HerBERT zatrzymała bramka unexpected keys:
bert.pooler.dense.bias/weight oraz cls.sso.sso_relationship.bias/weight.
Missing/mismatched/error_msgs puste według logu. Nie ukończono referencji/
kontroli pełnego MLM, więc brak porównania jakości obu modeli dla v3.
Nie jest to awaria runnerów ani wynik jakości HerBERT.
HerBERT diagnostic artifact11404641190 SHA256
c2f9aaf22c8a24d83fccb6499935802f322aa0d0a37b5fffc316a3e9d6c6994d.
Nie ponowiono jobs.

## 9. Ograniczenia
106363 wpisy nie gwarantują pokrycia polskiej fleksji.
Zbiór 9 jest zgłoszeniem użytkownika, nie reprezentatywnym corpus testem.
Aktualny import/version/wordCount telefonu nieznany.
Korekta pokrycia może zmienić koszty ładowania/geometrię/ranking i wymaga regresji.
Licencja modeli odłożona przez użytkownika, nie założono licencji.
HerBERT FP32 phone PSS >2GiB nadal przeszkodą; host RAM nie jest phone PSS.
V3 authored diagnostic, nie external/humanblind; strukturalne top3 par
nie dowodzi poprawy SI. CTC poza zakresem.

## 10. Następny krok
Wrócić do SI: skorygować ładowanie referencji z udokumentowaną dokładną listą
nieużywanych elementów checkpointu, bez dopuszczenia braków wag MLM,
i uruchomić nowe zamrożone porównanie o niezmienionych przypadkach.
Potem warunkowo zmierzyć mniejszy distilHerBERT na telefonie.
Pełny HerBERT FP32 jest punktem odniesienia jakości, nie rekomendacją
do codziennej klawiatury ze względu na zmierzony koszt pamięci.
Nie monitorować CI dłużej niż 60s TOTAL/run; użytkownik podaje zakończenie.
Odłożony słownik i trzy ustawienia czasów BS nadal wymagają przyszłej naprawy.

## 11. Różnica od poprzedniego zapisu
Poprzedni PROJECT_MILESTONE_2026-10-06_SWIPE_DICTIONARY_COVERAGE.md
ustalił brak 9 form w obu paczkach i błąd ładowania HerBERT.
Użytkownik teraz jawnie odłożył słownik i wrócił do wyboru SI.
Zachowano wynik audytu i backlog; kolejność pracy zmieniona na SI.
Zweryfikowano różnicę bramki loading_info pomiędzy v1 i v3.
Ten zapis jest docs-only, identyczny na obu main.
Bez merge/release/tag/version bump i bez nowych runów.
Polski UI priorytet; inne locale i czasy stacjonarnego BS backlog.
