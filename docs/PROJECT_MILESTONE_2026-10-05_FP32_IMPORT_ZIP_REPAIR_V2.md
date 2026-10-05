# Kamień milowy: naprawa importu ZIP FP32
Data: 2026-10-05. Status: poprawka wysłana, CI i ponowna próba na telefonie oczekują.

## 1. Wersje i zakres
Runtime jakamilek/CleverKeysPL: trial/herbert-fp32-benchmark-v1, commit 884a29b72e8673ad57e506c3d3d2d174e5cd329f.
Run naprawy: https://github.com/jakamilek/CleverKeysPL/actions/runs/37280833641 — podczas pojedynczego sprawdzenia in_progress, bez wyniku.
Producent jakamilek/CleverKeys-langpack-pl: zamrożone źródło d831e17b6cb99590d6ba036e92a72b6c3fd0cc7c i udany run 37230171787 pozostają bez zmian.
Ten identyczny checkpoint w obu main zmienia wyłącznie dokumentację. Bez merge, wydania, tagu, podbicia wersji ani promocji kodu próbnego na main.

## 2. Stan przyjętej architektury
Geometric i codzienne podpowiedzi pozostają bez zmian; SI działa tylko na przygotowanych przykładach na osobnym ekranie diagnostycznym.
Domyślny kontekst 32 słowa, maksimum 64/4096 UTF-16; test porównuje czas, nie jakość okien. Planowany kontekst bieżącego pola przed kursorem zachowuje case i interpunkcję, bez historii pomiędzy aplikacjami.

## 3. Zgłoszenie telefonu
Użytkownik zgłosił nieudany import. Ekran starego APK pokazywał jedynie „Import nie powiódł się. Wybierz zweryfikowany ZIP testowy i sprawdź wolne miejsce”.
Wyjątek był ukrywany przez ogólny catch. Nie ustalono dokładnego wyjątku na Nubii ani wolnego miejsca czy pełnego pobrania ZIP-a. Nie przypisujemy winy użytkownikowi i nie twierdzimy, że telefon już potwierdził naprawę.

## 4. Odtworzony błąd zgodności
Workflow producenta używa upload-artifact z compression-level 0. Jego archiver/zip-stream przełącza pliki strumieniowe na STORED z flagą bit 3 i końcowym deskryptorem danych.
Dotychczasowy ZipInputStream odrzuca taki wpis: „only DEFLATED entries can have EXT descriptor”.
Na lokalnej paczce z 16 bajtami danych Java 17 odtwarza odrzucenie; ZipFile odczytuje dokładnie tę samą paczkę. Jest to dowód defektu formatu obsługiwanego przez importer, nie odczyt wyjątku z telefonu ani niezależna weryfikacja pełnego modelu.

## 5. Wprowadzona poprawka
HerbertZipArchive zapisuje ograniczoną kopię kontenera w nowym prywatnym noBackup snapshot i używa ZipFile. Przed otwarciem kontroluje EOCD, liczbę wpisów oraz rozmiar katalogu, aby ograniczyć pamięć parsera. Pakiet <4 GiB z siedmioma plikami nie potrzebuje multidisk ani katalogu ZIP64; lokalne pola ZIP64 odczytuje ZipFile.
Limit kontenera: suma rozmiarów siedmiu zaufanych plików plus 1 MiB narzutu. Nadal obowiązują dokładne nazwy, brak katalogów/duplikatów, komplet plików, rozmiar i SHA-256 każdego pliku oraz weryfikacja manifestu/tokenizera.
Kopia ZIP zostaje usunięta przed parsowaniem metadanych. Błąd lub anulowanie usuwa snapshot. Poprzedni import zastępujemy dopiero po sukcesie.

## 6. Informacja dla użytkownika
Preflight miejsca obejmuje kopię ZIP, rozpakowane pliki i rezerwę — około 1,33 GB. Polski ekran prosi o co najmniej 1,4 GB wolnego miejsca podczas importu; końcowy model pozostaje około 622 MiB.
Zamiast ogólnego błędu dostępne są kody STORAGE, READ, ZIP, CONTENTS, IDENTITY, METADATA z polską przyczyną i raportem przez „Kopiuj raport”. Anulowanie ma oddzielny status.
Raport używa wyłącznie stałych kodów, tłumaczenia i tożsamości telefonu/Androida. Nie zawiera surowego wyjątku, URI, ścieżki, wybranego filename ani wpisanego tekstu.

