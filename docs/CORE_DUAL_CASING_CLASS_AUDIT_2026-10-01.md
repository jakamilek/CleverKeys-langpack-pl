# Audyt homonimii kapitalizacyjnej rdzenia 100k — 2026-10-01

## Cel

Zmierzono wyłącznie immutable 100k core pod kątem powierzchni, dla których Morfeusz 2 / SGJP pokazuje równocześnie:

- rzeczownik w mianowniku liczby pojedynczej (subst:sg:nom) z klasą wspólną `nazwa_pospolita` albo alternatywnym zapisem tej klasy `nazwa pospolita`;
- konkurencyjną analizę rzeczownikową (subst:sg:nom) z co najmniej jedną inną klasą NAME.

Moduły nie były używane do kwalifikacji. Formy odmiany inne niż mianownik zostały wyłączone.

## Źródła i wersje

- Morfeusz 2: `1.99.15`
- słownik: `pl.sgjp.sgjp-2026.06.01`
- rdzeń: dokładnie `100000` kluczy
- AOSP i wordfreq użyte wyłącznie do odtworzenia obecnej procedury wyboru immutable 100k
- wynik pochodzi z osobnego GitHub Actions run `36835102788`

## Wynik

Pierwszy pomiar dawał 1713 kandydatów. Dalsza kontrola wykazała 11 fałszywych „konkurencji”: Morfeusz używa w tym snapshotcie także wartości `nazwa pospolita` (ze spacją), a dla wszystkich 11 sprawdzonych przypadków oznacza ona ten sam typ pospolitego leksemu co `nazwa_pospolita`.

Po uwzględnieniu obu zapisów:

| Kategoria analityczna | Liczba |
|---|---:|
| wszystkie ścisłe kandydatury | **1702** |
| tylko `nazwisko` | **1173** |
| `nazwisko` + co najmniej jedna inna klasa | **254** |
| bez `nazwisko`, z bezpośrednią klasą leksykalną | **253** |
| bez `nazwisko`, tylko klasy typu `człon_*` | **22** |

Zatem 1702 = 1173 + 254 + 253 + 22.

## Klasy NAME występujące w 1702 kandydatach

Liczby są liczbą kandydatów posiadających daną klasę; jeden kandydat może należeć do wielu klas.

| Klasa NAME | Kandydaci |
|---|---:|
| `nazwisko` | 1427 |
| `nazwa_geograficzna` | 340 |
| `imię` | 135 |
| `człon_nazwy_geograficznej` | 41 |
| `nazwa_własna_astronomiczna` | 13 |
| `tytuł` | 6 |
| `nazwa_członka_rodu` | 3 |
| `nazwa_organizacji` | 2 |
| `człon_nazwiska` | 1 |
| `człon_nazwy_własnej` | 1 |
| `człon_tytułu` | 1 |
| `marka` | 1 |
| `nazwa_firmy` | 1 |
| `nazwa_instytucji` | 1 |
| `nazwa_własna` | 1 |
| `pseudonim` | 1 |

## Kombinacje klas NAME

Każdy kandydat jest tu liczony raz według pełnego zbioru konkurencyjnych klas:

| Kombinacja | Kandydaci |
|---|---:|
| `nazwisko` | 1173 |
| `nazwa_geograficzna + nazwisko` | 164 |
| `nazwa_geograficzna` | 163 |
| `imię` | 61 |
| `imię + nazwisko` | 57 |
| `człon_nazwy_geograficznej` | 20 |
| `człon_nazwy_geograficznej + nazwisko` | 18 |
| `imię + nazwa_geograficzna` | 7 |
| `imię + nazwa_geograficzna + nazwisko` | 6 |
| `tytuł` | 6 |
| `nazwa_własna_astronomiczna` | 5 |
| `nazwa_własna_astronomiczna + nazwisko` | 5 |
| `nazwa_członka_rodu` | 3 |
| `człon_nazwy_geograficznej + imię` | 2 |
| `nazwa_organizacji` | 2 |
| `człon_nazwiska + imię + nazwa_własna_astronomiczna + nazwisko` | 1 |
| `człon_nazwy_geograficznej + nazwa_własna_astronomiczna + nazwisko` | 1 |
| `człon_nazwy_własnej` | 1 |
| `człon_tytułu` | 1 |
| `imię + nazwa_własna_astronomiczna + nazwisko` | 1 |
| `marka` | 1 |
| `nazwa_firmy` | 1 |
| `nazwa_instytucji + nazwisko` | 1 |
| `nazwa_własna` | 1 |
| `pseudonim` | 1 |

## Co wynika z przykładów

- `warszawa` pozostaje kandydatem: common `nazwa_pospolita` + proper `nazwa_geograficzna | nazwisko`.
- `łódź` pozostaje kandydatem: common `nazwa_pospolita` + proper `nazwa_geograficzna`.
- `malina` pozostaje kandydatem: common `nazwa_pospolita` + proper `imię | nazwa_geograficzna | nazwisko`.
- `bardo` nie jest kandydatem w ścisłym audycie, ponieważ konkurencyjna analiza jest tylko nazwiskowa.

To potwierdza, że wcześniejsza liczba 1713 zawierała dokładnie 11 przypadków wynikających z alternatywnego zapisu klasy pospolitej, a nie z rzeczywistej homonimii kapitalizacyjnej.

## Dodatkowy rozkład grupy 254: nazwisko + inna klasa

W tej grupie pełna kombinacja po odrzuceniu samego @@nazwisko@@ wygląda następująco:

| Pozostała klasa / klasy | Kandydaci |
|---|---:|
| @@nazwa_geograficzna@@ | 164 |
| @@imię@@ | 57 |
| @@człon_nazwy_geograficznej@@ | 18 |
| @@imię + nazwa_geograficzna@@ | 6 |
| @@nazwa_własna_astronomiczna@@ | 5 |
| @@człon_nazwiska + imię + nazwa_własna_astronomiczna@@ | 1 |
| @@człon_nazwy_geograficznej + nazwa_własna_astronomiczna@@ | 1 |
| @@imię + nazwa_własna_astronomiczna@@ | 1 |
| @@nazwa_instytucji@@ | 1 |

Suma: 254.

To pokazuje, dlaczego nie wolno filtrować całej grupy @@nazwisko + inna klasa@@ jednym warunkiem. @@Warszawa@@ i @@Malina@@ należą do tej grupy, ale ich dodatkowe klasy są różne.

## Wniosek roboczy

Nie należy jeszcze traktować wszystkich 1702 rekordów jako kandydatów do dwóch widocznych powierzchni w klawiaturze.

Najbardziej użyteczny dalszy podział to:

1. **bezpośrednie klasy leksykalne bez `nazwisko` — 253**, np. `imię`, `nazwa_geograficzna`, `nazwa_własna_astronomiczna`, `marka`, `nazwa_firmy`, `nazwa_organizacji`, `tytuł`;
2. **mieszane z `nazwisko` — 254**, które wymagają osobnej oceny, ponieważ obecność nazwiska sama w sobie nie powinna tworzyć drugiej powierzchni;
3. **same klasy `człon_*` — 22**, które dotyczą elementów nazw, a niekoniecznie samodzielnych nazw własnych;
4. **tylko `nazwisko` — 1173**, które dla naszego celu nie są sensowną podstawą do dodawania wariantu kapitalizacyjnego.

Na tym etapie nie zmieniono członkostwa ani powierzchni immutable 100k i nie zmieniono runtime CleverKeys.
