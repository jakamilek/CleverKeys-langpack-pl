# Bezstratny zapis źródłowych form v11

Baza to zaakceptowana na telefonie paczka v10: 204 463 słowa, 114 299 wpisów metadanych,
30 387 503 bajty i 1 999 999 węzłów. Wszelkie wcześniejsze słowa, rangi, warianty
kapitalizacji, dane źródłowe i unigrams.txt zostają zachowane. Nie dodajemy słów,
znaczeń, końcówek ani wyjątków. Prywatny eksport nie jest wejściem.

Wejście: wewnętrzny ZIP z [runu 38301095587](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38301095587),
SHA-256 `11dee57bc161bd18f1f8e0e6bbee80099a039a5240b70419f971fc297e4e78b7`.
Użytkownik potwierdził „działa bardzo dobrze”. CI PR 38301100893 również SUCCESS.

## Reprezentacja

Samo dalsze współdzielenie lematów odzyskuje 3382 węzły. Dlatego współdzielimy także
powtarzaną w odczytaniach źródłowych pisownię słowa. `surfaceMask` jest całkowitym
zbiorem bitów: 1=surfaceKey,2=pierwsza litera wielka ROOT + reszta klucza,
4=cały klucz wielkimi ROOT. Wybrane formy są unikalne i sortowane. Dopuszczamy 1..7;
nie dopuszczamy konfliktu z literalnym `surfaces`, booli, ułamków ani nadmiarowych
bitów. Odwołanie dotyczy wyłącznie klucza tego wpisu i nie nadaje SI nowej formy.

Skrypt używa maski tylko wtedy, gdy odtworzona lista jest dokładnie oryginalna,
włącznie z kolejnością i pisownią. Literały pozostają obsługiwane. Maski ograniczamy
do kluczy BMP bez surogatów i wybranych form o długości do 96; brak zgodności oznacza
zachowanie literalnej listy. Wszystkie 195 288 list źródłowych v10 spełniają ten warunek.

29 320 starych rekordów źródłowych i 242 atrybuty zachowują dokładne indeksy i treść.
Na końcu dopisujemy 1354 opłacalne, identyczne nagłówki; 4512 odczytań używa ich
odwołań. Lemat, sufiks, POS, NAME, LABELS, puste i nieobecne pola pozostają różne.
Każdy pełny rozwinięty wpis jest porównywany bajtowo przed zapisaniem ZIP-a.

Format deklaruje API 3/schema 3. Starszy APK odmawia importu; najpierw zaktualizuj
APK. Nowy czytnik zachowuje obsługę 1/2. Waliduje cały strumień i rozwinięty koszt
wpisu przed kopiowaniem. Podczas aktualizacji porównuje zwalidowane widoki danych
i może zachować stary niezmienny wpis mimo zmiany kodowania. Prefixy tablic są
współdzielone tylko po dokładnym porównaniu. Pełny rozwinięty słownik nie jest
buforowany. Stare kodowanie może pozostać w RAM do zimnego restartu; nie deklarujemy
natychmiastowego spadku pamięci po imporcie ani oszczędności pamięci HerBERTa.

## Wynik i walidacja

| Pomiar | v10 | v11 |
|---|---:|---:|
| Słowa | 204 463 | 204 463 |
| Wpisy metadanych | 114 299 | 114 299 |
| Bajty metadanych | 30 387 503 | 28 596 173 |
| Węzły | 1 999 999 | 1 801 337 |

Odzyskano 198 662 węzły i 1 791 330 bajtów. Pozostało 198 663 węzłów i 5701 wpisów
przy niezmienionych limitach 32 MiB/2M/120K. To nie gwarancja konkretnej liczby
następnych dodatków. Model, jego instrukcje, ranking, gesty i ustawienia są niezmienione.

84 testy producenta i 34 rzeczywiste testy parsera PASS. Pełne 204 463 rekordy CKDT
pozostają bajtowo identyczne; wszystkie 114 299 zimnych widoków, tożsamości źródłowe,
referencje aktualizowanych wpisów i prezentacja kapitalizacji/form PASS. Zimny
odczyt, v10→v11 i ponowny v11 +16 MiB balastu w osobnych JVM 192 MiB PASS.
Oryginalny test pamięci v1 również PASS lokalnie. To nie PSS Androida ani niezależna
ocena trafności SI. Android, integracja importu, lint, bieżące CI i próby telefonu
pozostają do weryfikacji.

CI przypina nowe źródła konsumenta i wejście v10, odtwarza dokładnie
[reviewed-report.json](reviewed-report.json) i wymaga wszystkich bramek czytnika
przed udostępnieniem artefaktu. Po CI dostarczamy APK i wewnętrzny ZIP.
Nie ma merge, tagu, release ani wersji aplikacji; Actions monitorujemy do 60 s/run.

Paczka `cleverkeys-pl-compact-source-trial.zip`, SHA-256
`8169a8ac33261fc245d46a344193759a0c1a84b0eb49cf2436e46ccaed90a229`.
Pełne rozwinięte widoki SHA-256
`e08f7d4a23b9e1ff8543ee9a1daa947c1206475e739cd9edac0679d5f3a4e49a`.

Przypięty czytnik: CleverKeysPL 0b94e323789e96c44a77f762a6f83fa11e285699.
