# Dowody zewnętrzne i odmiana kandydatów — 15.10.2026

Baza: zaakceptowane v11. Pula pozostaje 7570 kluczy; w tym etapie nie dodano nowych kandydatur, nie wybrano słów do instalacji i nie zbudowano APK ani langpacka.

## 33 pozycje z wcześniejszymi dowodami zewnętrznymi

Ponownie pobrano sześć stron: WSJP PAN (powerbank, hasztag z wariantem hashtag), Dobry słownik (streaming, streamować, googlować), Obserwatorium Językowe UW (scrollować). Odczytano publiczne tabele i listy form oraz dosłowne wyróżnienia w cytatach. Nie kopiowano końcówek między wyrazami.

| Rodzina | Badane klucze | Dowód |
|---|---:|---|
| powerbank | 9 | tabela przypadków i liczby |
| streaming | 8 | jawna lista form; bez przypisywania przypadków |
| googlować | 5 | jawna lista form i gramatyka hasła |
| streamować | 5 | jawne listy form dla dwóch odrębnych znaczeń |
| hashtag / hashtaga | 2 | wariant pisowni i cytat; bez przenoszenia odmiany hasztag |
| scrollować i trzy formy | 4 | hasło i cytaty; brak kompletnej gramatyki form |

**27** kluczy ma potwierdzone powiązanie z formą wymienioną w tabeli/listach odmiany. **6** ma dowód częściowy z wariantu lub cytatu. Z 27 potwierdzonych **8 ma Zipf ≥1**, a **19 poniżej progu**. Niska częstość nie dowodzi zbędności tych form. To osiem konkretnych pozycji: googlować, googluje, powerbank, powerbanki, streaming, streamingu, streamować, streamuje.

Nie utożsamiamy listy form z pełnym opisem każdej kategorii gramatycznej. Tabelka przypadków streaming jest oznaczona przez serwis jako dostępna w abonamencie; wykorzystano tylko publiczną listę form, bez obchodzenia ograniczenia. U czasowników nie zgadywano osoby ani liczby na podstawie końcówki. Zachowano dwa identyfikatory znaczeń streamować. Łącznie dla 33 kluczy zapisano 38 odczytań źródłowych.

Dla scrollujesz obecny cytat ma zapis Scrollujesz. Zachowano tę obserwację i oznaczono brak dosłownego potwierdzenia wariantu małą literą w tym materiale; nie ukryto normalizacji. Pełny paradygmat nie jest deklarowany.

## Projekty metadanych i koszt

Przygotowano 33 projekty z dokładnymi źródłami, datą pobrania, hashami stron, selektorami, formami i zakresami potwierdzenia. Nie dopisano definicji ani etymologii od modelu. Dane z nowych słowników są osobno od odczytań SGJP.

| Scenariusz względem v11 | Wpisy | Bajty metadanych | Elementy JSON |
|---|---:|---:|---:|
| Potwierdzone tabelą/listą, Zipf ≥1 | 8 | 5359 | 201 |
| Wszystkie potwierdzone tabelą/listą | 27 | 17199 | 648 |
| Wszystkie projekty, również częściowe | 33 | 20499 | 769 |

Koszt zmierzono przez rzeczywistą serializację w pamięci. Zawiera pochodzenie przy każdym wpisie, ale nie nowy opis etapu. Wszystkie dotychczasowe wpisy v11 porównano po odczycie i pozostały niezmienione.

**To projekty danych, nie gotowa integracja z silnikiem.** Sprawdzono kod czytnika z commitu v11 0b94e323789e96c44a77f762a6f83fa11e285699. Zachowuje dowolne dane metadata, ale jego mechanizm relacji lematów odczytuje sourceEvidence, nie nową sekcję externalLexicalEvidence. Dlatego te projekty nie uzyskują automatycznie powiązania rodzin w silniku. Nie przeprowadzono nowego testu Kotlin/Android i nie deklarujemy poprawy podpowiedzi ani gotowości do importu.

## Dalsze 1776 haseł

Wykorzystano już pobrane i zweryfikowane sumami kontrolnymi snapshoty Wikisłownika. Porównano kandydata z dosłownymi komórkami tabel:

- **741** kluczy jest zapisanych dokładnie w komórce tabeli przypadków; z nich **179** ma Zipf ≥1, **562** niższy wynik.
- **52** ma różnicę wielkości liter względem komórki tabeli — zachowano oba zapisy do kontroli.
- **983** nie ma prostych komórek wyodrębnionych przez ten parser. Nie oznacza to braku odmiany w źródle: parser nie rozwija szablonów i nie odgaduje ich wyników.

Wśród 741 pozycji dla **721** zachowano jawny zakres znaczeń przypisany do tabeli; **20** ma mapowanie częściowe, np. dodatkowy szablon nieodmienności lub brak prefiksu zakresu. W pierwszej grupie **171** ma Zipf ≥1. To kolejka z mocniejszym dowodem odmiany, nie lista 171 nowych akceptacji. Zakres znaczeń pozostaje dosłownym oznaczeniem źródła, także gdy wskazuje grupę znaczeń. Nie deklarujemy sprawdzenia wszystkich znaczeń danego hasła.

Przykłady w materiale wymagające zachowania różnic: carbonara ma oprócz tabeli rzeczownika także nieodmienne użycie przymiotnikowe; malware ma dodatkową informację o nieodmienności. Nie wolno sprowadzać takich zapisów do jednego automatycznie wymyślonego odczytania. Są oznaczone jako częściowe.

## Odtwarzanie i pliki

- source-facts.json: 38 faktograficznych odczytań z sześciu stron; bez pełnych artykułów.
- metadata-drafts.jsonl: 33 projekty i ich statusy.
- dictionary-morphology-queue.jsonl: 1776 ocen tabel, z adresami i rewizjami źródeł.
- sense-scoped-case-evidence.jsonl: 741 powiązań z tabelą i oryginalnym zakresem znaczeń.
- report.json i pliki *summary.json: liczniki, koszty i hashe.

Skrypty: prepare_external_33.py, triage_dictionary_morphology.py, map_dictionary_case_evidence.py. Pierwszy odtwarza projekty z zachowanych faktów; --extract odczytuje lokalne HTML, a --extract --fetch pobiera brakujące strony i ponownie uruchamia ekstrakcję. HTML stron komercyjnych użyto tylko jako materiału roboczego; paczka zawiera fakty, hashe i selektory. Zmiana treści strony przy kolejnym pobraniu powinna być osobnym audytem.

Walidacja: 33 unikalne klucze, 38 odczytań, 27 powiązań tabelarycznych/listowych, brak tych kluczy w v11, zachowanie wszystkich dotychczasowych metadanych po serializacji, osobne dwa znaczenia streamować, brak dopisanych przypadków dla streaming. Dodatkowo 741 rekordów odsyła do snapshotów z kontrolą SHA-256. To nowe kontrole danych, nie ponowne wykonanie historycznych 97 testów. Prywatnego słownika nie używano.
