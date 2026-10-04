# Globalna kapitalizacja i metadane homonimów — langpack v5

## 1. Zweryfikowany stan i data
2026-10-04. Przed dokumentem main CleverKeysPL:
2e70db8b53563c05c39398a436fec4d8e005fdd2; main CleverKeys-langpack-pl:
93ea8fd86a14c8fc9b9f4a869dd426ea61b33521. Oba mainy otrzymują tylko ten dokument.
Producer feature/source-variants-trial-v1 przesunięto fast-forward z
bb55e87f5bfa2c7ce2a3eb2214cf5a7f3031205f do 041b28ae4587c531ef73e62933e9151cadb84c33.
Nowe drzewo: 8129d6d8456b0bf5df4734bf86b2e52e0328f328; wszystkie siedem zmienionych blobów
zgadza się z lokalnymi plikami i zostały odczytane dokładnie z nowego commita.
Runtime trial docs/source-variants-integration-v1 pozostaje na
4e51c3b45285fdbfdc93531bd80e228444601818, draft PR #1, bez nowego APK commita.

Wspólny zapis: [CleverKeysPL](https://github.com/jakamilek/CleverKeysPL/blob/main/docs/PROJECT_MILESTONE_2026-10-04_GLOBAL_CASING_V5.md)
i [CleverKeys-langpack-pl](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/main/docs/PROJECT_MILESTONE_2026-10-04_GLOBAL_CASING_V5.md).

## 2. Architektura
Audyt każdego CKDT key: obie sondy pierwszej litery, wyłącznie dokładne pojedyncze
formy połączone z generatorem tego samego lematu, pełnego tagu i klas NAME.
Zwykła poświadczona mała forma ma pierwszeństwo; nazwa zostaje alternatywą tego samego
wpisu. Wyłącznie nazwy zachowują dużą literę. Brak zgodnej formy zachowuje CKDT.
Skróty/camelcase poza małą/wielką pierwszą literą zachowują wejściową pisownię.

Pełny audyt JSONL zachowuje wszystkie interpretacje, tagi i dowody. Runtime grupuje
identyczne lemat/POS/NAME/kwalifikatory w lexicalReadings z formami; variantCategoryIds
łączy pisownię i klasy źródła. Łącze provenance.fullAudit podaje SHA i klucz surfaceKey.
Dziewięć dotychczasowych wpisów zachowuje wcześniejsze bogate dowody/GUS.
API v1 pozostaje bez zmian: metadata jest opcjonalnym obiektem opaque.
Wspólny resolver przyszłych buildów rozszerza priorytet zwykłej formy na wszystkie
poświadczone POS; reguła funkcyjna pozostaje wcześniejsza dla zgodności raportu v4.

## 3. Zaakceptowane ustalenia i przyczyna
Użytkownik potwierdza działanie aktualizacji v4, lecz odrzuca jej ograniczony zakres
i żąda globalnej obsługi informacji o zwykłym słowie i odmianie nazwy. Zgłasza Tutaj
w środku zdania. V4 nie był listą dwóch wyjątków: obejmował całą kategorię funkcyjną,
lecz nie eksportował metadanych tych homonimów i nie obejmował wszystkich POS.
Przypięte źródło potwierdza tutaj/adv oraz Tutaj/nazwisko, ale/conj/part/interj
i Ale/imię, lub/conj oraz impt od lubić i Lub/imię/nazwisko od Luba:Sf.
Nie dopowiadamy opisów znaczeń ani ulic/miast na podstawie nazwiska.

## 4. Rozwiązania odrzucone
Brak blacklisty słów, ręcznych opisów, duplikowania CKDT przez case i nowej listy
ręcznych kategorii. Nie traktujemy sondy z dużą literą jako dowodu nazwy.
Nie zwiększamy limitów Androida ani nie wkładamy pełnego 81 MB audytu do importowanego ZIP.
Pełna nieskompaktowana wersja przekroczyła limit węzłów i została odrzucona.
Nie zmieniamy rangi na podstawie nieistniejących częstotliwości znaczeń.
Bez merge/tagu/release/promocji do main i zmiany wersji aplikacji.

## 5. Niewdrożone plany
Kontekstowe AI, korpusowe wagi poszczególnych interpretacji, pełna morfologia runtime
i szersze źródła dla nierozpoznanych form pozostają osobnymi etapami.
Nie wykonano pełnego głównego preview pipeline. Inne tłumaczenia pozostają w backlogu.
Globalny audyt nie oznacza metadanych wszystkich wyrazów w pamięci klawiatury:
runtime zawiera konflikty/poprawki/kontrole; pełna analiza wszystkich jest w audycie.

## 6. Weryfikacja i jej granice
42 testy lokalnie PASS: 21 istniejących wariantów, 8 funkcyjnych, 13 nowych.
Nowe obejmują prawdziwe homonimy, adv/czasowniki, nazwy, brak fałszywych wielkich form,
fragmenty, pełne tagi, audyt każdego klucza, CKDT/rangi, korelację source/runtime,
historyczne dane, determinizm, checksum i limit JSON. Python py_compile PASS.
YAML i powiązanie test/build/summary/artifact PASS, 14 kroków workflow.

Niezależny przegląd całego realnego CKDT potwierdza klucze/kolejność/rangi,
nagłówek/lookup/unigrams i niezmienione dziewięć historycznych wpisów.
Dwa buildy mają identyczne ZIP, report, pełny audyt i summary.
Struktura wszystkich 16199 wpisów odpowiada kontraktowi kluczy/case/manifestu
odczytanemu z runtime; to kontrola hostowa, nie wykonany parser Androida.
Sidecar 11542814 bajtów / 751535 węzłów mieści się w
32 MiB / 1 000 000 / 120 000 wpisów bez podnoszenia limitów.
Nowego CI, bieżących runów runtime i artefaktu v5 nie odczytywano ani nie monitorowano.
Import, parser Androida, pamięć/start i telefon v5 pozostają do potwierdzenia.
Limit monitorowania 60 sekund łącznie na build obowiązuje.

## 7. Gałęzie i historia
Producer trial nowy commit 041b28ae4587c531ef73e62933e9151cadb84c33; runtime v15 i draft PR #1 bez zmian.
V4 ZIP pozostaje identyczny i zaakceptowany na telefonie pod względem korekty,
ale użytkownik żąda szerszego modelu danych. Poprzedni producer run 37188544526
był wcześniej potwierdzony SUCCESS; nie dowodzi nowego v5.
V14 poprawka SimpleX i v15 reset listy zachowują oczekujące wyniki/telefon.
W tym etapie nie odczytywano ich Actions ani nie kasowano/ponawiano runów.

## 8. Artefakty, hashe i integracja
Pack version 5, 106363 kluczy, 736 korekt (673 na małą,
63 na wielką literę), 16199 wpisów sidecara. Źródłowych par
16117, w tym 15977 zwykłe/nazwa.
Źródłowe pokrycie 102135; bez zgodnej formy 4228.
455 canonical forms poza obsługiwanym wzorcem case
zachowuje wejściową pisownię; liczba par audytu nie jest gwarancją par dla wszystkich skrótów.

Lokalny cleverkeys-pl-global-casing-trial.zip: 1713402 bajty.
ZIP SHA aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb
CKDT SHA a32f6a55bce7375e744d3d261d6ec9aad96dc64725ac429d4cb1d7225aed3c2a
sidecar SHA 5e0eac9b056861903d33664c6ba3d4a9d895044530e78be72ff0ad1596ba884d
pełny audyt SHA 06031fee57cc32b6c795cc36f0a728449e7bc7bd841b09bb23d0fb33012c7454
lista zmian SHA 50215963bff5ed9ab0332202309181b26ff7257b51ea51c2e267c6c323c1de3d
Audyt JSONL ma 81566499 bajtów, jest osobnym plikiem artefaktu.
Nie są to hashe/ID jeszcze potwierdzonego artefaktu GitHuba.

Workflow ma wydać artifact cleverkeys-pl-global-casing-trial z wewnętrznym ZIP,
raportem, audytem i summary. Raport v4 zmienił tylko fingerprint resolvera;
jego ZIP SHA 3767c76dbf87589182d6b26b8f8d64d80ec635764cee15d350015b60d41e21af
pozostaje identyczny. CI v5 porównuje summary z zatwierdzonym wynikiem i hashem pełnej listy.
[Specyfikacja v5](https://github.com/jakamilek/CleverKeys-langpack-pl/blob/041b28ae4587c531ef73e62933e9151cadb84c33/docs/GLOBAL_CASING_TRIAL_V1.md).

## 9. Ograniczenia
Źródło Morfeusz 1.99.15 / SGJP 2026.06.01 jest przypięte, nie zastępuje wszystkich baz.
Nierozpoznane i nieprzedstawialne formy nie są zgadywane. Domyślna mała forma jest
polityką użytkową, nie zmierzoną przewagą częstotliwości interpretacji.
Metadane przygotowują przyszły kontekst; obecnie AI ich nie konsumuje.
Większy sidecar wymaga testu importu, startu i płynności na telefonie; zgodność limitów
nie dowodzi kosztu pamięci ani akceptacji UX. Pisownia użytkownika może mieć pierwszeństwo.
Nie kasujemy jego danych. Osiem dawnych par i kontrola łódzki zostają.

## 10. Następny krok
Po zgłoszeniu zakończenia runów sprawdzić właściwe commity, testy i artefakty.
Dla producer v5 importować wewnętrzny cleverkeys-pl-global-casing-trial.zip,
nie zewnętrzny wrapper z audytem. Sprawdzić w środku zdania ale/lub/tutaj:
mała forma domyślna i nazwa obok, a następnie Jan, Łódź/łódź, Shift/kropkę,
restart i płynność po większym imporcie. Jeżeli nadal dominuje pisownia użytkownika,
zbadać ją bez automatycznego kasowania słownika.
Dokończyć oczekujące testy SimpleX i resetu paska na runtime v15.

## 11. Różnica względem poprzedniego kamienia
[Poprzedni v15 runtime](PROJECT_MILESTONE_2026-10-04_WORD_STRIP_V15.md)
dotyczył resetu paska i dostarczenia v4. Ten etap zmienia wyłącznie producer:
audyt wszystkich kluczy, ogólną politykę POS oraz automatyczny eksport interpretacji
i wariantów dla konfliktów. Zastępuje ograniczony zakres
[korekty funkcyjnej](PROJECT_MILESTONE_2026-10-04_FUNCTION_WORD_CASING.md)
nowym packiem v5; runtime/API, rangi i klucze pozostają. Lokalnie 42 PASS,
CI/import/telefon oczekują.
