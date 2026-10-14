# Audyt kandydatów względem v11 — 13.10.2026

Bazą pozostaje zaakceptowana v11. V12 z dodatkowymi nazwami jest odłożona.
Audyt nie tworzy langpacka, APK ani danych prywatnego słownika.

## Wynik automatycznej selekcji

| Unikalne nowe pojedyncze klucze | Liczba |
|---|---:|
| Potwierdzone źródłowo i spełniające dotychczasową politykę częstości | 1336 |
| Odrzucone z tej selekcji ze względu na próg częstości | 911 |
| Wymagające dodatkowych dowodów | 666 |
| Razem | 2913 |

1336 to 1333 zwykłe formy i trzy dodatkowe klucze: **hartować, wrotka, zawiesie**.
W module terminów przechodzi osiem kluczy, ale pięć już występuje w zwykłych
formach: kapeć, serwerownia, cyberprzemoc, nera, mikrofala.
Przykłady zwykłych form: fotorelacje, podpinać, slotów, zdyscyplinowana,
ziemniaczek, grejpfruty, lokalizatory, peelingi.

Potwierdzenie dotyczy istnienia formy i zachowanych odczytań SGJP.
Nie dowodzi konkretnego znaczenia technicznego/potocznego z indeksu.
Nie znaczy też, że wszystkie słowa są neutralne stylistycznie. Odczytania
i etykiety źródłowe pozostają w pełnym materiale, bez ręcznej cenzury lub zmian.

911 odrzuconych ma potwierdzenie SGJP, ale nie przechodzi istniejącej reguły:
Zipf formy >=2 albo Zipf formy >=1 oraz Zipf potwierdzonej rodziny w v11 >=2,5.
Przykłady blisko progu: dyferencjał, opornik, rezystor (1,99), responsywny (1,97),
chłodziarka (1,96). **Nie uznajemy ich za błędy ani trwale nieprzydatne słowa.**
Przy osobnym naborze terminów codziennych można je ocenić na podstawie innych
dowodów użycia; nie obniżono automatycznie progu i nie zmieniono wag v11.

666 oczekujących obejmuje 575 terminów i 92 nazwy aplikacji/usług, z jednym
wspólnym kluczem. Wśród terminów: 573 bez dokładnego zwykłego potwierdzenia
SGJP oraz dwa konflikty pisowni źródłowej: **Lisp/lisp, NEK/nek**.
Przykłady do dalszego potwierdzenia: powerbank, hashtag, cache, PDF, WhatsApp,
ChatGPT, Discord. Brak SGJP nie jest dowodem niepoprawności. Częstość klucza
nie rozstrzyga języka, znaczenia ani kapitalizacji homonimu.

Poza unią 2913 zachowano 1327 wierszy modułów już obecnych w v11 oraz 377
wierszy nowych fraz/zapisów z interpunkcją (291 terminów, 86 aplikacji).
To liczby wierszy modułów, nie dodatkowych unikalnych słów.

## Co ponownie wykonano

- Sprawdzono sumy ZIP v11 i paczki kandydatów, struktury CKDT i metadanych.
- Zweryfikowano 19 zamrożonych odpowiedzi źródłowych przez SHA-256 i rozmiar.
- Odtworzono 3290 zestawów wskazań źródłowych z indeksów/kategorii/etykiet.
- Ponownie obliczono częstości 4623 wierszy modułów.
- Ponownie wykonano natywną analizę i generację SGJP dla 4241 wierszy
  pojedynczych kluczy, porównując pełne dowody z zapisanym materiałem.
- Ponownie odtworzono 3501 istniejących propozycji metadanych, także dla
  wierszy już pokrytych przez v11; nie utożsamiać tej liczby z dodatkami.
- Sprawdzono duplikaty, normalizację przez lowercase z zachowaniem ogonków,
  dokładną pisownię, rodziny z odczytań v11 i zachowanie wszystkich interpretacji.
- Uruchomiono w tej sesji 97 istniejących testów producenta: OK.
  Nie są to 97 nowych testów tego audytu ani testy Androida.
- Domknięcie 14.10.2026: porównano dwa zakończone uruchomienia audytu.
  Wszystkie siedem wspólnych plików wynikowych jest identycznych bajt w bajt.
  Drugie uruchomienie dodatkowo zapisuje sondy obecności `coverage-probes.json`.

## Koszt potwierdzonej puli

Symulacja wyłącznie w pamięci, bez eksportu metadanych jako nowego langpacka.
Wspólne tabele i wszystkie stare wpisy pozostają identyczne.

