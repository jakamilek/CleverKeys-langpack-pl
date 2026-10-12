# CleverKeys-langpack-pl

Polski pakiet językowy dla klawiatury CleverKeys.

Zaakceptowane na telefonie: tematyczne v7, nazwy/marki/skróty v8 oraz
[współdzielone metadane v9](docs/shared-metadata-trial-v1/PROTOCOL.md).
V9 zachowuje 190 813 słów. Użytkownik potwierdził poprawny import i działanie;
odczuwalne przyspieszenie jest obserwacją, bez pomiaru PSS Androida.

Kolejny etap: [odłożone nazwy i odmiany v10](docs/deferred-names-trial-v1/PROTOCOL.md).
13 650 dodatków potwierdzonych w SGJP, razem 204 463 słowa. Wszystkie stare
wpisy, wagi, metadane i tablice współdzielone pozostają bez zmian. Ta paczka
używa obecnego APK schema-v2 (`64943d82`); nie zmienia SI ani aplikacji.
Bieżące CI i próby telefonu dla v10 pozostają do potwierdzenia.

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
