# Kamień milowy: MLM v3 attempt3 i zgłoszenie słabszych podpowiedzi
Data weryfikacji: 2026-10-06 (Europe/Warsaw).

## 1. Repozytoria i zakres
Main przed tym zapisem: CleverKeysPL 816b164c564af51d6e5fc3e3a61f5eb002768dc7;
CleverKeys-langpack-pl 042fb7454e6ac5e4006998046fefe7b220b20644.
Dokument identyczny na obu main, docs-only. Bez zmiany kodu/aplikacji.

## 2. Architektura
Geometric dekoduje. Jeden klucz langpacka ma źródłowe warianty/default/metadata.
SI w testowym Androidzie jest oddzielnym ekranem pomiarowym; live ranking nadal off.
Default32/max64/4096UTF16 i priorytet Shift/sentence caps/ręcznego wyboru bez zmian.

## 3. Ustalenia
Użytkownik zgłasza mniej słów/słabsze podpowiedzi na telefonie. Przyczyna NIEUSTALONA.
Nie zakładać poprawnie zaimportowanej/aktywnej paczki na urządzeniu bez informacji użytkownika.
Licencja wag odłożona na jego prośbę. Nie zmieniać słownika/rang punktowo bez diagnozy.

## 4. Odrzucone rozwiązania
Nie ponawiać ślepo podczas awarii runnerów, nie zmieniać frozen danych/bramek.
DistilRoBERTa unknown Ł i poprzedni HerBERT INT8 FAIL nadal odrzucone.
Geotrend v2 screen jakościowy FAIL; distilHerBERT v2 mixed, nie production approval.

## 5. Wdrożone i planowane
Ponowiono nieudane zadania run37363474711 z tym samym kodem
c1e9d3a7895f2a380bc75772985c88a53db32a4b; API success=true, attempt3.
Oba jobs naprawdę rozpoczęte: distil112217474022 i herbert112217474290 IN_PROGRESS,
checkout/setup wykonane, instalacja CPU dependencies trwa; inferencja jeszcze pending.
Contract112217474902 SUCCESS. Bez nowego APK/eksportu/live SI.
Plan: zdiagnozować zgłoszone słowa/paczkę/rodzaj podpowiedzi po dostarczeniu przykładów.

## 6. Zweryfikowane i niezweryfikowane
Attempt2 COMPLETED FAILURE: obie inferencje CANCELLED bez kroków i comparison CANCELLED.
Brak model predictions tego attemptu. Nie przedstawiać jako jakości FAIL.
GitHub Status 2026-10-06: All Systems Operational, Actions Operational,
incydent5października resolved22:49UTC; Actions normal21:54UTC.
Attempt3 IN_PROGRESS potwierdzone przez run/jobs API. Jakość nadal pending.
Nie odczytano danych z telefonu; brak diagnozy regresji podpowiedzi.

## 7. Gałęzie i historia
Producer experiment/polish-mlm-fresh-v3 kodc1e9d3..., draftPR10 baza v2.
Runtime docs trial/herbert-fp32-benchmark-v1 0367b334...; APK zaakceptowany db88fd28....
V2 rawresults a729fd780241a581f9cac153c0a6d926d8bfa1c1 i run37359525824SUCCESS.
Poprzedni checkpoint docs/PROJECT_MILESTONE_2026-10-05_FRESH_MLM_V3_RETRY_2.md:
attempt2 model jobs cancelled, brak kolejnego retry podczas awarii.

## 8. Słownik, źródła i artefakty
Sprawdzono Git tree i kod na db88fd28cca21ba2aa1e99b38e3886f1f147b5d6.
APK source assets nie zawierają pl_enhanced.bin/json. Polski jest z importowanego packa.
AsyncDictionaryLoader najpierw LanguagePackManager.getDictionaryPath(language),
potem bundled bin/JSON. getDictionaryPath zwraca files/langpacks/{code}/dictionary.bin.
Zweryfikowany lokalny authenticated v5 manifest: codepl, version5, wordCount106363,
capabilities lexicon/frequency/capitalization/metadata.
Pack SHAaa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb.
Nie jest to odczyt paczki faktycznie zainstalowanej na telefonie użytkownika.
SwipeSurfaceVariants.expand rozwija warianty tylko pierwszego klucza, zachowuje inne
klucze; pomija jego powtórzone powierzchnie tego samego języka. Sam nie obcina reszty.
Benchmark64/128cases lub model vocab nie stanowią słownika codziennej klawiatury.
Run: https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37363474711

## 9. Ograniczenia
106363 wpisy nie gwarantują pełnego słownika polskich odmian ani poprawnych rang.
Rozmiar/wersja lokalnie sprawdzonej paczki nie dowodzi stanu urządzenia.
Wnioski o ładowaniu są z kodu przypiętego APK, nie runtime trace użytkownika.
V3 authored diagnostic, nie independent humanblind; top3 par nasycone bezAI,
16/32 różne tylko nowe long21–26, stare regresje osobno. Host RAM nie jest telefonPSS.

## 10. Następny krok
Użytkownik: podać3–5 brakujących/słabo proponowanych słów, typ wejścia swipe/tap/nextword,
nazwę/wersję/liczbę wpisów polskiego packa (albo ekran zarządzania packami).
Sprawdzić obecność w dictionary.bin, częstotliwość, normalizację/odmianę i ranking dekodera.
Bez czyszczenia danych/słownika użytkownika/reinstalacji w ciemno.
Po zakończeniu attempt3 zweryfikować artifacts/identities i przeliczyć collector,
wszystkie fresh/historical regresje. Monitoring<=60s TOTAL/run, bez oczekiwania do końca.
Nie wykonywać kolejnych retry bez nowej przesłanki.

## 11. Różnica i utrwalenie
Awaria GitHuba usunięta; attempt3 dostał runnery i zaczął kroki. Nowe zgłoszenie jakości
codziennych podpowiedzi oddzielone od niewdrożonej SI i jej benchmarku.
Zweryfikowano importowaną ścieżkę słownika oraz106363 wpisy v5, ale stan telefonu nieznany.
Ten checkpoint exact readback na obu main. Bez merge/release/tag/version bump/subagentów.
Polski UI priorytet, inne locale backlog; trzy ustawienia czasów stacjonarnego BS backlog.