| Parametr | Przyrost wpisów | Przyrost z opisem pochodzenia | Pozostaje z opisem |
|---|---:|---:|---:|
| Wpisy metadanych | 1336 | 1336 | 4365 |
| Elementy JSON | 13986 | 13995 | 184668 |
| Bajty metadanych | 217574 | 218122 | 4740137 |

Po symulacji: 115635 wpisów, 1815332 elementy JSON, 28814295 bajtów.
Opis pochodzenia jest jawnie zapisany w skrypcie; przyszły zmieniony opis
albo inny format wymaga ponownego pomiaru. Brak pomiaru ZIP/APK, RAM telefonu,
testu importu i Top-3. Limitów nie zwiększono.

## Rzeczywiste źródła i ograniczenia

- Morfeusz2 1.99.15; SGJP `pl.sgjp.sgjp-2026.06.01`.
- wordfreq 3.2.0, commit `912caf64b657478d1dff1138efdc078947d54bb1`.
  Ten zamrożony materiał nie jest aktualnym korpusem nowych marek.
- Wikisłownik: indeksy Informatyka 8885714, Technika 8885742, Slang 8885715.
  Indeksy służą do zebrania kandydatur, nie potwierdzają samodzielnie sensu.
- Wikipedia: bezpośredni zakres czterech kategorii (komunikatory, serwisy
  społecznościowe, chatboty, strumieniowanie muzyki); Wikidane: literalne
  etykiety i wybrane deklaracje. To materiał selekcyjny, nie dowód aktualności.
- Nazwy aplikacji wymagają dalszych źródeł pierwotnych, oceny polskiego użycia
  i reprezentacji metadanych. Ich koszt nie został doliczony jako zero.

Sprawdzono pomocniczo oficjalne polskie strony WhatsApp, Discord i ChatGPT
(adresy i ograniczenia w `official-source-notes.json`). Potwierdzają pisownię
i użycie w polskim tekście producenta, nie popularność korpusową ani pełną
odmianę. Pozostają w grupie wymagającej danych, dopóki cały warunek akceptacji
nie jest spełniony. Nie wymyślono im lematów, odmiany ani znaczeń.

## Luki zbierania i następny etap

Wyniki sond obecności są w `coverage-probes.json`. Pula nie zawiera wszystkich
ważnych celów: m.in. TikTok, WiFi, streamować, scrollować, googlować wymagają
osobnego pozyskania dowodów. Nie dopisano ich po cichu do mianownika 2913.
Priorytet dalszego automatycznego naboru: źródła polskiego użycia współczesnych
terminów i oficjalna pisownia marek, z osobną oceną sensu, odmiany i częstości.
Nie wymaga to ręcznego przeglądania list przez użytkownika. Na tym etapie
nie ma problemu pojemności, który uzasadniałby podniesienie limitów.

## Tożsamość materiałów i odtworzenie

Skrypty producenta są na gałęzi `feature/additive-common-forms-v1`, commit
`535318eb4c4019625c3f63e04a1ba437c58c50ea` (nie na main).
Dokładny commit produkcji v11: `de587268e3936ade2cecb5bd595a0993b7103148`.

- v11: https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38437507820
- Kandydaci push: https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38450745004
- Kandydaci PR: https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38450754403

W tej sesji sprawdzono sukces powyższych runów. Dostępny artefakt kandydatów PR:
11839009981, zewnętrzny ZIP SHA-256
`da4d6e17927f915bdcbb3eac6d7c411de8fd9df2bb97cf3a23c058e733500735`.
To hash z metadanych GitHub, nie ponowne pobranie i hashowanie zewnętrznego ZIP-a.

Lokalnie przeliczone SHA-256 wejść:

- v11: `8169a8ac33261fc245d46a344193759a0c1a84b0eb49cf2436e46ccaed90a229`
- kandydaci: `6c7a7c2be951f6b32c1b65be24f3e907ad3a3f5bc161eaadf1b4ae0e794ffe77`

Z przypiętymi zależnościami uruchom w repozytorium:

```bash
python scripts/audit_practical_candidates.py \
  --base /path/to/cleverkeys-pl-compact-source-trial.zip \
  --bundle /path/to/cleverkeys-pl-practical-candidates.zip \
  --out build/practical-audit-new
```

Katalog wyjściowy musi być nowy. Skrypt odmawia innych wersji źródeł/ZIP-ów.
`decisions.jsonl` zachowuje wszystkie oryginalne rekordy dla każdego klucza,
powody, moduły, źródła, dowody, częstości i zatwierdzone propozycje metadanych.
Nie uruchamiać Python z `-O`, ponieważ walidacja używa asercji.
