# Addytywna próba nazw, marek i skrótowców v8

## Cel i punkt wyjścia

Do zaakceptowanego na telefonie v7 dodajemy formy nazw własnych, marek,
oprogramowania i skrótowców, które mają pełne potwierdzenie analizy i generacji
w SGJP. Nie usuwamy ani nie przepisujemy żadnego wcześniejszego wpisu,
jego pisowni, wagi, wariantów kapitalizacji lub metadanych. Nie dodajemy
ręcznie opisów znaczenia ani domyślnych końcówek. Prywatny eksport użytkownika
nie jest źródłem, korpusem ani listą wyjątków. Porównanie duplikatów słownika
prywatnego z bazowym pozostaje zadaniem po rozbudowie.

Wejście to paczka z udanego runu producenta
[38139409942](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38139409942),
kod `7bf141662bcc548ee15001c24cbe081bd7469d9f`:
`cleverkeys-pl-thematic-forms-trial.zip`, SHA-256
`3f105ed66661b120a23c0b03cd2571651609c9fd766a4e36c6a264cbe14831df`.
V7 ma 188 302 klucze i 98 138 wpisów metadanych. Historyczny protokół v7
opisuje wcześniejszy stan prób; aktualne potwierdzenie użytkownika obejmuje
poprawny import i rozpoznawanie brakujących wcześniej słów.

