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
