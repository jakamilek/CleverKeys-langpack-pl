# Language Intelligence API v1 — finalny kontrakt danych pakietu PL

**Data:** 2026-10-02  
**Status:** zaakceptowany kontrakt danych do implementacji  
**Zakres:** reprezentacja wiedzy językowej w pakiecie; bez zmiany kodu generatora w tym commicie

## 1. Wynik audytu rzeczywistych danych

Bieżący `main` został sprawdzony bez zakładania stanu z wcześniejszych rozmów.

Zweryfikowane fakty:

- `manifest.json` repozytorium projektu jest metadanymi projektu, a nie manifestem instalowanego ZIP-a;
- `scripts/build_pl_preview.py` buduje listę powierzchni oraz wykonuje audyty kapitalizacji i modułów;
- workflow preview tworzy tymczasowe TSV/JSON z informacją o Morfeuszu, kapitalizacji, nazwach, miejscach, TERC, państwach, stolicach itd.;
- następnie workflow buduje CKDT V2 i przekazuje do pakietu tylko wynikową listę słów oraz rangę CKDT;
- produkowany w preview ZIP zawierał historycznie `dictionary.bin`, `manifest.json` i `unigrams.txt` według własnej weryfikacji workflow;
- dodatkowa wiedza z audytów nie była dotychczas członkiem instalowanego artefaktu;
- bieżące `source/` zawiera również starszy, mały zestaw plików budowania, ale nie jest on równoważny 100k pipeline preview i nie może być traktowany jako dowód pełnej inteligencji pakietu PL.

Istotny wniosek:

**musimy przenieść do artefaktu wynik audytu, a nie narzędzia, które ten wynik wyliczają.**

## 2. Podział informacji

### Już dostępne w CKDT / runtime

- powierzchnia słownikowa;
- ranga częstotliwości;
- liczność słownika;
- podstawowa obecność słowa.

### Dostępne podczas budowy, ale dziś niewynoszone do artefaktu

- canonicalForm;
- morfologia;
- polityka kapitalizacji;
- common noun;
- proper name;
- warianty powierzchni;
- źródło/moduł/proweniencja;
- wyniki audytów dla nazw, miejsc i form fleksyjnych.

### Oddzielne źródło runtime

Android UserDictionary/custom words nie stają się częścią tej warstwy.

## 3. Minimalny kontrakt członu inteligencji

Nowy pakiet może zawierać:

```text
language-intelligence.json
```

Dokument:

```json
{
  "schemaVersion": 1,
  "languageCode": "pl",
  "entries": [
    {
      "surfaceKey": "łódź",
      "canonicalForm": "łódź",
      "capitalization": {
        "defaultSurface": "łódź",
        "variants": [
          {"surface": "łódź", "casePolicy": "lowercase"},
          {"surface": "Łódź", "casePolicy": "capitalized"}
        ]
      },
      "commonNoun": true,
      "properName": true,
      "morphology": {
        "pos": "noun",
        "features": {}
      },
      "metadata": {
        "module": "city"
      }
    }
  ]
}
```

Zasady:

- `surfaceKey` to lowercase powierzchni z zachowaniem diakrytyki;
- jeden `surfaceKey` reprezentuje jedną tożsamość klucza powierzchniowego;
- kilka powierzchni jest przechowywanych jako warianty;
- brak wpisu oznacza brak dodatkowej wiedzy;
- pola opcjonalne są pomijane, a nie wypełniane sztucznym `false`.

## 4. Dane morfologiczne

Format morfologii jest neutralny:

```text
pos: String?
features: Map<String, String>
```

Pakiet może wygenerować ten model z Morfeusza lub innego analizatora podczas budowy.

Runtime nie zależy od konkretnego analizatora.

## 5. Kapitalizacja

Pakiet przechowuje wynik resolvera, a nie samą regułę heurystyczną.

Obowiązują:

