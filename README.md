# CleverKeys-langpack-pl

Polski pakiet językowy dla klawiatury CleverKeys.

Sprawdzona na telefonie próba: [addytywne grupy tematyczne v7](docs/thematic-forms-trial-v1/PROTOCOL.md)
— słownictwo potoczne, komputerowe oraz dom, zakupy, technika i budownictwo.
188 302 klucze, bez usuwania starych wpisów. Import i wykrywanie słów
zaakceptowane przez użytkownika z poprawionym APK (kod `141f27e7`).

Kolejny etap: [nazwy, marki i skrótowce v8](docs/names-forms-trial-v1/PROTOCOL.md).
2511 dodatków potwierdzonych w SGJP, razem 190 813 kluczy; stare wpisy,
ich wagi i metadane pozostają bez zmian. Lokalne testy producenta,
rzeczywistych czytników i importu przy ograniczonej pamięci PASS.
CI i test telefonu dla v8 pozostają do sprawdzenia.

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
