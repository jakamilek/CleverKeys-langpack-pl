# Korekta domyślnej kapitalizacji wyrazów funkcyjnych — 2026-10-04

## 1. Zweryfikowany stan repozytoriów
Przed dodaniem tego kamienia zweryfikowano main: CleverKeysPL
6758e09fbd485342d29c2f004f3fcd5e9c643117; CleverKeys-langpack-pl
e83c8d73f00bbf8f629ade957bffa417e011dacb. Data: 2026-10-04.
Dokument otrzyma osobne commity dokumentacyjne na obu mainach. Kod aplikacji
pozostaje na docs/source-variants-integration-v1, 5200f718a0a9f2cf29135d6e8607c171d308f889,
draft PR #1. Producer feature/source-variants-trial-v1 został przesunięty fast-forward
z 75a06570cc9eaac72f1e7c4376a4efd068be73fb do bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f.
Wszystkie siedem zmienionych plików producer odczytano z nowego commita i porównano
z przygotowaną treścią — zgodność.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md)
i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md).

## 2. Architektura
Swipe pozostaje geometryczny. Jeden klucz słownika może zawierać warianty
kapitalizacji. APK, ranking geometryczny, ustawienia v9 i zaakceptowana obsługa
edytora/Backspace pozostają bez zmian. Naprawa dotyczy budowania słownika.
Przypięty historyczny pack v3 jest odtwarzany dotychczasowym kompilatorem;
oddzielny, jawny etap poprawia domyślną pisownię funkcyjną i tworzy pack v4.
Nie zwiększa liczby wpisów ani nie duplikuje słów przez wielkość litery.

## 3. Zaakceptowane ustalenia i przyczyna
Użytkownik autoryzował diagnozę i naprawę Ale/Lub. Zachowujemy priorytet polskiej
lokalizacji i limit monitorowania Actions 60 sekund łącznie na budowę.
W CKDT v3 rzeczywiście występują `Ale` (ranga 31) i `Lub` (59); nie obejmuje ich
dziewięciowpisowy sidecar. Historyczny preview-report przypisuje obu powód
proper-name-classification-from-linguistic-oracle. Morfeusz 1.99.15 / SGJP 2026.06.01
poświadcza zwykłe `ale:C/conj`, `ale:T/part`, `lub/conj` oraz formy nazw `Ale` od
`Ala` i `Lub` od `Luba:Sf`. Resolver dawał nazwom pierwszeństwo.

