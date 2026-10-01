# Dual-casing runtime integration experiment — 2026-10-01

## Stan

Eksperyment jest prowadzony jako patch w `jakamilek/CleverKeys-langpack-pl`.

Runtime reference baseline:
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

Project experiment branch:
`exp/dual-casing-runtime-2026-10-01`

## Etap 1 — czysty resolver

Gotowy i wcześniej zweryfikowany:
- jedna tożsamość case-insensitive;
- dwa warianty powierzchni;
- minimalny próg 5 użyć;
- przewaga 2 użyć;
- brak oscylacji przy równych danych.

## Etap 2 — projekcja paska

Patch:
`docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_PATCH_2026-10-01.patch`

Dodane elementy:
- `CaseVariantExperiment` — trzy kontrolowane przypadki: `malina/Malina`, `łódź/Łódź`, `warszawa/Warszawa`;
- `CaseVariantCatalog` — mapowanie jednego klucza na warianty;
- `CaseVariantPreferenceTracker` — tymczasowe uczenie in-memory wyłącznie dla katalogu eksperymentalnego;
- `CaseVariantProjector` — po rankingu tworzy `primary + alternate`, z tym samym score i wskaźnikiem źródłowego kandydata;
- testy czystej logiki projekcji i uczenia.

### Ważna kolejność runtime

Projekcja dual-casing jest przewidziana dopiero po:
- rankingu;
- ML capture;
- auto-insert top prediction.

Dzięki temu alternatywna powierzchnia nie jest traktowana jako drugi kandydat silnika i nie trafia do rankingu leksykalnego.

### Kapitalizacja początku zdania

Dual-casing jest wyłączony dla:
- aktywnego Shift;
- Caps Lock;
- aktywnego sentence-start autocap.

Te mechanizmy pozostają niezależne i nie są używane jako sygnał preferencji leksykalnej.

### Uczenie

- ręczny wybór wariantu jest czystym sygnałem preferencji;
- auto-insert primary może być obserwacją tylko bez Shift/Caps/auto-cap;
- preference tracker jest wyłącznie in-memory w eksperymencie;
- trwałe przechowywanie zostanie zaprojektowane dopiero po walidacji pierwszego eksperymentu.

## Weryfikacja

Lokalna kompilacja czystych klas Kotlin/JVM zakończona:
`DUAL_CASING_INTEGRATION_LOGIC_SELFTEST=PASS`

Zakres tego testu:
- `malina` -> `malina`, `Malina`;
- learned capitalized preference -> `Malina`, `malina`;
- `łódź` i `warszawa`;
- zachowanie `bardo` bez dodatkowego wariantu;
- próg 5 + lead 2;
- source-index duplication.

Nie wykonano jeszcze projektu Android/Gradle ani testu instrumentowanego paska. Nie należy tego nazywać testem runtime.

## Następny etap

1. Zweryfikować patch syntaktycznie na dokładnym checkoutcie runtime SHA `263bd0...`.
2. Uruchomić `runPureTests` dla nowych testów.
3. Dopiero po green przejść do minimalnego testu paska/suggestion selection.
4. Po walidacji zaprojektować sposób dostarczenia katalogu wariantów z generatora/CKDT.

## Ograniczenia

- brak zmian immutable 100k;
- brak zmian membership modułów;
- brak zmian `CandidateRanker`;
- brak zmian geometrii swipe;
- brak zmian `main`;
- brak traktowania dwóch wariantów jako dwóch niezależnych kandydatów.