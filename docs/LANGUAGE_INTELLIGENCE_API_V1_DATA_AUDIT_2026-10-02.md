# Language Intelligence API v1 — audit danych 2026-10-02

## Zakres

Audyt wykonany wyłącznie na podstawie zweryfikowanego stanu GitHub:

- repozytorium: `jakamilek/CleverKeys-langpack-pl`
- audytowany ref: `main`
- HEAD: `bef64a5d205f5ba280efc39a65728ee47407e6ee`
- branch dokumentacyjny: `docs/language-intelligence-api-v1-2026-10-02`

Celem jest sprawdzenie, które elementy kontraktu Language Intelligence API v1 istnieją faktycznie w obecnym pakiecie, a które istnieją tylko jako wcześniejsze założenia/dokumentacja albo nie istnieją w `main`.

## 1. Faktyczny model pakietu na main

### Root manifest

`manifest.json` na `main` zawiera:

- `id`
- `name`
- `project`
- `version`
- `encoding`
- `dictionary`

Nie zawiera kontraktowych pól runtime:

- `code`
- `wordCount`
- `hasPrefixBoost`
- `apiVersion`
- `capabilities`
- `provenance`

Ważne: jest to manifest repozytorium źródłowego, nie manifest zgodny z aktualnym importerem runtime.

### Obecny build

`scripts/build_pl.sh` buduje:

- `pl_PL.dic`
- `pl_PL.aff`
- `frequency.csv`
- `bigrams.csv`
- `priorities.csv`
- `custom_words.csv`
- `corrections.txt`
- `validation_rules.txt`
- `report.json` (jeżeli istnieje)
- `build_quality.json`
- generowany `manifest.json`

Generowany manifest ma pola:

- `language`
- `name`
- `version`
- `encoding`
- `features`

Lista `features` obejmuje:

- `dictionary`
- `word_frequency`
- `bigrams`
- `autocorrection`
- `priorities`
- `quality_report`

To nadal nie jest manifest zgodny z obecnym runtime `LanguagePackManager`, który wymaga `code` i `name`, a następnie oczekuje w ZIP-ie `dictionary.bin`.

## 2. Mapowanie API v1

| Capability / pole API v1 | Stan na langpack main | Dowód / lokalizacja | Wniosek |
|---|---|---|---|
| lexicon | częściowo obecne jako źródła | `source/*.dic` | Brak finalnego artefaktu CKDT na main |
| frequency | obecne jako źródło | `source/frequency.csv` | Nie jest jeszcze częścią formalnego kontraktu artefaktu |
| morphology | niepotwierdzone jako działający zasób | `source/pl_PL.aff`, `source/pl_PL.dic` | `.aff` zawiera tylko podstawę UTF-8/TRY, bez zweryfikowanych reguł odmiany |
| capitalization | reguły istnieją w dokumentacji | `docs/CHAT_HANDOFF_2026-09-26_CAPITALIZATION_POLICY.md` | Brak maszynowego artefaktu kapitalizacji |
| common_noun | brak maszynowego artefaktu | brak odpowiedniego źródła w tree | Nie można zadeklarować jako gotowej capability |
| proper_name | brak maszynowego artefaktu | brak odpowiedniego źródła w tree | Nie można zadeklarować jako gotowej capability |
| metadata | częściowo obecne | root `manifest.json`, build manifest | Brak wersjonowanego modelu `apiVersion/capabilities/provenance` |
| provenance | częściowo obecne | `docs/dictionary_sources.md`, build attribution istniejący w runtime tooling | Nie jest jeszcze częścią kontraktu langpack main |

## 3. Morphology — stan zweryfikowany

Na `main` istnieją:

- `source/pl_PL.dic`
- `source/pl_PL.aff`

Jednak `pl_PL.aff` zawiera tylko:

`SET UTF-8` oraz `TRY ąćęłńóśźż` i komentarze.

Nie ma w nim obecnie pełnego zestawu reguł odmiany.

Nie znaleziono w tree `main` odrębnego artefaktu pochodzącego z Morfeusza ani tabeli zweryfikowanych form.

**Wniosek:** capability `morphology` nie może być jeszcze oznaczona jako obecna w artefakcie API v1.

## 4. Capitalization / common noun / proper name

Dokument `docs/CHAT_HANDOFF_2026-09-26_CAPITALIZATION_POLICY.md` potwierdza decyzje projektowe:

- forma ortograficzna jest ważniejsza niż kategoria źródła,
- rdzeń ma być pierwszą prawdą kapitalizacji,
- nazwy własne są drugą warstwą ochronną,
- przymiotnik pochodzący od nazwy własnej nie jest automatycznie zapisywany wielką literą,
- przyszłe rozróżnienie typu `Łodzi` / `łodzią` wymaga kontekstu.

Nie znaleziono jednak na `main` maszynowego pliku, który przekazywałby runtime:

- `capitalization`,
- `commonNoun`,
- `properName`.

**Wniosek:** decyzje są udokumentowane, ale nie są jeszcze eksportowanym zasobem Language Intelligence.

## 5. Dane częstotliwości i priorytetów

Na `main` istnieją:

- `source/frequency.csv`
- `source/priorities.csv`
- `source/bigrams.csv`

Są to dane źródłowe/robocze. Nie ma na `main` zweryfikowanego mechanizmu, który przekształcałby je do jednolitego rekordu API v1 typu:

`surface + canonicalForm + frequency + morphology + capitalization + commonNoun + properName + metadata`.

## 6. Aktualny artefakt a runtime

Aktualny runtime `CleverKeysPL/main` przyjmuje ZIP językowy przez `LanguagePackManager`.

Importer wymaga:

- `manifest.json`
- `dictionary.bin`

Opcjonalnie obsługuje:

- `unigrams.txt`
- `contractions.json`
- `prefix_boost.bin`
- `NOTICE.txt`
- deklarowany `model.onnx`

Runtime nie ma obecnie zweryfikowanego parsera dla:

- morphology,
- capitalization,
- common/proper-name metadata,
- API version,
- capability declarations.

**Krytyczna luka integracyjna:** obecny langpack `build_pl.sh` nie produkuje `dictionary.bin`, a jego manifest ma inny schemat niż importer runtime.

## 7. Wnioski

1. API v1 jest obecnie specyfikacją docelową, nie formatem już obsługiwanym end-to-end.
2. Langpack main zawiera podstawowe dane leksykalne, częstotliwościowe i priorytety, ale nie zawiera jeszcze formalnego artefaktu Language Intelligence.
3. Morphology, capitalization, common-noun i proper-name są na tym etapie nieeksportowane jako dane runtime.
4. Nie należy implementować parsera API v1 w runtime na podstawie założenia, że te dane już istnieją w pakiecie.
5. Najmniejsza bezpieczna kolejna praca to zaprojektowanie rzeczywistego artefaktu v1 na podstawie istniejących źródeł, a dopiero potem jego eksport i parser runtime.
6. Konieczne jest również rozstrzygnięcie, czy budowanie pakietu PL ma przejąć wspólny generator `scripts/build_langpack.py` z runtime, czy powstać kompatybilny generator po stronie langpack. Nie należy tego rozstrzygać przez zgadywanie.

## 8. Zasada dalszej pracy

Nie wykonywać jeszcze zmian w `main`.

Najpierw należy uzgodnić i zweryfikować:

- rzeczywisty format artefaktu v1,
- źródła danych morphology/capitalization/common/proper,
- wersjonowanie API,
- capability negotiation,
- kompatybilność z `LanguagePackManager`,
- testy importu i fallbacku.

Audyt nie zmienia `main`.