Nowa ogólna reguła po rzeczownikach pospolitych i przymiotnikach, a przed nazwami
własnymi i wtórnym źródłem NKJP, preferuje małą literę dla dokładnie poświadczonej
formy funkcyjnej: sonda małymi literami, identyczna forma, brak NAME, POS conj/comp/part/prep.
To reguła tagów gramatycznych, bez ręcznej listy wyjątków i opisów znaczeń.
Interpretacje nazw pozostają w raporcie. [Dokumentacja Morfeusza](https://morfeusz.sgjp.pl/doc/about/)
opisuje pozycję klasy gramatycznej w znaczniku; samą kolejność pierwszeństwa ustala projekt.

## 4. Rozwiązania odrzucone
Nie dodajemy blacklisty ale/lub w klawiaturze, nie zamieniamy wszystkich nazw na
małe litery i nie podmieniamy źródeł ręcznie. Nie osłabiamy kontraktu pierwotnego
build_variant_trial.py „CKDT bez zmian”: nowa korekta to osobny etap z własnym
raportem i hashem. Nie ma merge, release, tagu ani promocji trial do main.

## 5. Plan niewdrożony
Pełna regeneracja preview ze wszystkich źródeł; poszerzenie metadanych poza
dziewięć wpisów; kontekstowe porządkowanie wariantów z poprawną formą w top 3,
historią dłuższą niż dwa słowa i przyszłą interpunkcją. Inne lokalizacje nadal
odłożone do późniejszego przeglądu. Nie wdrożono nowego silnika AI/CTC.

## 6. Weryfikacja i granice
Lokalnie 29/29 testów producer PASS (21 istniejących, 8 nowych). Nowe sprawdzają
rzeczywiste homonimy Ale/Lub, dalsze wyrazy funkcyjne, nazwy Jan/Ala/Maria,
rzeczowniki/przymiotniki, odrzucenie sondy tylko z wielką literą, fragmentów,
NAME, skrótów i czasowników, kontrakt binarny, deterministyczny ZIP i checksumy.
Pełny historyczny v3 odtworzono z identycznym SHA. Dwukrotny build v4 dał
identyczny ZIP i raport. Niezależny od buildera przegląd wszystkich 106363 rekordów
potwierdził identyczne klucze, kolejność i rangi; header i wszystkie bajty za
sekcją kanoniczną są niezmienione. Unigrams i sidecar są identyczne bajtowo.
git diff --check PASS.

GitHub rozpoczął dwa runy tego samego producer commita: [37188544526](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37188544526)
i [37188542611](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37188542611).
W pojedynczym odczycie były in_progress; ich sukces NIE jest potwierdzony.
Nie czekamy na zakończenie i nie uruchamiamy pętli monitorującej. Workflow testuje,
buduje pack oraz porównuje raport z zatwierdzonym wzorcem. Telefon jeszcze nie
zweryfikował packa v4. Nie uruchamiano Android builda, bo kod APK nie zmienił się.

## 7. Gałęzie i historia
feature/source-variants-trial-v1: bieżący producer korekty. docs/source-variants-integration-v1:
bieżący runtime trial, draft PR #1. Oba mainy służą tu wyłącznie zapisowi ciągłości.
Historyczny preview a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307 / run 36916501466
pozostaje źródłem zamrożonego słownika; nie jest aktualnym pełnym rebuildem maina.

## 8. Artefakty, SHA i integracja
Lokalny wynik: cleverkeys-pl-function-words-trial.zip, pack version 4, 106363 wpisy,
18 korekt: ale, ani, chyba, ino, kiedy, lub, niechaj, oby, per, ponieważ, pono,
przeszło, skoro, tylko, wedle, wręcz, zgoła, żali. Bajty rangi nie zmieniają się.

SHA-256 ZIP v4: 3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af.
CKDT v4: 868548d23415d22d04a6f0c5580e5c26ae1a72d64a68359288aa4a1d761b4bd9.
ZIP v3: 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7.
CKDT v3: 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20.
Niezmieniony sidecar: e0a878249f021eff00eeb11165f600720f9d5fe24f383c9063e1b91c2a589a54.
Niezmieniony unigrams: de64baefedba0f4da8a4f50e41fa431a92dd3241133cd5825d965fe84e5818c0.
Świadectwo: [raport korekty](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f/docs/function-word-trial-v1/function-word-trial-report.json),
[specyfikacja i test telefonu](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f/docs/FUNCTION_WORD_CASING_TRIAL_V1.md).
CI ma wydać artifact cleverkeys-pl-function-words-trial; nie ma jeszcze potwierdzonego ID/hashu
artefaktu GitHub. Powyższe hashe są policzone lokalnie, a nie zgadywane z CI.

Importować nowy ZIP w istniejącym APK jako aktualizację polskiego pakietu.
Runtime 5200 ma już zielony run 37185565077 (3031 testów, lintDebug/lintVitalRelease,
kontrola fixed HIGH/CRITICAL). Ten wynik dotyczy APK; nie zastępuje testu nowego packa.

## 9. Ograniczenia i znane luki
Korekta zachowuje historyczne pochodzenie dziewięciu wpisów sidecara; jego provenance
opisuje źródłowy snapshot, a nie nowy hash całego CKDT. Raport oddzielnie podaje oba.
Osiem istniejących par, w tym Łódź/łódź, pozostaje bez zmian. Nowych par dla
wyrazów funkcyjnych nie dodano; ich homonimiczne nazwy można wpisać przez Shift
lub świadomą pisownię użytkownika. Istniejąca pisownia użytkownika może nadal
zmienić kolejność propozycji. Nie usuwamy jej automatycznie.
Poprawiono również resolver przyszłych buildów, ale nie wykonano pełnego pipeline preview.
Znane zgłoszenia Bun audit i pozostałe ograniczenia v9 pozostają opisane w poprzednim kamieniu.

## 10. Następny krok
Po zgłoszeniu zakończenia runów odczytać wyniki i hash/ID paczki. Następnie
zaimportować pack v4 na telefonie i sprawdzić środek zdania ale/lub/tylko/ponieważ,
dużą literę po kropce i przez Shift oraz zachowanie dotychczasowych par.
Nie budować nowego APK wyłącznie dla tej zmiany danych.

## 11. Różnica względem poprzedniego kamienia
[Stabilizacja CI](PROJECT_MILESTONE_2026-10-04_CI_STABILIZATION.md) zakończyła naprawę
lint i devalue oraz wskazała Ale/Lub jako następny etap. Ten kamień dowodzi przyczyny
w danych i kolejności reguł, dodaje ogólną poprawkę producer, odtwarzalny pack v4,
raport zmian i 8 regresji. Akceptacja telefonu i sukces nowego producer CI pozostają
otwarte; nie mylimy ich z już zielonym CI niezmienionego runtime.
