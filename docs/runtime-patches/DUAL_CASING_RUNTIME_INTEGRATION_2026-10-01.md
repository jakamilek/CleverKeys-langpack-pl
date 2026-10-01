# Dual-casing runtime integration experiment — 2026-10-01

## Stan

Eksperyment jest prowadzony jako patch w `jakamilek/CleverKeys-langpack-pl`.

Runtime reference baseline:
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

Project experiment branch:
`exp/dual-casing-runtime-2026-10-01`

Gałąź eksperymentalna nie zmienia `main`.

## Etap 1 — czysty resolver

Gotowy i wcześniej zweryfikowany:
- jedna tożsamość case-insensitive;
- dwa warianty powierzchni;
- minimalny próg 5 użyć;
- przewaga 2 użyć;
- brak oscylacji przy równych danych.

## Etap 2 — projekcja paska

**Obowiązujący patch integracyjny V2:**
`docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_V2_PATCH_2026-10-01.patch`

Blob SHA patcha:
`a771440c28d235c08256fa72f2d237521502bbd4`

Poprzedni:
`docs/runtime-patches/DUAL_CASING_RUNTIME_INTEGRATION_PATCH_2026-10-01.patch`

jest **SUPERSEDED ("zastąpiony")** i nie należy go nakładać. Pozostaje w repozytorium wyłącznie jako ślad wcześniejszej wersji eksperymentu.

V2 zawiera:
- `CaseVariantExperiment` — trzy kontrolowane przypadki: `malina/Malina`, `łódź/Łódź`, `warszawa/Warszawa`;
- `CaseVariantCatalog` — mapowanie jednego klucza na warianty;
- `CaseVariantPreferenceTracker` — tymczasowe uczenie in-memory wyłącznie dla katalogu eksperymentalnego;
- `CaseVariantProjector` — pozycjonowanie `primary + alternate` z tym samym score ("wynikiem") i wskaźnikiem źródłowego kandydata;
- testy logiki projekcji, preferencji oraz progu 5 + 2.

### Kolejność runtime

Projekcja dual-casing jest przewidziana:
1. po rankingu silnika;
2. po przygotowaniu danych ML;
3. **przed auto-insert top prediction**;
4. następnie ten sam stan prezentacji pozostaje na pasku sugestii.

Dzięki temu:
- alternatywna powierzchnia nie staje się drugim kandydatem leksykalnym;
- ranking silnika pozostaje niezmieniony;
- wybrana preferencja może zmienić tylko powierzchnię prezentowaną jako primary;
- auto-insert korzysta z aktualnej primary;
- oba warianty pozostają dostępne na pasku.

### Kapitalizacja początku zdania

Dual-casing jest wyłączony dla:
- aktywnego Shift;
- Caps Lock;
- aktywnego sentence-start autocap ("automatycznej kapitalizacji początku zdania").

Te mechanizmy pozostają niezależne i nie są używane jako sygnał preferencji leksykalnej.

### Uczenie

- ręczny wybór wariantu jest sygnałem preferencji;
- obserwacja auto-insert primary jest dopuszczona tylko bez Shift/Caps/auto-cap;
- oba kanały uczenia respektują istniejące bramki `LearningGate` i `fieldAllowsPersonalizedLearning`;
- tracker jest wyłącznie in-memory w tym eksperymencie;
- trwałe przechowywanie zostanie zaprojektowane dopiero po walidacji pierwszego eksperymentu.

## Weryfikacja

### Czysta logika Kotlin/JVM

Uruchomiony ponownie czysty test host-JVM:
`CASE_VARIANT_HOST_JVM_SELFTEST=PASS`

Zakres:
- `malina` -> `malina`, `Malina`;
- wyuczona preferencja kapitalizowana -> `Malina`, `malina`;
- `łódź` i `warszawa`;
- `bardo` pozostaje bez dodatkowego wariantu;
- próg 5 obserwacji + przewaga 2;
- zachowanie source-index.

To jest test logiki host-JVM, **nie** test Android/Gradle ani test pełnego runtime.

### Zgodność patcha z przypiętym runtime

Na dokładnym pliku:
`tribixbite/CleverKeys/src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt`

dla SHA:
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

zweryfikowano wszystkie **7 kontekstów hunks** patcha V2. Każdy blok starego kontekstu występuje w pliku bazowym.

Dodatkowo:
- brak błędnych markerów typu `+@@`;
- brak linii `++import`;
- brak nieprefiksowanych linii w sekcjach `Add File`.

Nie wykonano jeszcze rzeczywistego `git apply` + Android/Gradle build na checkoutcie runtime, ponieważ zapis do repozytorium runtime nie jest obecnie potwierdzony jako dostępny.

## Aktualny stan aplikacji klawiatury

**Actual runtime source / APK: UNCHANGED ("bez zmian").**

Nie zmodyfikowano:
- `tribixbite/CleverKeys`;
- `CandidateRanker`;
- `PredictionResult`;
- `SuggestionBar`;
- `SuggestionHandler` w repo runtime;
- geometrii swipe;
- `main`.

Patch V2 jest wyłącznie zapisanym eksperymentem/specyfikacją w repozytorium pakietu językowego.

Zweryfikowane repozytoria użytkownika obejmują:
- `jakamilek/CleverKeys-langpack-pl` — właściwe repo projektu pakietu językowego;
- `jakamilek/CleverKeys-animated-gif` — repo odrębnego eksperymentu GIF, **nie** jest repo runtime dla dual-casing.

Brak potwierdzonego zapisu do właściwego repo runtime pozostaje ograniczeniem eksperymentu.

## Następny etap

1. Uzyskać potwierdzony zapis do właściwego repo runtime albo pozostawić runtime jako reference-only.
2. Na checkoutcie dokładnego SHA `263bd0...` uruchomić rzeczywisty `git apply`, `runPureTests` i build/test Android.
3. Dopiero po green przejść do minimalnego testu paska i wyboru wariantu.
4. Dopiero później zaprojektować dostarczanie katalogu wariantów z generatora/CKDT.

## Ograniczenia

- brak zmian immutable 100k;
- brak zmian membership modułów;
- brak zmian `CandidateRanker`;
- brak zmian geometrii swipe;
- brak zmian `main`;
- brak traktowania dwóch wariantów jako dwóch niezależnych kandydatów;
- brak trwałego przechowywania preferencji w tej wersji eksperymentu.
