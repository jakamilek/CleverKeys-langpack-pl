# TERC retention policy — 2026-09-25

## Docelowy zakres

Dla oficjalnego katalogu GUS TERYT TERC przyjmujemy następującą politykę retencji w słowniku CleverKeys:

| Poziom TERC | Liczba rekordów | Retencja |
|---|---:|---|
| Województwa | 16 | pełna odmiana liczby pojedynczej |
| Powiaty | 380 | odmiana selektywna, sterowana częstością i innymi wagami |
| Gminy | 2479 | wyłącznie mianownik |

Liczby 16 / 380 / 2479 są walidowanymi oczekiwanymi liczebnościami trzech poziomów TERC, a nie przybliżeniem.

## Zasady techniczne

1. Pełny wygenerowany materiał morfologiczny pozostaje artefaktem audytowym, nawet gdy część form nie trafi do finalnego słownika.
2. Województwa zachowują wszystkie zwalidowane formy liczby pojedynczej.
3. Gminy zachowują wyłącznie zwalidowany mianownik; odmiany gmin nie są dodawane do finalnego modułu TERC.
4. Powiaty otrzymują selekcję odmiany. Selekcja jest wykonywana dopiero po pomiarze rzeczywistego wkładu modułu do unii kluczy CKDT.
5. Dla powiatów:
   - NKJP1M jest głównym sygnałem częstości,
   - wordfreq jest niezależnym sygnałem wtórnym,
   - priorytet przypadku / użyteczność gramatyczna i pewność źródła są dodatkowymi wagami decyzyjnymi,
   - nie tworzymy sztucznego skumulowanego „score” łączącego NKJP i wordfreq.
6. Progi i quota dla powiatów nie są ustalane przed pomiarem. Po wygenerowaniu kompletnego materiału zostanie zmierzony rozkład częstości, a następnie zostanie wybrana deterministyczna selekcja mieszcząca się w uzgodnionej pojemności.
7. Wykluczone formy pozostają wykazane w artefaktach audytowych wraz z podstawą wykluczenia.
8. Równość kluczy jest case-insensitive. Ta sama forma znaczeniowo/kluczowo obecna w rdzeniu nie zużywa dodatkowego slotu, a różnica kapitalizacji może zostać zapisana jako wymiana powierzchni kanonicznej.

## Powiązanie z generowaniem

scripts/generate_terc_inflections.py służy do wygenerowania kompletnego, walidowalnego materiału dla audytu. Retencja produkcyjna jest osobną decyzją od generowania i nie może usuwać danych źródłowych ani dowodu ich oceny.

## Status

Polityka obowiązuje od 2026-09-25. Aktualny blokujący etap projektu pozostaje niezależny: ekstrakcja oficjalnego PDF KSNG/GUGiK (197 państw + stolice).
