# Eksperymentalna warstwa wariantów kapitalizacji — 2026-10-01

## Cel

Rozwiązać homonimię kapitalizacyjną bez zmiany 100 000-kluczowego rdzenia i bez dokładania dwóch zwykłych wpisów różniących się wyłącznie wielkością liter.

Przykłady docelowe:

- `malina` / `Malina`
- `łódź` / `Łódź`
- `warszawa` / `Warszawa`

Problem jest przede wszystkim kontekstowy: sam słownik nie zna pełnego zdania ani intencji użytkownika. Dlatego rozdzielamy rozpoznanie leksykalne od wyboru powierzchni zapisu.

## Decyzja architektoniczna

### 1. Jedna tożsamość leksykalna

Dla klucza case-insensitive istnieje jedna tożsamość leksykalna:

```
key: malina
```

Nie tworzymy dwóch niezależnych wpisów:

```
malina
Malina
```

w tej samej warstwie słownikowej, ponieważ obecny runtime CleverKeys traktuje klucze case-insensitive i deduplikuje takie powierzchnie.

### 2. Osobna lista wariantów powierzchni

Tożsamość leksykalna może mieć przypisane warianty zapisu:

```
key: malina
variants:
  - malina
  - Malina
```

Warianty są metadanymi projekcji powierzchniowej, a nie drugim członkostwem w rdzeniu.

### 3. Morfeusz jako dowód lingwistyczny

Dla kandydatury warstwa audytu zachowuje niezależne analizy Morfeusza/SGJP, np.:

```
malina
  common: nazwa_pospolita
  proper: imię | nazwa_geograficzna | nazwisko
```

Nie tworzymy na tej podstawie automatycznej reguły typu „nazwa własna zawsze wygrywa”. Klasy służą do identyfikacji i kwalifikacji kandydatur.

### 4. Ranking leksykalny i wybór powierzchni są rozdzielone

Przepływ:

```
swipe
  -> kandydat leksykalny: malina
  -> ranking leksykalny
  -> wybór wariantu powierzchni
  -> sugestia główna + alternatywna
```

Czyli najpierw odpowiadamy na pytanie „jakie słowo użytkownik prawdopodobnie wpisał?”, a dopiero potem „jak zapisać jego powierzchnię?”.

## Personalizacja użytkownika

Preferowany wariant może być uczony lokalnie przez runtime.

Przykład użytkownika używającego owocu:

```
malina:
  lowercase = 156
  capitalized = 87
```

Preferowana powierzchnia: `malina`.

Przykład użytkownika często piszącego o osobie o imieniu Malina:

```
malina:
  lowercase = 12
  capitalized = 87
```

Preferowana powierzchnia: `Malina`.

Oba warianty pozostają dostępne.

### Zasady uczenia

Nie zmieniamy preferencji po jednym użyciu.

Mechanizm powinien używać co najmniej:

- progu lub miękkiego narastania preferencji;
- możliwości wyhamowania wpływu pojedynczej pomyłki;
- okresowego wygaszania starszych obserwacji lub innego mechanizmu zapobiegającego trwałemu zablokowaniu preferencji.

Dokładne parametry będą należeć do eksperymentu runtime, nie do generatora słownika.

## Ergonomia sugestii

Docelowy przypadek:

```
swipe -> Malina
         malina
```

albo odwrotnie, zależnie od lokalnej preferencji użytkownika.

Użytkownik powinien móc wybrać drugi wariant z paska sugestii jednym stuknięciem, bez ponownego wpisywania słowa i bez ręcznego przechodzenia do Shift.

To jest główny cel użytkowy całego rozwiązania.

## Zdanie a homonimia leksykalna

Kapitalizacja początku zdania jest osobnym problemem.

Nie łączymy jej z regułą homonimii `malina/Malina`.

Warstwa kontekstowa początku zdania może później zmieniać powierzchnię, ale nie zastępuje mechanizmu wariantów leksykalnych.

## Zakres pierwszego eksperymentu

Nie wdrażamy od razu wszystkich 1702 ścisłych kandydatur.

Pierwsza faza ma objąć przede wszystkim kandydatury z bezpośrednimi klasami leksykalnymi innymi niż samo `nazwisko`, a następnie osobno przypadki mieszane.

Szczególnie wartościowe przypadki testowe:

- `malina/Malina`
- `łódź/Łódź`
- `warszawa/Warszawa`

`bardo` pozostaje kontrolnym przykładem wykluczonym z aktualnego ścisłego audytu dual-casing, ponieważ konkurencyjna analiza właściwa jest tylko klasy `nazwisko`.

## Czego nie robimy

- nie zmieniamy członkostwa immutable 100k;
- nie usuwamy `malina`, `łódź` ani `warszawa` z rdzenia;
- nie dodajemy jednorazowego wyjątku dla Warszawy;
- nie wymuszamy globalnie kapitalizowanej powierzchni dla żadnego słowa;
- nie przenosimy rozstrzygania kapitalizacji do generatora w postaci sztywnej reguły „proper > common”;
- nie traktujemy 1702 kandydatur jako gotowej listy produkcyjnej;
- nie zakładamy, że sama obecność dwóch powierzchni w CKDT da dwie sugestie.

## Warunek techniczny przed zmianą generatora

Najpierw trzeba potwierdzić w aktualnym runtime CleverKeys, gdzie i w jaki sposób kandydat jest deduplikowany case-insensitive oraz gdzie można dołączyć wariant powierzchni bez naruszania rankingu leksykalnego.

Dopiero po tym eksperymencie można zdecydować, jaki format metadanych/wariantu jest najbezpieczniejszy.

## Kryteria akceptacji eksperymentu runtime

Eksperyment uznajemy za funkcjonalny, gdy:

1. jeden klucz leksykalny może reprezentować co najmniej dwa warianty powierzchni;
2. warianty nie powodują podwójnego członkostwa ani zmiany 100k core;
3. ranking leksykalny nadal działa jak wcześniej;
4. użytkownik może wybrać alternatywną kapitalizację bez ręcznego przepisywania;
5. lokalna preferencja może zmieniać wariant główny;
6. oba warianty pozostają osiągalne;
7. przypadki `malina`, `łódź` i `warszawa` przechodzą testy regresyjne;
8. standardowa kapitalizacja zdań nie zostaje pomylona z homonimią leksykalną.

## Kolejność prac

1. Audyt aktualnego runtime CleverKeys i jego deduplikacji case-insensitive.
2. Minimalny eksperyment z jednym kluczem i dwoma wariantami powierzchni.
3. Test wyboru sugestii i lokalnego uczenia preferencji.
4. Dopiero potem projekt formatu danych dla generatora/CKDT.
5. Dopiero po walidacji runtime kwalifikowanie większej grupy kandydatur z audytu 1702.

## Stan

Na dzień 2026-10-01 rozwiązanie jest decyzją architektoniczną dla eksperymentu.

Nie zmieniono:

- immutable 100k;
- produkcyjnego członkostwa modułów;
- generatora CKDT w celu obsługi dwóch powierzchni;
- zachowania `main`.

Powiązany audyt kandydatur:
- `docs/CORE_DUAL_CASING_CLASS_AUDIT_2026-10-01.md`
- ścisły wynik: 1702 kandydatur.
