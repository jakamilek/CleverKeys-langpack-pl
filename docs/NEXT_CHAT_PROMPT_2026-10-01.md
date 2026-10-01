# NEXT CHAT PROMPT — CleverKeys PL / dual-casing runtime — 2026-10-01

Kontynuuj istniejący projekt CleverKeys Polish Language Pack. NIE zaczynaj od zera.

## Oficjalny baseline

- repo: `jakamilek/CleverKeys-langpack-pl`
- branch: `ops/baseline-sync-2026-09-20`
- GitHub jest jedynym oficjalnym baseline.
- Nie zakładaj istnienia lokalnych zmian.
- Nie wykonuj merge/promote do `main`.
- Zmiany zapisuj małymi, atomowymi commitami.

Runtime:
- repo: `tribixbite/CleverKeys`
- przypięty SHA: `263bd0abc03dec420f60fa073a9d2c5e25a176b5`
- obecne połączenie GitHub do runtime ma tylko `pull`, bez `push`; właściwy eksperyment kodowy wymaga forka z prawem zapisu albo innego połączenia do repo użytkownika.

## Decyzja architektoniczna dual-casing

Chcemy obsłużyć prawdziwą homonimię kapitalizacyjną bez zmiany immutable 100k i bez tworzenia dwóch zwykłych wpisów różniących się wyłącznie wielkością liter.

Przykłady:
- `malina` / `Malina`
- `łódź` / `Łódź`
- `warszawa` / `Warszawa`

Model:
1. jedna tożsamość leksykalna, np. `malina`;
2. osobne warianty powierzchni, np. `malina`, `Malina`;
3. ranking leksykalny wybiera jeden klucz;
4. dopiero potem resolver powierzchni wybiera wariant główny i alternatywny;
5. lokalne uczenie użytkownika preferencji wariantu;
6. oba warianty mają pozostać łatwo osiągalne z paska sugestii.

Nie stosować reguły `proper > common`.
Nie robić wyjątku tylko dla Warszawy.
Nie zmieniać membership immutable 100k.
Nie obejmować od razu wszystkich 1702 ścisłych kandydatur.

## Audyt Morfeusz / SGJP

Ścisły audyt immutable 100k:
- wynik: **1702** kandydatur;
- common side: `subst:sg:nom` + `nazwa_pospolita` lub `nazwa pospolita`;
- proper side: `subst:sg:nom` + dowolna niepospolita klasa NAME;
- inflected forms wykluczone;
- moduły nie były używane.

Dokument:
`docs/CORE_DUAL_CASING_CLASS_AUDIT_2026-10-01.md`

Ważne przykłady:
- `warszawa`: common + `nazwa_geograficzna | nazwisko`;
- `łódź`: common + `nazwa_geograficzna`;
- `malina`: common + `imię | nazwa_geograficzna | nazwisko`;
- `bardo`: poza ścisłym zbiorem, bo właściwa konkurencja jest tylko `nazwisko`.

Podział 1702:
- 1173 tylko `nazwisko`;
- 254 `nazwisko` + inna klasa;
- 253 bez `nazwisko`, z bezpośrednią klasą leksykalną;
- 22 tylko `człon_*`.

## Audyt runtime

Dokument:
`docs/CLEVERKEYS_RUNTIME_DUAL_CASING_AUDIT_2026-10-01.md`

Przypięty runtime potwierdził:

### `CandidateRanker`
Plik:
`src/main/kotlin/tribixbite/cleverkeys/swipe/geometric/CandidateRanker.kt`
Blob SHA:
`9d4c6fdf53536a25c3ab9ed0ad120a9d12a93cb4`

Ranking deduplikuje kandydatów przez `c.word.lowercase()`, więc dwa warianty nie mogą być zwykłymi równorzędnymi kandydatami rankera.

### `PredictionResult`
Plik:
`src/main/kotlin/tribixbite/cleverkeys/PredictionResult.kt`
Blob SHA:
`3584ee89b0e0f9ebeb55dceb8a6112eae244e117`

Kontrakt ma:
- `words`
- `scores`
- opcjonalne `languages`

