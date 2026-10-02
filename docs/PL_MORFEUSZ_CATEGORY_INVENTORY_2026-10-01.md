# Morfeusz 2 / SGJP — inventory klas nazwowych i tagów (2026-10-01)

Źródło wykonania: Morfeusz 2 / SGJP **1.99.15**, słownik **pl.sgjp.sgjp-2026.06.01**, tagset **pl.sgjp.morfeusz-0.8.0**. Pomiar wykonano w izolowanym GitHub Actions run po commitcie `8f9d25950e221dee0099b2f6df18259d60aca2c6` (job `110273035055`), bez wpływu na zawartość rdzenia 100k ani reguły kapitalizacji.

## Struktura wyniku Morfeusza

Pythonowy wrapper zwraca analizę jako:

`(orth, lemma, tag, name, labels)`

czyli:
- `TAG` — informacja gramatyczna;
- `NAME` — klasyfikacja nazwy własnej / pospolitej;
- `LABELS` — kwalifikatory słownikowe.

Oficjalna dokumentacja Morfeusza rozróżnia te trzy warstwy.

## Wynik inventory

- unikalne pełne ciągi `TAG`: **736**;
- unikalne pierwsze człony `TAG` (klasy POS): **45**;
- różne wartości `NAME`: **81**;
- pojedyncze klasy składowe `NAME` po rozbiciu kombinacji po `|`: **37**;
- niepuste kombinacje `LABELS` faktycznie wyliczone: **615**;
- różne wartości zwracane przez `getLabels()`: **605**.

Uwaga: `getTagsCount()`, `getNamesCount()` i `getLabelsCount()` w tym buildzie zwracają **65536** jako przestrzeń identyfikatorów. Nie należy interpretować 65536 jako liczby rzeczywistych kategorii. Rzeczywisty używany inwentarz został policzony przez enumerację wartości i odrzucenie pustych/nieużywanych wpisów.

## 37 pojedynczych klas `NAME`

```text
człon_nazwiska
człon_nazwiska_(herb)
człon_nazwy_firmy
człon_nazwy_geograficznej
człon_nazwy_instytucji
człon_nazwy_organizacji
człon_nazwy_własnej
człon_nazwy_święta
człon_przydomka
człon_pseudonimu
człon_tytułu
imię
marka
nazwa pospolita
nazwa_członka_rodu
nazwa_firmy
nazwa_geograficzna
nazwa_instytucji
nazwa_języka_programowania
nazwa_kroju_pisma
nazwa_oprogramowania
nazwa_organizacji
nazwa_pospolita
nazwa_własna
nazwa_własna_astronomiczna
nazwa_własna_budowli
nazwa_własna_osoby
nazwa_własna_środka_lokomocji
nazwa_święta
nazwisko
nazwisko_(odmężowskie)
nazwisko_(odojcowskie)
patronimicum
pospolita
przydomek
pseudonim
tytuł
```

### Ważna obserwacja dla projektu

Nie należy traktować tych 37 klas jako równorzędnych „typów słów”:
- część to pełne klasy nazw (`imię`, `nazwisko`, `nazwa_geograficzna`, `nazwa_firmy`, `nazwa_organizacji` itd.);
- część oznacza **człon** nazwy wieloczłonowej (`człon_nazwy_geograficznej`, `człon_nazwiska` itd.);
- część to relacje/typy szczególne (`pseudonim`, `przydomek`, `tytuł`, `patronimicum`);
- `nazwa_pospolita`, `nazwa pospolita` i `pospolita` są odrębnymi wartościami zwróconymi przez inventory, więc ich znaczenie trzeba sprawdzić na konkretnych analizach zamiast je automatycznie utożsamiać.

### Przykłady kluczowe dla kapitalizacji

- `bardo`: `nazwa_pospolita`;
- `łódź` / `Łódź`: obok `nazwa_pospolita` występuje `nazwa_geograficzna`;
- `malina` / `Malina`: `nazwa_pospolita` oraz konkurencyjnie `imię|nazwa_geograficzna|nazwisko`, a także `nazwisko` i `nazwa_geograficzna`;
- `warszawa` / `Warszawa`: `nazwa_pospolita` oraz konkurencyjnie `nazwa_geograficzna|nazwisko` i `nazwisko`.

Wniosek: pole `NAME` jest właściwą warstwą do badania klas nazwowych, natomiast `TAG` nie zastępuje tej klasyfikacji. Dla naszego audytu należy nadal rozdzielać: POS/tag, klasę `NAME`, kwalifikatory `LABELS` oraz dowód fleksyjny.

