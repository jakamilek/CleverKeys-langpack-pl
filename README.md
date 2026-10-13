# CleverKeys-langpack-pl

Polski pakiet językowy dla klawiatury CleverKeys.

Zaakceptowane na telefonie: tematyczne v7, nazwy/marki/skróty v8 oraz
[współdzielone metadane v9](docs/shared-metadata-trial-v1/PROTOCOL.md).
V9 zachowuje 190 813 słów. Użytkownik potwierdził poprawny import i działanie;
odczuwalne przyspieszenie jest obserwacją, bez pomiaru PSS Androida.

V10 i bezstratne v11 zaakceptowano na telefonie: 204 463 słowa.
CI v11, czytnik API/schema3 oraz APK również przeszły wymagane bramki.
Pozostajemy przy zaakceptowanej v11. Dodatkową partię rzadszych nazw v12
odkładamy; nie została przekazana jako kolejny etap do instalacji.
Aktualne zadanie to [moduły z kandydatami](docs/practical-candidates-v1/PROTOCOL.md):
zwykłe formy, terminologia techniczna/internetowa i potoczna oraz aplikacje/usługi.
To materiał do przeglądu i pomiaru, bez nowego langpacka lub APK.

## Cel projektu

Praktyczny polski słownik mobilny:
- język polski PL,
- odmiana i sugestie dla klawiatury ekranowej,
- popularne słowa codzienne,
- terminologia techniczna,
- często używane zapożyczenia angielskie.

Wykluczamy:
- losowe śmieciowe wpisy,
- błędne formy,
- spam i niskiej jakości dane.

## Struktura

```
source/
  pl_PL.dic
  pl_PL.aff
  frequency.csv
  custom_words.csv

scripts/
  build_pl.sh
```

## Budowanie

Pakiety będą budowane automatycznie przez GitHub Actions z kontrolą SHA256.