Nie ma jeszcze warstwy wariantów powierzchni.

### `WordPredictor`
Plik:
`src/main/kotlin/tribixbite/cleverkeys/WordPredictor.kt`
Blob SHA:
`dcb88266857b56003b4c7c1f3f1e763708718e33`

Istnieje:
- `userWordOriginalCase`: lower-case key -> jedna zapamiętana powierzchnia;
- `applyUserWordCase()`;
- `applyUserWordCaseToList()`.

To jest ważny precedens, ale obecny model obsługuje tylko JEDEN wariant dla klucza.

### `SuggestionHandler`
Plik:
`src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt`
Blob SHA:
`896bba5c7996fff21705129196f06a2e6dc9848b`

Swipe flow:
- 748–758: `handleSwipePredictionResults()`;
- 779–795: istniejące przywracanie kapitalizacji użytkownika + auto-cap;
- 852–855: `setSuggestionsWithScores()`;
- top suggestion jest następnie automatycznie zatwierdzany.

To jest preferowany punkt wpięcia nowego resolvera powierzchniowego.

## Kolejność następnych prac

1. Uzyskać fork/runtime branch z prawem zapisu, oparty dokładnie na `263bd0abc03dec420f60fa073a9d2c5e25a176b5`.
2. Dodać minimalny eksperyment runtime, bez zmian słownika PL:
   - jeden klucz;
   - dwa warianty powierzchni;
   - zachowanie jednego rankowanego klucza;
   - prezentacja primary + alternate;
   - wybór alternatywy z paska;
   - test lokalnego preferowania wariantu.
3. Najpierw testy jednostkowe czystej logiki resolvera; dopiero potem test integracyjny paska/sugestii.
4. Przetestować `malina/Malina`, `łódź/Łódź`, `warszawa/Warszawa`.
5. Dopiero po udanym eksperymencie zaprojektować format danych po stronie generatora/CKDT.

## Najważniejsze ograniczenia

- nie modyfikować immutable 100k;
- nie zmieniać membership modułów;
- nie modyfikować geometrii swipe;
- nie dodawać dwóch case-variantów do rankera jako osobnych kandydatów;
- nie traktować `PN` z NKJP ani samej klasy proper jako automatycznego uppercase;
- nie mylić homonimii leksykalnej z kapitalizacją początku zdania.

Stan zapisany w GitHub:
- decyzja architektoniczna: `docs/DUAL_CASING_RUNTIME_DESIGN_2026-10-01.md`;
- audyt runtime: `docs/CLEVERKEYS_RUNTIME_DUAL_CASING_AUDIT_2026-10-01.md`;
- audyt 1702: `docs/CORE_DUAL_CASING_CLASS_AUDIT_2026-10-01.md`.

## Aktualizacja 2026-10-01 — repozytorium robocze potwierdzone

Użytkownik potwierdził, że jedynym właściwym repozytorium roboczym projektu jest:
`jakamilek/CleverKeys-langpack-pl`.

Nie należy próbować używać `jakamilek/CleverKeys-animated-gif` ani żadnego innego forka użytkownika.

Gałąź eksperymentalna dla bieżącego etapu:
`exp/dual-casing-runtime-2026-10-01`

została utworzona z oficjalnej gałęzi:
`ops/baseline-sync-2026-09-20`.

