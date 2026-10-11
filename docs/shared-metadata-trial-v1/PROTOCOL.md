# Współdzielone metadane źródłowe v9

Zmiana dotyczy reprezentacji zaakceptowanej na telefonie paczki v8. Zachowujemy
wszystkie 190 813 słów, rangi, warianty pisowni, dane źródłowe i unigrams.txt.
Nie dodajemy słów ani znaczeń i nie usuwamy wpisów. Prywatny eksport nie jest
źródłem ani listą wyjątków; jego końcowe porównanie pozostaje osobnym zadaniem.

Bazą jest wewnętrzny ZIP z udanego runu [38167348861](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38167348861),
SHA-256 `0362cf38e06d821af96947104f7f714bfb63e9ea2ddf505ec466bc29140001f7`.
Skrypt `build_shared_metadata_trial.py` przypina również sumę metadanych v8.
Odtworzenie starego dokumentu musi być identyczne bajt po bajcie przed zapisaniem
jakiegokolwiek instalowalnego ZIP-a. Metadane dawnych pełnych dowodów pozostają
nietknięte. Nie zgadujemy rdzeni ani końcówek.

## Format i odczyt

Manifest v9 deklaruje API2 i schemaVersion2. Wymaga nowego zgodnego APK;
stare APK odrzuca format. Nowy czytnik nadal obsługuje v1. Kolejność pól głównych:
`schemaVersion`, `languageCode`, `sourceAttributes`, `sourceLexemes`, `provenance`,
`entries`. Tabele poprzedzają słowa, a atrybuty poprzedzają rekordy źródłowe.

Powtarzający się rekord przechowujemy raz tylko wtedy, gdy daje oszczędność węzłów.
Tożsamość obejmuje dokładny lemat, sufiks źródłowy, część mowy, klasy NAME,
etykiety LABELS i obecność pól. Brak pola i pusta lista pozostają różne.
Pisownia `surfaces` zostaje przy konkretnym słowie. Wpis odsyłający ma
`sourceRef` i `surfaces`; unikatowe rekordy pozostają lokalne. `sourceAttributesRef`
może współdzielić identyczny komplet klas i etykiet zarówno dla rekordu tabeli,
jak i lokalnego odczytania. Odwołania są indeksami całkowitymi; konflikty,
niepoprawne indeksy i powielone definicje są odrzucane.

Czytnik strumieniowy zachowuje zwarte dane i niezmienne tożsamości lemat/POS
wykorzystywane przez istniejącą SI. Pełny `metadataJson` odtwarza się na żądanie
dla pojedynczego słowa, bez zapisywania rozwiniętego całego słownika w RAM.
Limity importu pozostają: 32 MiB, 2M węzłów, 120K wpisów, 16K węzłów na fragment,
głębokość32, hashe, duplikaty i bezpieczna podmiana. Tabele łącznie mają własny
limit120K rekordów. Koszt rozwiniętego wpisu sprawdzamy przed kopiowaniem.

## Wynik i bramki

| Pomiar | v8 | v9 |
|---|---:|---:|
| Słowa | 190 813 | 190 813 |
| Wpisy metadanych | 100 649 | 100 649 |
| Bajty metadanych | 30 456 556 | 26 141 080 |
| Węzły JSON | 1 999 993 | 1 740 933 |

Zyskujemy259 060 węzłów i4 315 476 bajtów nieskompresowanych metadanych.
Pozostaje259 067 węzłów do limitu. Nie jest to gwarancja konkretnej liczby nowych
słów: nadal obowiązują limity bajtów i wpisów. Kompresja ZIP może dać nieco
większy plik; nie deklarujemy spadku RAM Androida ani pamięci modelu HerBERT.

Lokalnie:71 testów producenta i28 rzeczywistych testów parsera Kotlin PASS.
Pełne porównanie CKDT i100 649 rozwiniętych widoków metadanych oraz tożsamości
źródłowych PASS; rzeczywista prezentacja form i kapitalizacji bez zmian.
Osobne JVM: zimny v9, v8→v9 i ponowne v9, każdy z16 MiB balastu przy192 MiB,
PASS. To bramki regresji hosta, nie pomiar PSS telefonu ani trafności SI.

Konsument: `jakamilek/CleverKeysPL@64943d82e4480c3e2afb5e3618a5e4e47fa4c6ff`.
Workflow przypina commit konsumenta i odtwarza [reviewed-report.json](reviewed-report.json)
przed przesłaniem artefaktu. Android, MockK importu, lint, rzeczywiste artefakty CI,
instalacja i próby telefonu pozostają do potwierdzenia. Po udanym CI dostarczamy
najpierw APK, następnie wewnętrzny ZIP do importu. Nie ma merge, tagu ani wydania;
monitorowanie Actions do60 sekund łącznie na run.

Paczka: `cleverkeys-pl-shared-metadata-trial.zip`, SHA-256
`c1ffdac5ef607f183996abf6a4804490a0b5c43c39b6d4215975936062ba8677`.
