# Kolejna część odłożonych nazw — v12

**Odłożone decyzją użytkownika 2026-10-13.** Bazą pozostaje zaakceptowana v11.
Poniższy wynik zachowujemy jako audyt; zamiast dalszych nazw przygotowujemy
moduły kandydatów codziennego słownictwa i współczesnych terminów.
Nie przekazujemy tej paczki do instalacji.

## Baza i zakres

V11 została zaakceptowana na telefonie: „działa dobrze”. Runtime CleverKeysPL
0b94e323789e96c44a77f762a6f83fa11e285699 przeszedł runy 38437360577 i 38437368829:
2931 testów pure, 51 importu, integracje edytora, zgodność oryginalnego tokenizera
HerBERT, gate 192 MiB, lint debug/vital i kontrolę APK. APK SHA-256:
`af22cd26bbd2dc943d01286672c7caa19df5d42ec10f5364e691d1cb022696eb`.
V12 używa tego samego zainstalowanego APK; nie zmienia modelu, gestów, ustawień,
polityk kapitalizacji ani limitów. Ogólne potwierdzenie telefonu nie jest
pomiarem PSS, czasu ani wszystkich oddzielnych ścieżek Menedżera słownika.

Wejście: wewnętrzny ZIP v11 z udanego runu 38437507820, SHA-256
`8169a8ac33261fc245d46a344193759a0c1a84b0eb49cf2436e46ccaed90a229`.
Zachowujemy wszystkie 204 463 słowa, 114 299 wpisów metadanych, bajty rang,
kanoniczną pisownię, warianty, pełne dane źródłowe i unigrams.
Prywatny eksport nie jest źródłem ani listą wyjątków.

## Skąd ta pula

To dalszy ciąg grupy 8, a nie nowa baza imion/miejscowości. Oryginalna próba v8
badała 300 000 całych alfabetycznych kluczy polskiego wordfreq. SGJP/Morfeusz
potwierdził źródłowe lematy nazw, marek i skrótowców; ich paradygmaty wygenerował
SGJP. Każda forma ponownie przechodzi dokładną analizę/generowanie całego słowa,
zgodność lematu, taga, NAME i LABELS. Nie generuje ich SI. Kandydatura dowodzi
poprawności źródłowej, nie powszechności użycia ani aktualnego statusu miejscowości.

Pula została zamrożona w `name-forms-audit.jsonl` z runu 38167348861,
SHA-256 `18af9ce13103aeb969c6079729574ec327e8e4326daf9c5b5f3753b4c33177`.
V8 odłożyła 124 217 form z powodu pojemności; v10 przyjęła 13 650 z nich.
V11 zmieniła tylko reprezentację. Pozostało 110 567 kwalifikowanych kluczy.
Źródła nadal: Morfeusz2 1.99.15 / `pl.sgjp.sgjp-2026.06.01`, wordfreq 3.2.0
commit `912caf64b657478d1dff1138efdc078947d54bb1`; sprawdzamy instalacyjne
wersje i commit. Dotychczasowe źródłowe wykluczenia imion, fragmentów nazw,
przestarzałych/nieleksykalnych odczytań i dominujących obcych kolizji pozostają.

Najpierw mierzymy całą pozostałą pulę, potem wybieramy według dotychczasowej
kolejności grup i malejącej częstości. Obecne słowa pomijamy po dokładnym
małoliterowym kluczu; ogonków nie składamy. Nie dodajemy opisów znaczeń.
Każdy instalowany nowy klucz ponownie weryfikujemy w przypiętym natywnym SGJP.
Reguły częstości i rangi nowych form pozostają te same co w v8/v10.

## Wynik

204 463 + 5701 = **210 164 słowa**. Wszystkie starsze rekordy CKDT/rangi,
wzajemna kolejność wcześniejszych accent-map i zakodowane wpisy metadanych
pozostają zachowane. Nowe formy mogą zmienić konkurencję gestów, więc to
nie deklaracja niezmiennej kolejności podpowiedzi ani poprawy każdej próby.

Klasy dodatków zachodzą na siebie: 3888 nazwisk, 1887 nazw geograficznych,
570 imion, plus drobniejsze klasy zapisane w raporcie. Nie sumujemy tych liczb.
Następna partia jest rzadsza: Zipf 1,32–1,54. To pomiar istniejącego wordfreq,
nie ręcznie ustalona preferencja nazw. Przykłady z wyniku: Kuczkowski,
Krysztofiak, Kłosowicz, Lehara, Majkowska, Matusiaka, Kryłowa, Luboszyce.

API/schema3, packVersion12. Te same 242 atrybuty i 30 674 rekordy źródłowe
zachowują treść/indeksy. Nowe odczytania używają dokładnie zgodnych istniejących
referencji oraz masek pisowni v11, z literalnym fallbackiem. Brak pola/pusta
lista, kapitalizacja, sufiks lematu, POS, NAME i LABELS pozostają odrębne.
Nie przepisujemy wcześniejszych wpisów. 10985 nowych odczytań używa surfaceMask,
1045 sourceRef, 9272 sourceAttributesRef. Źródłowe nazwowe homonimy zwykłych
wyrazów pozostają w dowodach; nie wymuszamy ich kapitalizacji.

Metadane: 120 000 wpisów, 30 380 178 bajtów, 1 904 279 węzłów.
Pozostaje 95 721 węzłów, ale 0 miejsc do niezmienionego limitu 120K wpisów.
104 866 kwalifikowanych form nadal pozostaje odłożonych. Dalsza rozbudowa
wymaga osobnego rozwiązania limitu liczby wpisów i pomiaru, a nie usunięcia
starszych słów lub bezwarunkowego podniesienia limitów w tej paczce.

## Walidacja i dalszy test

90 testów producenta oraz 34 rzeczywiste testy parsera PASS. Pełny niezależny
zimny czytnik schema3, aktualizacja i legacy schema1 każdej nowej źródłowej
postaci potwierdzają wszystkie dane. 114 299 dawnych niezmiennych wpisów jest
współdzielonych przy podmianie. Prezentacja dotychczasowych rodzin pozostaje
zgodna. Realne zimny odczyt/v11→v12/ponowny-v12 z 16 MiB balastu w osobnych
JVM 192 MiB PASS. To nie Android PSS, dokładny szczyt RAM ani ocena jakości SI.

CI przypina oba wejścia i dokładny niezmieniony czytnik APK, reprodukuje cały
`reviewed-report.json` i wymaga wszystkich bramek przed artefaktem. Nowe CI
oraz próba telefonu pozostają do potwierdzenia. Po CI dostarczamy wyłącznie
wewnętrzny ZIP langpacka; audyt i oczekiwane niezakodowane nowe wpisy są poza nim.
Sprawdzić import/reimport/licznik 210164, przykładów nowych gestów i dziewięciu
wcześniejszych braków, odmiany/kapitalizację z SI oraz Menedżer po restarcie.

Paczka SHA-256 `bd743d0cc3ca91ef93173239532eb9115d4fea6e2f564b762392b6fe76c19b1a`.
Dalsze porównanie prywatnego słownika pozostaje lokalne i oddzielne; nie usuwamy
z bazowego słownika. Bez merge/tag/release. Actions monitorujemy najwyżej 60 s
łącznie na run, potem stan zgłasza użytkownik.
