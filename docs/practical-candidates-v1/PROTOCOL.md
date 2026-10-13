# Moduły kandydatów praktycznego słownictwa — etap 1

Użytkownik wybrał pozostanie przy zaakceptowanej v11 i odłożenie dodatkowej
partii nazw v12. Przygotowujemy wyłącznie paczkę danych do przeglądu, nie
nowy słownik do importu ani APK. Aktualnego pakietu i limitów nie zmieniamy.

Baza: 204 463 słowa, 114 299 wpisów; ZIP SHA256
`8169a8ac33261fc245d46a344193759a0c1a84b0eb49cf2436e46ccaed90a229`.
Pozostaje 5701 wpisów/198663 elementy/4958259 bajtów metadanych.

## Moduły i pełny pomiar

| Moduł | Nowe pojedyncze klucze | Obecne w v11 | Nowe pozostałe zapisy |
|---|---:|---:|---:|
| Zwykłe formy | 1333 | 0 | 0 |
| Terminy techniczne/internetowe i potoczne | 1494 | 1319 | 291 |
| Aplikacje/usługi | 92 | 8 | 86 |

Moduły nakładają się: 5 wspólnych zwykłych/terminów i 1 termin/aplikacja.
Unia to 2913 nowych pojedynczych kluczy. To kandydatury, nie zatwierdzone dodatki.
Frazy i interpunkcja pozostają całe, bez zgadywania komponentów lub końcówek.
Deduplikujemy przez lowercase, zachowując ogonki; nie robimy accent folding.
Źródłowe identyfikatory/QID/rewizje zachowujemy nawet przy równych kluczach.

1333 zwykłe formy są ponownie potwierdzone w natywnym SGJP i spełniają te same
progi co v6: formZipf>=2 albo>=1 i familyZipf>=2,5. Rodziny ustalamy z pełnych
źródłowych odczytań v11, nie z domniemanych rdzeni. Stary audyt v6 przechowuje
wszystkie interpretacje i dokładne zgodności analiza/generacja. Tę grupę można
skierować do dalszego przeglądu: 13936 elementów/216771 bajtów proponowanych wpisów.

W module terminów 921 nowych kluczy ma zwykłe źródłowe potwierdzenie SGJP;
573 wymaga dalszego źródła/pisowni/morfologii. Sam indeks i poprawność SGJP
nie dowodzą częstego użycia lub konkretnego znaczenia homonimu. Nie stosujemy
dodatkowego progu częstości przed pomiarem całego nowego modułu.

92 nowe pojedyncze nazwy aplikacji/usług wymagają sprawdzenia pisowni,
aktualności, polskiego użycia, klasy obiektu i ewentualnej odmiany. Kategorie
obejmują także historyczne produkty i ogólne pojęcia. Nie twierdzimy, że to
kompletna baza współczesnych marek lub że każdy wiersz jest nazwą marki.
Brak SGJP nie dowodzi błędu; etykieta nie tworzy automatycznie lematu/POS/NAME.
Nie zgadujemy odmian ani opisów znaczenia dla SI. Koszt nieznanych metadanych
jest null w rekordzie, nie zero; podsumowanie sumuje tylko znane koszty.

## Zamrożone źródła

- Morfeusz2 1.99.15 / `pl.sgjp.sgjp-2026.06.01`, wordfreq 3.2.0 commit
  `912caf64b657478d1dff1138efdc078947d54bb1`; sprawdzamy natywną wersję,
  słownik i direct_url commitu. Prywatny eksport nie jest źródłem/fixturem.
- Audyt v6 z runu 38121444186, SHA256
  `ad47bd2386bf7a68d37dc84ae8b0bcd2d2b86802817398292477dbee03b53e00`.
  Każdy przyjęty zwykły kandydat ma identyczną ponowną natywną analizę/generację.
- Indeksy polskiego Wikisłownika: Informatyka (rev 8885714), Technika (rev 8885742),
  Slang (rev 8885715). Całe cele linków, bez wybierania słów ręcznie.
- Bezpośrednie strony czterech polskich kategorii Wikipedii: Komunikatory
  internetowe, Serwisy społecznościowe, Chatboty, Usługi strumieniowania muzyki.
  Brak rekurencji. To ograniczony jawny zakres, nie gwarancja kompletności.
- 187 stron i 185 obiektów Wikidanych. Etykieta pl, fallback en jawnie oznaczony;
  jeśli brak etykiety, pozostaje pełny tytuł artykułu, wraz z kwalifikatorem.
  Nie usuwamy nawiasów w celu wymyślenia pisowni. Wspólna pisownia zachowuje
  wszystkie obiekty i dowody, zamiast bezgłośnego wybierania jednego.
- 19 odpowiedzi API w `source/practical-candidates-v1`; lock ma URL, rewizje,
  czas pobrania i SHA. Członkostwo kategorii jest zamrożone hashem odpowiedzi,
  nie numerem edycji strony kategorii. Projekcja Wikidanych zachowuje literalne
  etykiety/identity i mainsnaks P31/P856; pomija nieużywane claims/references,
  zachowuje także SHA i rozmiar pierwotnej odpowiedzi. Nie jest interpretacją
  znaczeń. Źródłowe rank/snaktype i obiekty pozostają w projekcji.

Źródłowe teksty/wybór indeksowy Wikimedia: autorzy, CC BY-SA 4.0;
ustrukturyzowane Wikidane: CC0. URL i przypisanie źródła są w każdym rekordzie,
licencje/NOTICE v11 pozostają. Indeks Elektronika nie istnieje w sprawdzonym
źródle; nie podstawiamy pod niego wymyślonych danych.

## Format i walidacja

ZIP zawiera `candidate-bundle.json`, trzy moduły JSONL/listy przeglądu,
polski raport i zamrożone dowody. Nie zawiera manifest.json/dictionary.bin/
language-intelligence.json, więc nie jest paczką importową. Listy nowych
kluczy nie oznaczają zatwierdzonych dodatków. Nie zmieniamy żadnego starego
słowa, kapitalizacji, rankingu SI, modelu lub gestu.

97 lokalnych testów producenta PASS, w tym pełna deterministyczna syntetyczna
budowa, odmowa nadpisania, checksum/path guards, język/kapitalizacja źródeł,
niezgadywanie fraz, exact lower proof, projekcja literalnych źródeł i null kosztu.
Rzeczywista budowa ponownie weryfikuje wszystkie 1333 formy, liczniki modułów,
pełny JSON/ZIP, unikatowość i brak importowych plików. CI odtwarza dokładny
reviewed-report.json z obu przypiętych wejść i zamrożonych snapshotów.
Nie ma nowego testu Androida/PSS ani obietnicy trafności; to tylko kandydatury.
Następnie: przegląd użyteczności/źródeł, potwierdzenie odmian/kapitalizacji,
deduplikacja całej unii, wybór i pomiar; dopiero później przyszły langpack.

Bez merge/tag/release. Actions monitorowane do 60 s łącznie/run.