- rzeczownik pospolity ma pierwszeństwo przed nazwą własną;
- przymiotnik nie jest kapitalizowany automatycznie z powodu pochodzenia od nazwy własnej;
- dual-casing jest reprezentowany przez warianty jednego `surfaceKey`;
- wspólny klucz nie jest rozbijany na dwa rekordy CKDT.

Przykłady:

- `łódź` + `Łódź` → jeden klucz, domyślnie `łódź`;
- `Tomaszów` → wariant kapitalizowany;
- `mazowiecki` / `warszawski` → lowercase.

## 6. Capability manifestu

Pakiet v1 deklaruje możliwości:

```text
lexicon
frequency
morphology
capitalization
common_noun
proper_name
metadata
```

Capability oznacza możliwość dostarczenia danego typu informacji, nie gwarancję kompletności dla każdego rekordu.

Coverage ma być raportowane w audycie budowania, nie zakodowane w semantyce `false`.

## 7. Rozszerzony manifest instalowany

Po stronie generatora:

```json
{
  "code": "pl",
  "name": "Polish",
  "version": 2,
  "author": "jakamilek/CleverKeys-langpack-pl",
  "wordCount": 106363,
  "hasPrefixBoost": false,
  "apiVersion": 1,
  "capabilities": [
    "lexicon",
    "frequency",
    "morphology",
    "capitalization",
    "common_noun",
    "proper_name",
    "metadata"
  ],
  "languageIntelligence": {
    "file": "language-intelligence.json",
    "schemaVersion": 1,
    "sha256": "<64 hex>"
  }
}
```

Liczba `106363` jest tu przykładowym historycznie zweryfikowanym rozmiarem artefaktu, a nie nową obietnicą bieżącego builda. Aktualny build musi wyznaczyć `wordCount` z rzeczywistego `dictionary.bin`.

## 8. Deterministyczność

Nowy człon danych musi być:

- generowany deterministycznie;
- UTF-8;
- stabilnie uporządkowany;
- możliwy do zahashowania;
- dołączany do ZIP-a z deterministycznym wpisem.

Manifest zawiera SHA pliku inteligencji.

## 9. Fallback i starsze pakiety

Brak `apiVersion` i brak członu inteligencji oznacza legalny pakiet legacy.

Nie wolno wymuszać nowego pliku na starych pakietach.

Pakiet z nieobsługiwanym głównym API nie może być po cichu traktowany jako starszy format.

## 10. Generowanie danych PL

Źródłem danych wejściowych pozostają istniejące, zweryfikowane procesy:

- Morfeusz 2 / SGJP;
- NKJP1M;
- AOSP LatinIME;
- Hunspell;
- TERC/SIMC;
- KSNG;
- audyty nazw własnych i kapitalizacji;
- ręcznie zatwierdzone wpisy.

Do artefaktu trafia **wynik** tych procesów, nie zależność wykonawcza.

## 11. Minimalny producent v1

Generator PL powinien wyprodukować:

1. bieżący `pl_words_preview.txt`;
2. CKDT V2;
3. `language-intelligence.json`;
4. manifest z `apiVersion`, capability i SHA;
5. raport coverage i konfliktów.

Pierwsza implementacja może przechowywać tylko rekordy posiadające dodatkową wiedzę. Nie jest wymagane zduplikowanie 100% słownika w sidecarze.

## 12. Poza zakresem

Nie ustalamy teraz:

- wag scoringowych;
- modelu statystycznego;
- osobnego polskiego rerankera;
- formatu optymalizowanego pamięciowo poza kontraktem JSON;
- UserDictionary;
- automatycznego uruchamiania Morfeusza na urządzeniu.

Optymalizacja JSON do zwartego formatu binarnego może być późniejszą zmianą transportową bez zmiany kontraktu logicznego.

## 13. Warunek implementacji

Przed zmianą generatora należy zachować możliwość uruchomienia obecnego CKDT V2 jako fallbacku.

Każdy nowy rekord powinien być audytowalny do źródła i reguły, która go wyprodukowała.

Nie wolno kopiować historycznych danych tylko dlatego, że występowały w dawnych artefaktach; bieżący `main` jest źródłem prawdy.

