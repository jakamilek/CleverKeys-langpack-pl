# Audyt runtime CleverKeys pod kątem wariantów kapitalizacji — 2026-10-01

## Zakres

Sprawdzono przypięty runtime CleverKeys:

- repozytorium: `tribixbite/CleverKeys`
- przypięty SHA: `263bd0abc03dec420f60fa073a9d2c5e25a176b5`

Celem było ustalenie, czy można dołączyć dwa warianty powierzchni jednego klucza leksykalnego bez tworzenia dwóch niezależnych wpisów słownikowych.

## Wyniki

### 1. Słownik główny używa jednej tożsamości case-insensitive

`DictionaryDataSource.kt` ładuje z binarnego słownika znormalizowane klucze przez `NormalizedPrefixIndex`, a następnie emituje jedną powierzchnię kanoniczną przez `bestCanonical`.

Plik:
`src/main/kotlin/tribixbite/cleverkeys/DictionaryDataSource.kt`

Blob SHA:
`4e521e3878a87430e092a99fe7a4ea0ed0ea3669`

Wniosek: nie należy próbować osiągać dual-casing przez zwykłe dodanie `malina` i `Malina` do tego samego słownika.

### 2. Geometryczny ranking deduplikuje po lowercase

`CandidateRanker.rank()` wykonuje:

- sortowanie kandydatów po wyniku;
- następnie deduplikację przez `c.word.lowercase()`;
- zachowuje tylko najlepiej punktowanego przedstawiciela.

Plik:
`src/main/kotlin/tribixbite/cleverkeys/swipe/geometric/CandidateRanker.kt`

Blob SHA:
`9d4c6fdf53536a25c3ab9ed0ad120a9d12a93cb4`

Istotne linie w przypiętym SHA: 62–83.

Wniosek: nawet gdyby silnik chwilowo otrzymał oba warianty, obecna warstwa rankingu zredukowałaby je do jednego kandydata.

### 3. PredictionResult przenosi listę powierzchni, ale nie ma obecnie listy wariantów

Plik:
`src/main/kotlin/tribixbite/cleverkeys/PredictionResult.kt`

Blob SHA:
`3584ee89b0e0f9ebeb55dceb8a6112eae244e117`

Aktualny kontrakt zawiera:
- `words`
- `scores`
- opcjonalne `languages`

Nie zawiera metadanych typu:
`primarySurface / alternateSurfaces`.

To jest naturalny potencjalny seam („punkt wpięcia”) dla eksperymentalnej warstwy wariantów, ale najpierw należy sprawdzić konsekwencje wszystkich konsumentów `PredictionResult`.

### 4. Runtime już ma precedens dla przywracania kapitalizacji

`WordPredictor` przechowuje:

```
userWordOriginalCase[lowercase] = originalCase
```

Plik:
`src/main/kotlin/tribixbite/cleverkeys/WordPredictor.kt`

Blob SHA:
`dcb88266857b56003b4c7c1f3f1e763708718e33`

Istotne linie:
- 227–230: mapa `userWordOriginalCase`;
- 665–678: `applyUserWordCase()` i `applyUserWordCaseToList()`;
- 1918–1926: publiczne wejście do predykcji.

Obecna mapa jest jednak relacją:

```
jedno lower-case key -> jedna zapamiętana powierzchnia
```

czyli dokładnie nie wystarcza dla `malina -> malina + Malina`.

### 5. Swipe ma już wyraźnie oddzieloną warstwę prezentacji od rankingu

`SuggestionHandler.handleSwipePredictionResults()` otrzymuje listę predykcji i wyników, następnie:

1. przywraca istniejącą kapitalizację użytkownika;
2. stosuje Shift / auto-cap początku zdania;
3. może wykonać context rescoring;
4. buduje listę paska sugestii;
5. przekazuje ją do `SuggestionBar.setSuggestionsWithScores()`;
6. najwyższą sugestię automatycznie zatwierdza.

Plik:
`src/main/kotlin/tribixbite/cleverkeys/SuggestionHandler.kt`

Blob SHA:
`896bba5c7996fff21705129196f06a2e6dc9848b`

Istotne miejsca:
- 748–758: wejście `handleSwipePredictionResults()`;
- 779–795: `applyUserWordCaseToList` + auto-cap;
- 852–855: przekazanie listy do paska sugestii.

Wniosek: istnieje już osobna warstwa transformacji powierzchniowej po rankingu silnika. Jest to preferowane miejsce do eksperymentu, zamiast modyfikowania geometrii swipe.

### 6. Istniejąca polityka początku zdania jest odrębna

Runtime rozróżnia:

- zapamiętane przypadki kapitalizacji słów użytkownika;
- jawny Shift / Caps Lock;
- automatyczną kapitalizację początku zdania.

To potwierdza przyjętą w projekcie zasadę, że `malina/Malina` nie należy utożsamiać z regułą początku zdania.

## Wymagana architektura eksperymentalna

Najmniejsza sensowna zmiana powinna zachować obecny ranking:

```
gesture
  -> lexical ranking (jeden key)
  -> surface-variant resolver
  -> suggestion bar
```

Warstwa resolvera ma możliwość dla jednego klucza zwrócić np.:

```
malina
  primary: Malina
  alternate: malina
```

albo odwrotnie.

Ranking leksykalny nie może otrzymać dwóch kopii tego samego klucza.

## Lokalna personalizacja

Istniejąca koncepcja `userWordOriginalCase` może być wykorzystana jako punkt wyjścia, ale model docelowy musi dopuszczać co najmniej dwa warianty i preferencję licznikową, np.:

```
malina:
  lowercase: 156
  capitalized: 87
```

Preferencja nie powinna przeskakiwać po pojedynczym zdarzeniu. Dokładne parametry uczenia mają zostać ustalone eksperymentalnie.

## Pierwsze przypadki testowe

- `malina / Malina`
- `łódź / Łódź`
- `warszawa / Warszawa`

Kontrolnie:
- `bardo` nie jest obecnie kandydatem ścisłego audytu dual-casing, ponieważ konkurencyjna analiza właściwa jest tylko nazwiskowa.

## Granice eksperymentu

Nie należy jeszcze:

- zmieniać immutable 100k;
- dodawać drugiego wpisu do CKDT dla tej samej tożsamości case-insensitive;
- modyfikować geometrii swipe;
- zmieniać globalnego rankingu słów;
- stosować zasady `proper > common`;
- obejmować automatycznie wszystkich 1702 kandydatur.

## Dostęp do runtime

Przypięte repozytorium `tribixbite/CleverKeys` jest obecnie dostępne przez połączenie GitHub tylko z uprawnieniem odczytu. Nie można bezpośrednio utworzyć gałęzi ani zapisać eksperymentalnej zmiany w tym repozytorium.

Dlatego w repozytorium języka zapisano architekturę i audyt, natomiast właściwa zmiana kodu runtime powinna zostać wykonana w forkowanym repozytorium CleverKeys, gdy będzie ono dostępne z prawem zapisu.

## Aktualny wniosek

Runtime potwierdza wcześniejszą decyzję:

- jedna tożsamość leksykalna;
- warianty powierzchni jako osobna warstwa;
- ranking przed rozstrzygnięciem powierzchni;
- lokalna preferencja użytkownika;
- drugi wariant łatwo dostępny z paska sugestii.

Najmniejszy eksperyment powinien powstać po stronie runtime, a nie w generatorze polskiego słownika.
