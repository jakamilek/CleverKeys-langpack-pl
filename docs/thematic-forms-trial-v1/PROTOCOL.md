# Addytywne grupy tematyczne — próba v7

## Wynik i zaakceptowana kolejność

**181 691 + 6611 = 188 302 klucze.** Żaden stary rekord, bajt rangi,
wariant kapitalizacji, wpis metadanych ani bajt unigrams nie został usunięty
lub zmieniony. Stare powiązania accent-map zachowują wzajemną kolejność.
Nowe formy mogą wpływać na ranking konkurujących gestów; zachowanie starych
bajtów rang nie gwarantuje niezmiennej kolejności podpowiedzi.

Wcześniej uzgodniona kolejność: (1) odmiany czasowników, (2) rzeczowników,
(3) przymiotników/imiesłowów, (4) potoczne wiadomości, (5) komputer/internet,
(6) dom/zakupy/narzędzia/budownictwo, (7) marki/aplikacje/skróty z odmianami,
(8) imiona/nazwiska/miejscowości z odmianami. Ogólna paczka v6 poszerzyła
grupy 1–3; v7 wybiera rodziny z indeksów grup 4–6. To poszerzenie pokrycia,
nie deklaracja kompletności tych grup. Etapy 7–8 oraz końcowe porównanie
prywatnego eksportu pozostają kolejnymi zadaniami.

| Źródłowy indeks | Dodatkowe formy |
|---|---:|
| Potoczne | 4691 |
| Informatyka | 589 |
| Technika | 1207 |
| Dom | 132 |
| Architektura/budownictwo | 247 |
| Jedzenie | 374 |
| Sklepy | 47 |

Grupy zachodzą na siebie; nie wolno sumować kolumny jako unikalnych dodatków.
Przykłady rzeczywiście nowych form: backupy, kompilatory, cyberbezpieczeństwie,
mrugaj, dramatyzuj, rozkminę, durszlaku, taborety, zamrażarką, szlifierki,
imadła, wspornikami, parmezanem, kurkumę, delikatesach.

## Zamrożone źródła i reguły

- Wewnętrzny ZIP v6 z runu 38121444186, artifact 11694789515,
  SHA-256 `01ea95d26a32a9784d3de10495a89e91a28f77230b39c3ddb298ecb27e127fce`.
- Siedem publicznych indeksów Wikisłownika w `source/thematic-v7`.
  `intake-lock.json` przypina wersje, daty, URL, historię autorów i hashe
  dokładnych tekstów. CI używa zapisanych wersji, nie strony „latest”.
- Morfeusz2 1.99.15, SGJP `pl.sgjp.sgjp-2026.06.01`, wordfreq 3.2.0
  commit `912caf64b657478d1dff1138efdc078947d54bb1`. To te same źródła
  fleksji/częstości co v6; wersje i commit są sprawdzane przy budowie.
- Całe małoliterowe cele linków; nie rozbijamy fraz, nie zgadujemy kapitalizacji
  z etykiet i nie normalizujemy nazw własnych do zwykłych wyrazów.
- Lematy muszą mieć zwykłą analizę całego słowa i dokładne poświadczone
  generowanie. Kandydat musi mieć analizę/generowanie z tą samą tożsamością
  lematu, pełnym tagiem i klasami, oraz należeć do poświadczonej rodziny indeksu.
  Odczytania wyłącznie nazwowe, nieleksykalne i dawne/historyczne/gwarowe
  nie stanowią podstawy dodatku. Inne współistniejące dowody są zachowane.
- Zipf formy >=1.0; dokładny zwykły lemat ma źródłowe hasło indeksu o Zipf >=2.0.
  W v6 próg rodziny >=2.5 obejmował stary v5; tu >=2.0 dotyczy wyłącznie
  zamrożonych indeksów. Nie ma globalnego obniżenia ani wyjątków dla słów.
- 8823 klucze indeksowe; 7498 ze zwykłymi dowodami, 1325 bez takich dowodów.
  8491 rodzin generuje 147642 klucze, z których 29677 już występowało w v6.
  111285 brakujących form odpada przez częstość, 69 przez powiązanie źródłowe,
  6611 przechodzi wszystkie warunki. Pełne decyzje są w audytach JSONL.
- Wagi nowych wpisów wynikają z istniejącej logarytmicznej kwantyzacji wordfreq.
  Nie zwiększamy ręcznie wag potocznych lub tematycznych słów.

