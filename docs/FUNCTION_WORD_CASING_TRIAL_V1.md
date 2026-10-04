# Domyślna pisownia wyrazów funkcyjnych — trial v1

## Przyczyna

Pack v3 zawiera kanoniczne `Ale` i `Lub`, mimo zwykłych analiz `ale:C/conj`,
`ale:T/part` i `lub/conj`. Dawny resolver dawał pierwszeństwo formom imion:
`Ale` od `Ala` i `Lub` od `Luba:Sf`. Nie jest to błąd gestu ani kodu Shift.
Dziewięć wpisów metadanych nie obejmuje tych dwóch kluczy.

## Reguła oparta na źródle

Po dotychczasowych regułach rzeczownika pospolitego i przymiotnika, ale przed
nazwami własnymi i wtórnym źródłem NKJP, zwykła analiza funkcyjna ustala małą
literę jako domyślną. Wymagane: dokładna forma w sondzie małymi literami,
brak klasy NAME oraz POS `conj`, `comp`, `part` lub `prep`. Nie ma listy
ręcznych wyjątków. Interpretacje nazw własnych pozostają w raporcie decyzji.
Znaczniki są danymi SGJP; [dokumentacja Morfeusza](https://morfeusz.sgjp.pl/doc/about/)
opisuje klasę gramatyczną na pierwszej pozycji znacznika.

Zmiana nie obejmuje dowolnych rzeczowników, czasowników, skrótów ani słów
nierozpoznanych. Nazwy takie jak Jan zachowują dotychczasową regułę.

## Poprawiony pakiet

`build_variant_trial.py` nadal odtwarza pierwotny pack v3 bez zmiany CKDT.
Nowy, jawny etap `build_function_word_trial.py` przyjmuje wyłącznie ten pack
(przypięty SHA-256) i Morfeusz 1.99.15 / SGJP 2026.06.01. Wersja packa rośnie
do 4; wersja aplikacji pozostaje bez zmian. Etap modyfikuje wyłącznie pisownię
kanoniczną 18 form poświadczonych przez nową regułę. Nie dodaje wpisów.

Każda zamiana ma identyczną długość UTF-8. Pozostają niezmienione: nagłówek,
kolejność i klucze słownika, bajty rang, indeksy, sekcje normalizacji i mapowania
akcentów, unigrams oraz cały dziewięciowpisowy sidecar. Weryfikacja blokuje
konflikt z domyślną formą w zamrożonych metadanych. Provenance sidecara nadal
opisuje historyczne źródło jego dziewięciu wpisów; bieżący hash CKDT podaje
oddzielny [raport korekty](function-word-trial-v1/function-word-trial-report.json).
NOTICE zachowuje atrybucję i jawnie podaje modyfikację snapshotu.

Workflow `variant-trial.yml` wykonuje 29 testów (21 dotychczasowych, 8 nowych),
buduje oba etapy i porównuje wynik z zatwierdzonym raportem. Lokalnie wszystkie
29 testów zaliczono; dodatkowo niezależnie porównano wszystkie 106363 klucze
i rangi na rzeczywistym packu. CI i telefon wymagają osobnego potwierdzenia.

## Import i test telefonu

W już zainstalowanej klawiaturze zaimportować `cleverkeys-pl-function-words-trial.zip`
jako aktualizację polskiego pakietu. APK nie wymaga zmiany. Po odświeżeniu
słownika sprawdzić zwykłe słowa w środku zdań: `chcę ale nie mogę`, `kawa lub herbata`,
`chcę tylko wodę`, `zostaję ponieważ pada`. Sprawdzić też początek zdania po
kropce, ręczny Shift oraz `Łódź/łódź`, `Malina/malina`, `Warszawska/warszawska`.
Jeśli wyraz jest zapisany z wielką literą w słowniku użytkownika, jego świadomy
wybór może nadal mieć pierwszeństwo; nie usuwamy danych użytkownika.

## Granice

To korekta zamrożonego preview, nie pełna regeneracja wszystkich źródeł.
Reguła głównego resolvera została również naprawiona dla przyszłych buildów,
ale pełnego pipeline preview nie uruchomiono w tym etapie. Nazwy homonimiczne
poprawionych słów są dostępne przez Shift lub własną pisownię użytkownika;
nie dodano dla nich nowych par w metadanych paska. Ocena kontekstu AI pozostaje
odrębnym planem. Nowy pack zachowuje dotychczasowe osiem par i jeden przymiotnik
o pojedynczej formie. Nie zmieniamy zaakceptowanej obsługi edytora i gestów.
