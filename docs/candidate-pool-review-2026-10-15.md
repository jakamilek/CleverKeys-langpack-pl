# Ocena wspólnej puli kandydatów — 15.10.2026

V11 pozostaje bez zmian; nie zbudowano nowego langpacka ani APK. Oceniono całą pulę 7570 kluczy, z zachowaniem wcześniejszych 911 kandydatur o niskiej częstości. Nie odrzucano kandydatów z powodu limitu miejsca.

## Wyniki

| Wynik automatycznej oceny | Liczba |
|---|---:|
| Dowód SGJP i pierwotne reguły częstości | 1360 |
| Dowód SGJP i obniżony próg Zipf ≥1 | 1775 |
| Dowód SGJP, ale częstość poniżej progu | 2295 |
| Nazwy, marki i skrótowce: ocena tożsamości i pisowni | 99 |
| Rozbieżność kapitalizacji źródłowej | 7 |
| Poza profilem SGJP: nazwy własne, dawne/regionalne odczytania lub skróty | 157 |
| Wcześniejsze dowody zewnętrzne: potrzebne mapowanie metadanych | 33 |
| Polskie hasło słownikowe; dalsza kontrola odmiany i przydatności | 1776 |
| Hasło z ostrzeżeniem redakcyjnym | 7 |
| Przekierowanie wymagające sprawdzenia celu | 0 |
| Strona bez rozpoznanej polskiej definicji | 8 |
| Dotąd brak wystarczającego dowodu leksykalnego | 53 |

Kategorie są rozłączne i sumują się do 7570. „Poza profilem” nie oznacza błędnego słowa: może chodzić o historyczne znaczenie, nazwę lub regionalizm. Brak częstości nie dowodzi zbędności. Żadna nowa kandydatura nie została zatwierdzona do instalacji.

## Co sprawdzono źródłowo

Pobrano **2138 zapisów haseł** z Wikisłownika dla kandydatur bez zgodnego nowoczesnego odczytania SGJP. Znormalizowanych odpowiedzi o stronach: 2138; polską sekcję z numerowaną definicją rozpoznano w 1954; brakujących stron: 170; przekierowań: 0. To liczby stron, nie dodatkowych słów.

Zapisano surowe odpowiedzi, rewizje i sumy SHA-256. Parser rozdziela języki, definicje, ostrzeżenia redakcyjne, kwalifikatory, przykłady i dosłowne komórki tabel odmiany. Przykłady i przypisy są wskaźnikami do dalszej kontroli — ich treści i przywołanych publikacji nie uznajemy automatycznie za niezależnie sprawdzone.

Dla słów z dowodem SGJP ponownie oceniono zapisane odczytania i kwalifikatory oraz powiązanie z częstymi formami tej samej rodziny w v11. Zachowano klucz kotwicy i częstość. Nie korzystano z modelowej oceny znaczeń jako dowodu.

## Korekta kwalifikatorów

Dotychczasowy filtr sprawdzał początek etykiety, przez co mógł przeoczyć kwalifikator po przecinku. Nowy filtr rozdziela składniki. Dotyczy to kandydatur: abakus, alkowa, bajdura, ruchawka. Trzy z nich miały Zipf ≥1, jedna wynik poniżej progu. To przesunięcie do kontroli profilu, nie stwierdzenie błędu pisowni. Wcześniejsza grupa 1336 potwierdzonych form nie utraciła potwierdzenia z tego powodu.

## Scenariusz roboczy i koszt

Łącznie **3135 kandydatur** ma zgodne odczytanie SGJP, źródłową pisownię i Zipf ≥1 (z zachowaniem wcześniejszych reguł rodzin). W porównaniu z wczorajszym scenariuszem 3138 to trzy pozycje mniej. Dokładny koszt dopisania ich metadanych w pamięci: **562007 bajtów**, **34871 elementów JSON**. Pozostaje **2566 miejsc**, **163792 elementów JSON**, **4396252 bajtów**. Koszt nie obejmuje nowego opisu pochodzenia etapu; nie jest pomiarem RAM telefonu. Nie zapisano paczki instalacyjnej.

Zachowano też wcześniejsze obserwacje WSJP, Dobrego słownika, Obserwatorium Językowego UW i stron producentów; brak nowego hasła w Wikisłowniku nie kasuje tych dowodów. Te obserwacje nie zostały dziś ponownie pobrane.

Ta grupa nie jest automatyczną rekomendacją wszystkich słów. Częstość dotyczy zapisu, a nie zawsze konkretnego znaczenia. Kwalifikatory potoczne, żartobliwe, pejoratywne i wulgarne zachowano do oceny, bez automatycznego usuwania. W grupie roboczej 22 klucze mają co najmniej jedno odczytanie z etykietą wulg.; to wyodrębniona kwestia polityki podpowiedzi, a nie powód ukrytego odrzucania danych.

## Dalsza kolejność

Najpierw rozstrzygamy hasła już wsparte definicją lub zewnętrzną obserwacją źródłową, ale bez mapowania metadanych; następnie słowa o niskiej częstości należące do częstych rodzin. Przekierowania, redakcyjne ostrzeżenia i sprzeczność profili pozostają osobnymi kolejkami. Nie potrzeba ręcznego przeglądu całej listy przez użytkownika.

Nie utożsamiać obecności w Wikisłowniku z potwierdzoną współczesną przydatnością. Hasło może być regionalne lub historyczne. Brak polskiej sekcji może oznaczać brak opracowania, nie błąd zapisu. Nie sprawdzono na nowo wszystkich witryn producentów aplikacji ani korpusowej częstości znaczeń.

## Odtwarzanie i weryfikacja

Repozytorium CleverKeys-langpack-pl, gałąź audit/practical-candidates-v11. scripts/review_candidate_pool.py --base /ścieżka/v11.zip --out build/pool-review używa zamrożonych stron; --fetch pobiera brakujące partie. Następnie scripts/render_pool_review.py /ścieżka/v11.zip. Wersja wordfreq i commit są kontrolowane; ścieżki wejść i sumy znajdują się w report.json. Odczytania SGJP pochodzą z wcześniejszego przypiętego audytu, a nie z nowego pobrania słownika.

Sprawdzono na rzeczywistych snapshotach cztery istotne zachowania parsera: niemieckie ADAC nie staje się polskim hasłem; abandonware ma polską definicję; ajlauf zachowuje ostrzeżenie do weryfikacji; abwera zachowuje dosłowną formę abwery w dopełniaczu. Walidacja bazy i symulacji sprawdza sumę v11 oraz unikalność kluczy. Historycznych 97 testów nie uruchamiano ponownie.

Snapshoty Wikisłownika: CC BY-SA; rewizje i odnośniki do historii autorstwa wskazują dictionary-pages/lock.json oraz rekordy dictionaryPages. Prywatny słownik nie był wejściem analizy.
