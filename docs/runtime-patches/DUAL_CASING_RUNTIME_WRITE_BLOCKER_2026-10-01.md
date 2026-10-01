# Dual-casing runtime — stan integracji 2026-10-01

## Właściwe repozytorium runtime

Eksperyment dual-casing pracuje na forku użytkownika:

`jakamilek/CleverKeys-animated-gif`

Nie używać `tribixbite/CleverKeys` jako miejsca zmian roboczych i nie używać tego repo jako substytutu właściwego forka.

## Wymagany baseline eksperymentu

Dokładny baseline runtime:

`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

Aktualny `main` forka:
`5b66db1b1edc6a563a546aa0f7f299299f02dd5e`

GitHub compare potwierdza:
- `main` jest 14 commitów do przodu;
- `main` nie jest równocześnie wymaganym baseline eksperymentu;
- eksperyment powinien być utworzony od przypiętego SHA, bez automatycznego włączania tych 14 późniejszych commitów.

## Stan gałęzi

Na forku istnieje obecnie tylko:
- `main`

Próba utworzenia:
`exp/dual-casing-2026-10-01`

bezpośrednio od:
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

została odrzucona przez aktualne połączenie GitHub błędem:

`403 Resource not accessible by integration`

Ponowienie przez aktualizację refu dało ten sam `403`.

Odczyt repozytorium działa prawidłowo. Metadane repozytorium raportują uprawnienie `push=true`, ale bieżący konektor nie pozwala wykonać operacji tworzenia/aktualizacji refu.

### Czego NIE robimy

- nie zapisujemy eksperymentu bezpośrednio do `main`;
- nie zaczynamy eksperymentu od `5b66db1...`;
- nie scalujemy 14 późniejszych commitów do baseline;
- nie przenosimy eksperymentu do innego forka.

## Potwierdzony punkt wpięcia runtime

Na przypiętym SHA potwierdzono:

### CandidateRanker

`src/main/kotlin/tribixbite/cleverkeys/swipe/geometric/CandidateRanker.kt`

Ranker sortuje kandydatów, następnie deduplikuje przez:

`c.word.lowercase()`

Wniosek:
- `malina` i `Malina` nie mogą być dwoma zwykłymi kandydatami rankera;
- warianty muszą być dodane dopiero po rankingu.

### SuggestionHandler

`src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt`

W `handleSwipePredictionResults()` kolejność jest obecnie:
1. przywrócenie zapamiętanej kapitalizacji użytkownika;
2. auto-cap początku zdania / Shift / Caps Lock;
3. context rescoring;
4. augment posessivów;
5. budowa metadanych;
6. `suggestionBar.setSuggestionsWithScores(...)`;
7. automatyczne zatwierdzenie pierwszej sugestii.

Docelowy eksperyment powinien zachować ranking i auto-wstawianie top-candidate, a wariant alternatywny dodać dopiero na warstwie prezentacji.

### SuggestionBar

`src/main/kotlin/tribixbite/cleverkeys/SuggestionBar.kt`

Wire pozostaje:
- `List<String>`
- równoległe `List<Int>`
- równoległe `List<SuggestionMeta>`

Kliknięcie sugestii przekazuje dokładnie aktualny tekst z danego slotu do `onSuggestionSelected()`.

Wniosek:
- alternatywna powierzchnia może być prezentowana jako osobny slot paska;
- tap na alternatywę może przejść istniejącą ścieżką wyboru;
- nie ma potrzeby wprowadzania dwóch case-variantów do rankera.

## Stan eksperymentalnej logiki

Istnieje już czysty resolver:

`src/main/kotlin/tribixbite/cleverkeys/casing/CaseVariantResolver.kt`

oraz test:

`src/test/kotlin/tribixbite/cleverkeys/casing/CaseVariantResolverTest.kt`

Przygotowany jako patch w:
`docs/runtime-patches/DUAL_CASING_RUNTIME_PATCH_2026-10-01.patch`

Sam resolver przeszedł niezależny self-test:
`CASE_VARIANT_RESOLVER_SELFTEST=PASS`

Testowane przypadki:
- `malina/Malina`
- `warszawa/Warszawa`
- próg 5 użyć;
- przewaga 2 użyć;
- brak oscylacji przy równych danych;
- odrzucenie różnych kluczy;
- odrzucenie eksperymentalnej formy ALL CAPS.

## Następny bezpieczny krok

Po uzyskaniu działającej możliwości zapisu do forka:
1. utworzyć `exp/dual-casing-2026-10-01` od dokładnego SHA `263bd0...`;
2. uruchomić wyłącznie test czystego resolvera;
3. dodać minimalną projekcję wariantu do paska sugestii bez zmian rankera, słownika i geometrii;
4. przetestować tap alternatywy;
5. dopiero potem dodać lokalne uczenie preferencji.

Do czasu usunięcia blokady zapisu nie wolno udawać, że runtime został zmodyfikowany.