Indeks wyznacza rodziny do sprawdzenia; nie dowodzi znaczenia każdego homografu.
Nie dopisujemy opisów i nie twierdzimy, że SI czyta etykietę tematyczną. Runtime
zachowuje źródłowe lemma/POS/surfaces/nameClasses/labels, w tym poświadczone
homonimy i kapitalizacje. Tematyczne powiązania i pełne tagi pozostają w audycie.
Nowe słowa bez wymaganych dowodów SGJP, frazy, marki i skróty nie są na siłę
dodawane. Prywatny słownik nie jest wejściem ani testowym wyjątkiem.

## Format i limity

CKDT v2, langpack version=7/API=1. Cały pakiet nadal ma pięć standardowych
członków, bez audytów i modeli SI. 98138 wpisów metadanych, 29828753 bajty,
1957832 węzły JSON; pozostaje 42168 węzłów do obecnego limitu 2M.
Pozostałe limity 32MiB/120000 wpisów/głębokość32/string16384/32 source identities
pozostają. Przed większymi etapami nazw trzeba zaplanować dalszą pojemność
metadanych, bez usuwania starych danych i bez bezwarunkowego podnoszenia limitów.

ZIP SHA-256 `3f105ed66661b120a23c0b03cd2571651609c9fd766a4e36c6a264cbe14831df`.
Dictionary SHA-256 `7b081aff64b0c386650ed0f986a570633e2d02af057196b9f63dcde2a1c6c129`.
Pełny deterministyczny wynik: `reviewed-report.json`.

## Rzeczywista weryfikacja, również nieudany test pamięci

Lokalnie 56 testów producenta PASS. Rzeczywiste pliki konsumenta
CleverKeysPL `2f4735dd296e07bd8358ab8c71a3a58760e9cd0d` (bieżący 524bdab
różni się tylko dokumentacją) przechodzą 21 testów parsera i pełne v6 → v7:
181691 starych rekordów/metadanych zachowane, 188302 klucze, wszystkie
nowe formy mają odczytywane sourceLemmas, 3964 relacje nowych form.

Izolowane rzeczywiste workloady JVM, każdy z 16MiB żywych danych dodatkowych:

| Workload | Heap JVM | Wynik |
|---|---:|---|
| Dwie niezmienione paczki v6 | 192MiB | OOM — kontrola bazowa |
| v6 + v7 | 192MiB | OOM |
| Sam v7 | 192MiB | PASS |
| v5 + v7, pierwotny scenariusz aktualizacji | 192MiB | PASS |
| v6 + v7, dwa duże snapshoty przy aktualizacji | 256MiB | PASS |

Nie ukrywamy OOM ani nie nazywamy 256MiB testem 192MiB. Przyczyna dotyczy
współistnienia dwóch już dużych snapshotów; nie dowodzi problemu wyłącznie
nowych 6611 wpisów. Istniejący gate 192MiB aplikacji nie został zmieniony.
To pomiar heap JVM, nie pamięci Androida, PSS ani telefonu/modelu SI.
Nie zmieniamy aplikacji, rankera, gestów, ustawień lub importowego rollbacku.

CI odtwarza ZIP, porównuje cały report i powtarza rzeczywisty consumer oraz
trzy pozytywne gate'y pamięci w osobnych JVM. Artifact jest publikowany po
wszystkich bramkach; dotychczasowa próba v6 zostaje dostępna niezależnie.

## Test telefonu i dalszy etap

Użytkownik potwierdził szybkie ładowanie menedżera w najnowszym APK, jak przed
rozszerzeniem. Nie potwierdził osobno wcześniejszego crasha przy przełączaniu
zakładek w trakcie ładowania; ten retest pozostaje otwarty.

Po udanym CI importować **wewnętrzny ZIP langpacka**, nie archiwum audytów.
Nie trzeba nowego APK: pozostaje wersja z szybkim menedżerem i streamingiem.
Sprawdzić licznik 188302, swipe przykładów powyżej i dziewięciu wcześniejszych
regresji, mała/wielka litera i odmiany z SI, czas importu i menedżera oraz
zakładki podczas ładowania. Nie ma jeszcze dowodu jakości Top3 ani pomiaru RAM
na telefonie dla v7.

Po etapach 7–8 porównać prywatny eksport z dokładnymi formami i zadeklarowanymi
kapitalizacjami. Nie usuwać z bazowego słownika; nie usuwać przez folding
ogonków. Eksport prywatny pozostaje poza git; import użytkownika scala wpisy,
więc sam nie usuwa już zapisanych na telefonie duplikatów.

Bez merge/tag/release. Monitoring Actions <=60s łącznie na run, potem stan
zgłasza użytkownik. Dokumentacja źródeł/licencji jest dołączona do repo i ZIP.