Konsument przypięty w tej próbie:
`jakamilek/CleverKeysPL@141f27e7e780f00451b50887603cd885d015a72c`.
To poprawiony czytnik strumieniowy współdzielący dokładnie równe, niezmienne
wpisy z poprzednim snapshotem. APK tej wersji przeszedł runy
[38142499529](https://github.com/jakamilek/CleverKeysPL/actions/runs/38142499529)
i [38142502456](https://github.com/jakamilek/CleverKeysPL/actions/runs/38142502456).
Użytkownik zaakceptował na nim v7. V8 nie zmienia kodu aplikacji,
SI, gestów ani limitów importera. Nie podnosimy wersji aplikacji ani nie
publikujemy wydania; jest to kolejna izolowana paczka testowa API-v1.

## Źródła i potwierdzenie form

- Morfeusz2 `1.99.15`, słownik `pl.sgjp.sgjp-2026.06.01`.
- wordfreq `3.2.0`, commit `912caf64b657478d1dff1138efdc078947d54bb1`.
  Ranking jest sygnałem częstości, a nie dowodem poprawnej pisowni.
- Istniejące wykluczenia źródłowe imion:
  `sources/staging/first_name_source_exclusions.tsv`, SHA-256
  `2eda1f002aa3b631cbf919d71c43421190531d784d8545d8d6f2cd8c55faccea`.
  Wykluczenie lematu `Oleksandr` obejmuje również jego odmiany.

Oficjalny opis analizatora i generatora:
[Morfeusz](https://morfeusz.sgjp.pl/doc/about/).
Analizator nie rozstrzyga znaczenia z kontekstu. Tu ustala wyłącznie źródłową
tożsamość i dopuszczalne formy; istniejąca SI może później porównywać kandydatów.
Klasy NAME i etykiety pozostają danymi źródłowymi, bez ręcznie dopisywanych
definicji. SGJP jest źródłem leksykalnym, nie aktualnym rejestrem znaków towarowych.

Sprawdzamy 300 000 różnych, całych, alfabetycznych kandydatów polskiego
wordfreq o długości 2–25 liter. Alfabet obejmuje polskie litery i łacińskie
`q`, `v`, `x`, potrzebne w nazwach. Nie tniemy nazw wielowyrazowych,
adresów, łączników, apostrofów ani znaków interpunkcyjnych na nowe klucze.
Badamy małą literę, pierwszą wielką literę i wszystkie wielkie litery.
Sam fakt, że analizator przyjął zapis wielką literą, nie wystarcza:
wymagamy dokładnego dopasowania wygenerowanej formy, lematu, taga,
NAME i LABELS, dla jednego całego segmentu.

Źródłowe lematy znalezione w kandydaturach służą do wygenerowania pełnych
paradygmatów. Nowe formy również muszą przejść analizę i generację.
Odrzucamy samodzielne fragmenty nazw (`człon_*`), odczytania nieleksykalne
i przestarzałe jako podstawę przyjęcia nowego klucza. Aliasy klas zwykłych
`nazwa_pospolita` i `nazwa pospolita` nie są nazwami własnymi.

## Pomiar przed ograniczeniem pojemności

Najpierw mierzymy wszystkie potwierdzone nowe klucze, bez wstępnego progu
częstości. Wynik: 22 199 rodzin źródłowych i 128 934 kwalifikowane nowe klucze.
Ich dodatkowe metadane zajęłyby 2 491 066 węzłów, ponad pozostały budżet.

W v7 wykorzystano już 1 957 832 z 2 000 000 węzłów. Nie zwiększamy limitu
ani nie usuwamy starszych wpisów. Kolejność wyboru to najpierw marki,
firmy, oprogramowanie i języki programowania, następnie źródłowe skrótowce,
a następnie pozostałe nazwy, według malejącej częstości polskiej i klucza.
Każdy przyjęty wpis musi zmieścić się jednocześnie w limitach węzłów,
bajtów i liczby wpisów. Pełne dowody odłożonych form pozostają w audycie.

| Grupa | Zmierzone nowe klucze | Przyjęte klucze |
|---|---:|---:|
| Marki, firmy, oprogramowanie | 577 | 577 |
| Skrótowce | 467 | 467 |
| Pozostałe nazwy własne | 128 256 | 1833 |

Grupy nakładają się, dlatego nie sumujemy ich liczebności.
Łącznie dodano 2511 różnych kluczy. Odłożono 124 217 kluczy ze względu
na pojemność i 2206 kolizji nazw własnych z dominującymi wyrazami obcymi.
157 wygenerowanych kluczy nie miało aktualnego, powiązanego dowodu przyjęcia.

Kontrola kolizji obejmuje wyłącznie alfabetyczne ASCII z grupy samych nazw
własnych: najwyższa obca częstość musi wynosić co najmniej Zipf 3 i przewyższać
polską o więcej niż 1. Badane języki: en, cs, sk, ru, uk, de, es, it, fr, pt, nl.
Marki i potwierdzone skrótowce są odrębnymi kategoriami. Pozwala to nie
nadawać wysokiej rangi rzadkiemu nazwisku tylko dlatego, że identyczny zapis
jest popularnym słowem obcym. Audyt zachowuje źródłowy dowód i powód odłożenia,
bez ręcznej listy wyjątków (np. `from`, `just`, `then` są odłożone tą regułą).

## Kapitalizacja i przykłady

Klucz pozostaje jeden, z małych liter. W CKDT przechowujemy jeden źródłowy
zapis domyślny; w metadanych zachowujemy powiązane odczytania źródłowe.
Aktualny odczyt zwykłego wyrazu pisanego małą literą ma pierwszeństwo.
W pozostałych przypadkach domyślny zapis wybieramy według częstości źródłowego
lematu, nie według samej wielkości liter. Dlatego forma `Jana` rodziny `Jan`
wygrywa z instytucjonalnym skrótowcem `JANA`; ten drugi dowód nadal jest
w metadanych. Wcześniejsze wpisy, np. `janowi`/`Janowi`, pozostają bez zmian.

API-v1 dopuszcza wyłącznie polityki `lowercase` i `capitalized`.
Nie wysyłamy nieobsługiwanej polityki dla wszystkich wielkich liter.
`USB`, `HTML`, `NATO` zachowują dokładną źródłową pisownię w CKDT i
`canonicalForm`. Przyjęcie całego zapisu nie oznacza, że każde dodatkowe
odczytanie ALLCAPS ma osobny wariant wyboru w pasku. Dotychczasowe kolizje
mała litera/skrótowiec nie są przepisywane. Rozszerzenie tego API wymaga
osobnej zmiany konsumenta i producenta.

| Nowe przykłady zapisu | Powiązana forma źródłowa |
|---|---|
| Twitter | Twittera |
| Instagram | Instagrama |
| Google | Nie dopisujemy niepotwierdzonego `Googla` |
| USB, HTML, NATO | Zachowujemy cały źródłowy zapis |
| Jana | Janem, wspólny lemat `Jan:Sm1` |
| Ikea | Metadane obejmują również źródłowy lemat `IKEA` |

Lista ma pokazać przypadki kontrolne, nie definiuje ręcznych wyjątków.
Nie deklarujemy kompletnej bazy aplikacji i współczesnych marek.
Nazwy bez potwierdzenia w przypiętym SGJP, np. WhatsApp, wymagają kolejnego
źródła; nie dopisujemy ich ręcznie. Formy z interpunkcją również pozostają
poza tym etapem. Większa pula nazw będzie wymagać osobnego projektu
reprezentacji i pojemności metadanych.

## Wynik i weryfikacja

- 190 813 kluczy, 100 649 wpisów metadanych, 30 456 556 bajtów metadanych,
  1 999 993 węzły. Pozostało 7 węzłów; ta paczka zamyka obecny budżet,
  bez dalszego dokładania wpisów do jej metadanych.
- Limity są niezmienione: 32 MiB / 2 000 000 węzłów / 120 000 wpisów;
  maksymalnie 32 tożsamości lemat/POS na wpis.
- Wszystkie 188 302 stare rekordy, rangi i wpisy metadanych są zachowane.
  `unigrams.txt` i wcześniejsze atrybucje również pozostają bez zmian.
- Wszystkie dziewięć zgłoszonych brakujących słów z poprzednich etapów
  pozostaje obecne; test nie używa ich jako nowych wyjątków.
- Lokalne testy: 64 testy producenta PASS; 23 testy rzeczywistego parsera
  Kotlin PASS; pełne porównanie v7/v8 rzeczywistym czytnikiem CKDT i
  metadanych PASS, 1016 powiązań źródłowych nowych form.
- Osobne procesy JVM: zimne v8 i v7 + współdzielone v8, każdy z 16 MiB
  balastu przy `-Xmx192m`, PASS. Kontrolujemy źródłową pisownię i prezentację
  form w faktycznym `SwipeSurfaceVariants`. To nie pomiar PSS Androida
  ani szczytu pamięci i nie niezależny benchmark trafności swipe lub SI.
- CI odtwarza paczkę z przypiętych źródeł i wymaga identycznego
  `reviewed-report.json` przed publikacją artefaktu. CI i telefon dla v8
  pozostają do sprawdzenia w chwili przygotowania tego protokołu.

Paczka `cleverkeys-pl-names-forms-trial.zip`, 3 916 776 bajtów:
SHA-256 `0362cf38e06d821af96947104f7f714bfb63e9ea2ddf505ec466bc29140001f7`.
Pełny wynik, źródła i pozostałe sumy są w [reviewed-report.json](reviewed-report.json).
Artefakt CI obejmuje również `name-seed-audit.jsonl`, `name-forms-audit.jsonl`,
sumę paczki oraz zapis testów czytnika. Audyty nie trafiają do instalowanego ZIP-a.

Po udanym CI przekazujemy zweryfikowany ZIP do importu na już sprawdzonym APK.
Nie oczekujemy na Actions dłużej niż 60 sekund; użytkownik informuje o
zakończeniu. Nie ma merge, tagu, release ani publicznej publikacji aplikacji.