Runtime CleverKeys pozostaje źródłem referencyjnym od przypiętego SHA
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`, ale artefakty eksperymentu runtime są w tym projekcie przechowywane jako patch/specyfikacja do czasu ich zastosowania w odpowiednim źródle runtime. Nie należy twierdzić, że kod runtime został zmodyfikowany, jeśli zmiana istnieje tylko jako patch.



## Aktualizacja 2026-10-01 — badanie dwutorowe: pakiet PL + aplikacja

Bieżące badanie ma dwa równoległe, wzajemnie zależne tory:

### Tor A — pakiet językowy
- repo: `jakamilek/CleverKeys-langpack-pl`
- branch: `ops/baseline-sync-2026-09-20`
- commit źródłowy ostatniego zweryfikowanego buildu: `a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307`
- ostatni preview: workflow `Polish language pack preview`, run `382`, zakończony `success`
- artifact: `cleverkeys-pl-preview`, GitHub artifact id `11189614575`
- SHA-256 archiwum artifactu: `827a20f8489fad51023e1c0d58319dca030d304f7e213ef4973141251c3ad9ff`
- wewnętrzny pakiet CKDT: SHA-256 `301b0b9c7c4c7b96ac7a2545bf27745b6ee38c87f5d04133ede490008d861945`
- manifest CKDT: `wordCount=106363`, `version=2`, `hasPrefixBoost=false`
- audyt: immutable core = 100000; module-only = 6363; registry conflicts = 0; capitalization violations = 0
- poprawka w `scripts/audit_capitalization_common_noun_homonyms.py` zachowuje oficjalne powierzchnie nazw z łącznikiem; nie jest wyjątkiem dla jednej nazwy.

Stary `CleverKeys-PL-size-100k-final.zip` jest artefaktem historycznym i nie jest bazą bieżącego benchmarku.

### Tor B — aplikacja/runtime
- repo robocze: `jakamilek/CleverKeysPL`
- branch: `exp/context-reranking-runtime-2026-10-01`
- dokładna baza: `263bd0abc03dec420f60fa073a9d2c5e25a176b5`
- aktualny HEAD po poprawce builda i pomocniczej konfiguracji eksperymentalnej: `a290afac1aca086224d3c54c838a95f073eb9a3b`
- porównanie z pinned runtime: 7 commitów ahead, 0 behind
- eksperyment capture nie zmienia rankingu produkcyjnego; zapisuje `decoder_candidates` przed casingiem, context rerankingiem i augmentation.
- błąd ostatniego builda APK (run `36915350017`) był jednoznaczny: `SuggestionHandler.kt:782:9 Unresolved reference 'swipeData'`.
- poprawka: commit `97aa20c04357fcead23bba32ef8b28e8ccaee1a1` pobiera `inputCoordinator.getCurrentSwipeData()` przed rerankingiem i używa tego samego obiektu dalej.
- poprzedni build zatrzymał się na `compileDebugKotlin`; `clean`, generowanie ikon i wcześniejsze zadania Gradle przeszły poprawnie.
- pełna kompilacja poprawionego runtime nie została jeszcze potwierdzona przez nowy GitHub Actions run; lokalna próba była niemożliwa z powodu braku rozwiązywania DNS dla GitHuba w środowisku roboczym.
- dodano eksperymentalny workflow `.github/workflows/experimental-runtime-build.yml`; GitHub nie utworzył dotąd runu dla tej gałęzi, więc nie traktować tego jako zielonego CI.

### Zasada powiązania obu torów
Benchmark kontekstowy ma korzystać z pakietu wygenerowanego z aktualnego, zweryfikowanego commitu toru A oraz z dokładnie określonego runtime/candidate-set capture z toru B. Nie mieszać starego ZIP-a z nowym runtime bez jawnego oznaczenia artefaktu i provenance.

## Reguła nadrzędna: ZERO DOMYSŁÓW

Obowiązuje `docs/PROJECT_RULE_NO_GUESSING_2026-10-01.md`.

**NIE WOLNO ZGADYWAĆ.** Informacji niepotwierdzonych w aktualnym GitHub, obowiązującym handoffie/promptcie albo wprost przez użytkownika nie wolno uzupełniać przez skojarzenie, podobieństwo, pamięć modelu ani prawdopodobieństwo.

Przed każdą operacją zależną od repozytorium, gałęzi, SHA, pliku, statusu CI lub decyzji projektowej należy ją zweryfikować. Przy konflikcie informacji trzeba ustalić stan z aktualnego GitHub HEAD; przy braku możliwości weryfikacji informacja pozostaje **NIEZNANA** i nie wolno wykonywać zależnej od niej operacji.

Innego repozytorium, forka lub gałęzi nie wolno traktować jako zamiennika tylko dlatego, że nazwa lub zawartość są podobne. Pamięć rozmowy może wskazać, co sprawdzić, ale nie zastępuje weryfikacji.

