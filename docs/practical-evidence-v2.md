# Uzupełnienie dowodów — partia priorytetowa, 14.10.2026

Baza: v11. V12 odłożona. Wyłącznie materiał analityczny, bez langpacka/APK.

## Zakres i wynik

Sprawdzono 17 pozycji: 12 z grupy 666 wymagających dowodów oraz 5 luk wskazanych
w sondach obecności. Nie jest to ukończona weryfikacja wszystkich 666 pozycji.
654 dotychczasowe klucze nie otrzymały w tej partii nowego przeglądu źródeł.
Zachowano osobno wszystkie 2913 pierwotnych decyzji, bez przepisywania historii.

| Wynik uzupełnienia | Liczba | Pozycje |
|---|---:|---|
| Potwierdzenie pisowni/odnotowania w źródle; nadal niezatwierdzone do instalacji | 15 | powerbank, hashtag, emoji, streaming, scrollować, streamować, googlować, WhatsApp, ChatGPT, Discord, Spotify, Signal, Photoshop, PDF, TikTok |
| Odłożenie z priorytetu aktywnych aplikacji | 1 | Skype |
| Brak potwierdzenia dokładnie żądanego wariantu pisowni | 1 | WiFi; źródło potwierdza Wi-Fi |

Nowe luki: scrollować, streamować, googlować, TikTok, WiFi. Ich obecność poza v11
i poza pierwotną pulą ustalono w wcześniejszej sondzie kluczy. Nie dopisano ich
do mianownika 2913. Zebrane formy odmiany nie są kolejnymi zatwierdzonymi kluczami.

## Najważniejsze dowody

- **powerbank**: WSJP PAN, hasło 81432, jawna tabela odmiany i polskie cytaty.
  Zapisano formy z tabeli, bez generowania końcówek.
- **hashtag**: WSJP PAN, hasło 86506, jawny wariant hasła hasztag i cytat.
  Tabela odmiany dotyczy hasztag. Nie zamieniano szt na sh w jej komórkach.
- **emoji**: Dobry słownik, hasło 225460, rzeczownik nijaki nieodmienny.
- **streaming**: Dobry słownik, hasło 226209, jawna lista form rzeczownika.
- **scrollować**: Obserwatorium Językowe UW, opracowanie z 27.01.2024,
  hasło i liczne przykłady. Jest to opis rzeczywistego użycia, nie automatyczna
  rekomendacja wszystkich odnotowanych wariantów pisowni.
- **streamować, googlować**: hasła Dobrego słownika z informacją gramatyczną
  i listami form. Zapisano niewielki wybór literalnych form, nie pełne paradygmaty.
- **WhatsApp, ChatGPT, Discord, Spotify, Signal, Photoshop, PDF**: strony
  właścicieli produktów/dokumentacja po polsku potwierdzają dokładną pisownię.
  Lokalizacja producenta nie dowodzi częstości w niezależnym polskim korpusie.
- **TikTok**: oficjalna strona potwierdza nazwę z wewnętrzną wielką literą.
  Polski materiał wsparcia dostępny był w wyniku wyszukiwania, ale bez pełnego
  odczytu strony. Ograniczenie jawnie zapisano; nie uznano go za pełny snapshot.
- **Skype**: Microsoft podaje wycofanie konsumenckiego komunikatora 5.05.2025.
  Nie dotyczy to Skype for Business. Nazwa może mieć wartość historyczną,
  ale wysoka stara częstość nie dowodzi aktywności usługi w 2026 r.
- **WiFi**: polska instrukcja Apple używa Wi-Fi. Nie usunięto łącznika,
  nie utworzono automatycznego aliasu i nie utożsamiono tych kluczy.

Dokładne adresy, daty odczytu, dostępne wersje, zakres dowodu, formy i ograniczenia
są w `source/practical-evidence-v2/observations.json`. To transkrypcja sprawdzonych
faktów ze źródeł, nie dowód wygenerowany przez model. Skrypt sprawdza spójność
rekordów, ich połączenie z bazowym audytem i liczniki; nie ocenia samodzielnie
prawdziwości stron internetowych.

## Oddzielne osie oceny

1. Pisownia i odnotowanie jednostki: nowe dowody dla 15 pozycji.
2. Polskie użycie: słownik/cytaty lub tekst właściciela produktu, jawnie rozróżnione.
3. Odmiana: wyłącznie źródłowe formy; brak pełnego paradygmatu nie jest uzupełniany.
4. Częstość: wartości zamrożonego wordfreq zachowano dla starych kandydatów.
   Dla pięciu nowych pozycji jest null, nie zero. Brak nowego pomiaru korpusowego.
5. Instalacja: brak nowych zatwierdzeń. Potrzebne mapowanie dowodów spoza SGJP,
   sprawdzenie homonimów/kapitalizacji, dobór wag i pomiar metadanych.

Nie zmieniło się 1336 wcześniej potwierdzonych wpisów ani 911 odrzuconych przez
starą politykę częstości. Nie podajemy 1351 jako liczby gotowych wpisów:
15 źródłowo wspartych pozycji należy do innego etapu weryfikacji.
Koszt nowych metadanych pozostaje null, a nie 0. Poprzedni pomiar wolnego miejsca
(4365 wpisów po symulowanym dodaniu 1336) nie obejmuje obecnej partii.

## Powtarzalność

```bash
python scripts/reconcile_practical_evidence.py \
  --decisions build/practical-audit-reproduced/decisions.jsonl \
  --observations source/practical-evidence-v2/observations.json \
  --probes build/practical-audit-reproduced/coverage-probes.json \
  --out build/practical-evidence-new
```

Katalog wyjściowy musi być nowy. Skrypt zapisuje SHA-256 wejść i osobne wyniki
uzupełnienia. Nie pobiera stron na nowo: przyszły ponowny odczyt może wykazać
zmiany źródeł i wymaga osobnej wersji obserwacji. Hash obserwacji identyfikuje
nasz zapis, nie pełną zawartość strony wydawcy.

Dalsza kolejka: pozostałe 654 klucze, dowody częstości dla nowych słów,
konwersja zweryfikowanych danych do metadanych bez domyślania znaczeń.
Użytkownik nie musi przeglądać ręcznie list.