## 7. Testy i ograniczenia sprawdzenia
Dodano siedem testów do zarejestrowanego HerbertBundleImportTest: STORED+deskryptor, dotychczasowy DEFLATED, odmowa zmienionych sum/duplikatów/traversal/braku plików, manipulacja o stałym rozmiarze, ograniczenia katalogu i kontenera, anulowanie kopii, budżet miejsca.
Małe pozytywne próbki badają czytnik kontenera i weryfikację SHA, nie uwierzytelniają fikcyjnego modelu. Zaufany hash pełnego FP32 pozostaje wymagany.
Lokalnie: rzeczywista próba Java formatu PASS, struktura 27 zasobów base/Polish i zgodność formatów PASS, kolejka TODO <500 linii. Nie ma lokalnego Kotlin/Android SDK; kompilacja, testy Kotlin, lint i nowe APK oczekują CI.
Zachowano obowiązkowe 2471 wektorów tokenizera /232 batche /532 kandydatów oraz istniejące testy edytora, lint i audyt APK.

## 8. Tożsamość modelu i wcześniejszego APK
Ten sam model ZIP:
https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/37230171787/artifacts/11312693984
657295441 bajtów; ZIP SHA-256 36c2183acca3ae6dca4afb54c28fe4d9d4cb37ec26f3230c94b4e007b494587f.
model.onnx: 651798883 bajty, SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
Siedem przypiętych tożsamości w HerbertBenchmarkTrial bez zmian. Allegro/herbert-base-cased, rev 50e33e0567be0c0b313832314c586e3df0dc2297, CC BY 4.0.
Starszy runtime run 37232458354 i APK artifact 11314463703 miały PASS wszystkich bramek CI, ale zawierają wadliwy czytnik. Nie są paczką z obecną naprawą. Nowego APK nie ogłaszamy przed udanym runem 37280833641.

## 9. Rzeczy odłożone
INT8 pozostaje FAIL (22 zmiany rankingu, 7 regresji top-1, 1 regresja top-3); nie osłabiono warunków.
Natywne wyniki modelu, czas i pamięć na Nubia Z60 Ultra LV 12/512 pozostają niezweryfikowane.
Niezależne konteksty jakości, opt-in SI, dispatcher, opcje modelu/kontekstu i trzy czasy Backspace pozostają na dalszej liście.
Dla tych samych 18 innych języków zapisano siedem nowych brakujących kluczy oraz zmienione opisy w backlogu. Polski ma pierwszeństwo; nie zmieniono globalnego lint.

## 10. Kolejny krok i monitoring
Użytkownik zachowuje pobrany model ZIP; potrzebna jest tylko instalacja nowego zweryfikowanego APK.
Po sukcesie CI: pobrać APK ARM64, zaktualizować aplikację, pozostawić >=1,4 GB wolnego miejsca i ponowić „Importuj ZIP z modelem”.
Jeżeli import się uda — uruchomić test i przekazać raport; jeżeli nie — skopiować nowy raport powodu importu.
Sprawdzono stan runu raz. Zgodnie z ustaleniem nie czekamy na CI w pętli; maksymalnie 60 sekund łącznie monitorowania/build, następnie zakończenie zgłasza użytkownik.

## 11. Różnica względem poprzedniego checkpointu
Poprzedni etap potwierdził dostępność APK i host/JVM conformance, lecz nie ćwiczył formatu pełnego ZIP-a upload-artifact przez importer na telefonie. Obecne zgłoszenie ujawniło tę lukę i brak diagnostyki.
Naprawiono obsługę potwierdzonego problematycznego formatu, dodano regresje i bezpieczny raport błędów. Kod i model SI, identyfikatory źródła oraz zachowanie edytora pozostają bez zmian. Pełna próba urządzenia jest nadal warunkiem dalszej decyzji.
