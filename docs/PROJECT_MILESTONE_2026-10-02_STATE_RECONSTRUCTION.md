# Kamień milowy — odtworzenie stanu projektu po migracji

**Data weryfikacji:** 2026-10-02  
**Typ:** audyt stanu / cross-repo reconstruction  
**Repo kanoniczne tego raportu:** `jakamilek/CleverKeys-langpack-pl`  
**Krótki rekord cross-repo:** `jakamilek/CleverKeysPL/docs/PROJECT_MILESTONE_2026-10-02_STATE_RECONSTRUCTION.md`

> Ten dokument zapisuje zweryfikowany stan **przed commitem, który dodaje sam milestone**. Commit milestone'u z definicji przesuwa HEAD repozytorium o jeden dokumentacyjny commit; po utworzeniu należy ponownie odczytać finalny HEAD z GitHub.

## 0. Zweryfikowany snapshot GitHub

### CleverKeys-langpack-pl

- repo: `jakamilek/CleverKeys-langpack-pl`
- branch: `main`
- HEAD przed tym milestone'em: `1d712783faa1a775c46f3b7f359750d45b40a155`
- ostatni commit: `docs: add 2026-10-02 continuation prompt`
- wcześniejszy HEAD przed dokumentami tej rekonstrukcji: `87cd949a01961c196ec88ab0aa240ba42bc1c5a5`
- branch historyczny `ops/baseline-sync-2026-09-20`: HEAD `8862b31044695f0f28a8667ec851d1ba5b278dd3`
- `main` jest względem tego branchu 14 commitów ahead i 0 behind na moment weryfikacji.

Wniosek: historyczny `ops/baseline-sync-2026-09-20` pozostaje przodkiem stanu `main`; nie jest obecnie najnowszym stanem projektu.

### CleverKeysPL

- repo: `jakamilek/CleverKeysPL`
- branch: `main`
- HEAD przed tym milestone'em: `83c8f6fe201fd1db3de9365a3d1c6c9bea6fdb69`
- ostatni commit: `docs: add cross-repo state reconstruction pointer`
- wcześniejszy HEAD przed dokumentami tej rekonstrukcji: `af78ae5f2842d2d4ddcb069ad53ef103bc85b684`

### Upstream runtime

- repo: `tribixbite/CleverKeys`
- branch: `main`
- HEAD: `01b6212d92d96dd8943145a7b6cef2be53c9fe3c`
- ostatni commit: `feat(keyboard): minimize to a bar or a floating button (gh #175)`

Porównanie w forku `jakamilek/CleverKeysPL` od upstream SHA `01b6212...` do bieżącego `main`:
- 9 commitów ahead;
- 0 behind;
- różnice obejmują wyłącznie dokumentację projektu Language Intelligence / milestone'y.

Nie stwierdzono kodowej dywergencji forka od tego upstream SHA w analizowanym zakresie.

## 1. Najnowsze milestone'y i dokumenty wejściowe

Najważniejsze pliki na bieżącym `main`:

1. `docs/PROJECT_CONTINUITY_RULE_MILESTONES.md`
2. `docs/PROJECT_MILESTONE_2026-10-02_LANGUAGE_INTELLIGENCE_API_V1.md`
3. `docs/LANGUAGE_INTELLIGENCE_API_V1_FINAL_2026-10-02.md`
4. `docs/PROJECT_MILESTONE_2026-10-02_RUNTIME_LANGPACK_AUDIT.md`
5. `docs/ARCHITECTURE_DECISION_RUNTIME_LANGPACK_AUDIT_2026-10-02.md`
6. `docs/NEXT_CHAT_PROMPT_2026-10-02.md`

Od HEAD-ów finalizujących API v1:
- langpack `168f1f83a7df49e572518f1c87037485bc5bee5d`
- runtime `e26d70da385e20a175ecf9e1884233746587ca3d`

do stanu sprzed tej rekonstrukcji zmieniał się wyłącznie plik milestone'u API v1. Kod generatora i kod runtime nie zostały w tym odcinku zmienione.

## 2. Odtworzona architektura — obowiązujący sens „wariantu B”

Na bieżącym `main` nie znaleziono literalnej etykiety tekstowej **„wariant B”**.

Nie odtwarzamy litery z pamięci.

Wiążący sens architektury jest jednak jednoznacznie zapisany w bieżących milestone'ach i finalnym kontrakcie:

```
CleverKeys-langpack-pl
        ↓
zweryfikowana wiedza językowa PL
        ↓
wersjonowany artefakt pakietu
        ↓
Language Intelligence API
        ↓
CleverKeysPL runtime
        ↓
wzbogacenie istniejących kandydatów
        ↓
istniejący context reranking
        ↓
prezentacja / commit
```

Zasady:
- repozytoria pozostają oddzielne;
- runtime jest uniwersalnym silnikiem;
- pakiet jest dostawcą wiedzy językowej;
- API nie generuje nowych kandydatów;
- istniejący `SwipeContextRescorer` pozostaje mechanizmem context rerankingu;
- nie tworzymy drugiego polskiego rerankera;
- UserDictionary pozostaje osobnym źródłem runtime;
- monorepo / embedded langpack nie jest architekturą docelową.

To jest obecnie potwierdzona definicja przyjętego modelu integracji.

## 3. Ważna niespójność dokumentacji ADR

Bieżący plik:
`docs/ARCHITECTURE_DECISION_RUNTIME_LANGPACK_AUDIT_2026-10-02.md`

odwołuje się jako do „authoritative ADRs” do:
- `docs/ARCHITECTURE_DECISION_RUNTIME_LANGPACK_SEPARATION_2026-10-02.md`
- `docs/ARCHITECTURE_DECISION_LANGPACK_PLUGIN_MODEL_2026-10-02.md`

Tych plików **nie ma na bieżących `main`**.

Istnieją natomiast na rozbieżnych branchach dokumentacyjnych:
- langpack: `docs/architecture-runtime-langpack-separation-2026-10-02`, HEAD `9f273652efc91beec15e63d2d6a4a2fd47266160`
- runtime: `docs/architecture-langpack-plugin-model-2026-10-02`, HEAD `969366021b929a4f5a9e2da347d45db90fd4854b`

Ich treść jest zgodna semantycznie z obowiązującymi milestone'ami: separate repositories + external language package + Language Intelligence API.

**Otwarte:** referencje ADR na `main` są niespójne z fizyczną obecnością plików. Nie wykonano automatycznego merge/promote tych branchy.

## 4. Language Intelligence API v1 — stan zaakceptowany

Kontrakt v1 jest sfinalizowany dokumentacyjnie na obu `main`.

Opcjonalny człon pakietu:
`language-intelligence.json`

Model logiczny obejmuje:
- `surfaceKey`;
- `canonicalForm`;
- `frequencyRank`;
- `morphology`;
- `capitalization`;
- `commonNoun`;
- `properName`;
- `metadata`.

Manifest nowego pakietu może deklarować:
- `apiVersion=1`;
- `capabilities`;
- `languageIntelligence.file`;
- `schemaVersion`;
- SHA256 pliku inteligencji.

CKDT V2 pozostaje kompatybilnym fallbackiem.

## 5. Reguły danych PL utrwalone jako kontrakt

Potwierdzono:
- common noun > proper name;
- przymiotnik nie jest automatycznie kapitalizowany z powodu pochodzenia od nazwy własnej;
- dual-casing to wiele wariantów powierzchni jednego `surfaceKey`;
- `Łódź` / `łódź` nie są dwiema niezależnymi pozycjami CKDT;
- brak wpisu/capability oznacza brak wiedzy, a nie automatyczne `false`;
- do artefaktu ma trafiać wynik audytu, nie zależności typu Morfeusz/Hunspell wykonywane na urządzeniu.

## 6. Co jest już zaimplementowane

### Runtime

Potwierdzone z bieżących milestone'ów:
- import zewnętrznych pakietów ZIP przez `LanguagePackManager`;
- CKDT V1/V2 przez `BinaryDictionaryLoader`;
- `Predictor` jako granica runtime;
- `WordPredictor` używający zainstalowanego langpacku;
- istniejący `SwipeContextRescorer`;
- UserDictionary jako osobne źródło.

### Pakiet PL

Potwierdzone:
- działający pipeline 100k/core + moduły;
- audyty kapitalizacji, morfologii, nazw, miejsc, TERC itd.;
- dane źródłowe potrzebne do przyszłego sidecara powstają podczas builda;
- CKDT przenosi obecnie przede wszystkim powierzchnię + rangę.

## 7. Co istnieje jako zaakceptowany kontrakt, ale nie jako implementacja

Niezaimplementowane pozostają m.in.:
- produkcyjny generator `language-intelligence.json`;
- walidator sidecara;
- rozszerzenie manifestu builda o API/capabilities/SHA;
- runtime model `LanguageIntelligence`;
- legacy provider;
- parser/walidator sidecara po stronie runtime;
- wpięcie sidecara w `LanguagePackManager`;
- wzbogacenie kandydatów metadanymi w produkcyjnym flow;
- testy v1/fallback/dual-casing;
- pomiar wydajności i pamięci nowego formatu.

## 8. Eksperymenty / historia — nie promować automatycznie

- `exp/context-reranking-runtime-2026-10-01`: eksperymentalna proweniencja; nie kopiować hurtowo.
- `exp/unified-pl-project-2026-10-01`: historyczny eksperyment monorepo; nie jest architekturą docelową.
- branche dokumentacyjne ADR: zawierają zaakceptowane treści, ale są rozbieżne z `main`; nie zostały automatycznie scalone podczas tej rekonstrukcji.

## 9. Otwarte issues

### Projekt langpack

- `jakamilek/CleverKeys-langpack-pl#1` — **Beta 0.1.0-beta1 — Polish language pack** — open.

### Fork runtime

- brak otwartych issues zwróconych przez wyszukiwanie GitHub dla `jakamilek/CleverKeysPL`.

### Upstream — istotne do obserwacji, ale nie oznaczone tu jako blokery projektu

- `tribixbite/CleverKeys#184` — **Cannot handle big dictionaries** — open;
- `tribixbite/CleverKeys#179` — **Very long time to startup with custom language pack** — open;
- `tribixbite/CleverKeys#99` — **Unclear or outdated documentation of build_langpack.py** — open.

Ich wpływ na obecny projekt nie został w tym etapie ponownie zbadany; nie należy automatycznie traktować ich jako przyczyny lub blokera implementacji v1.

## 10. Status workflowów / CI

Dostępny konektor GitHub dla commitów:
- zwrócił puste combined statuses dla sprawdzanych HEAD-ów;
- `fetch_commit_workflow_runs` zwrócił brak runów i zgodnie z interfejsem filtruje tylko runy wywołane przez pull request.

Dlatego:

**Niezweryfikowane — wymaga sprawdzenia pełnej listy GitHub Actions / push runs.**

Pusty wynik nie jest dowodem `green`.

Nie zmieniono kodu w tym etapie, więc nie uruchamiano ponownie testów lokalnych jako substytutu CI.

## 11. Historyczny artefakt PL

Poprzedni milestone przechowuje historycznie zweryfikowany run 382 / artifact 11189614575 / wordCount 106363.

Nie został w tej rekonstrukcji potwierdzony jako najnowszy artefakt publikacyjny.

**Niezweryfikowane — wymaga pełnego odczytu aktualnych GitHub Actions/artifacts przed użyciem jako bieżącego benchmarku.**

## 12. Różnica względem poprzedniego milestone'u

Poprzedni milestone API v1 zamknął kontrakt danych.

Ten milestone:
- ponownie zweryfikował oba `main` i upstream;
- potwierdził brak zmian kodowych od finalizacji API v1;
- ustalił, że historyczny branch `ops/baseline-sync-2026-09-20` jest przodkiem obecnego langpack `main`;
- potwierdził, że fork runtime jest względem bieżącego upstream SHA tylko dokumentacyjnie ahead;
- wykrył niespójne referencje do ADR-ów nieobecnych na `main`;
- utworzył nowy prompt ciągłości `docs/NEXT_CHAT_PROMPT_2026-10-02.md`;
- nie wykonał żadnego merge/promote gałęzi eksperymentalnych.

## 13. Następny zalecany krok

Nie wracać do pełnego audytu.

Najbliższy etap po stronie producenta danych, zgodnie z najnowszym milestone'em langpacku:

1. zbudować pierwszy deterministyczny `language-intelligence.json` z **bieżących, zweryfikowanych wyników audytów**;
2. nie zmieniać reguł selekcji 100k core;
3. dodać walidację schema/SHA;
4. rozszerzyć manifest builda;
5. dodać coverage/conflict report i testy deterministyczności.

Następnie po stronie runtime:
1. model/capability;
2. legacy provider;
3. parser/walidator;
4. integracja z `LanguagePackManager`;
5. lookup/wzbogacenie istniejących kandydatów;
6. testy legacy/v1/fallback/dual-casing;
7. dopiero później wpływ na scoring.

Osobno należy zdecydować, czy naprawić brakujące ADR-y na `main`; nie scalać ich automatycznie jako efekt uboczny implementacji.

## 14. Reguła wejścia dla kolejnej instancji

Najpierw:
1. odczytaj ten milestone;
2. zweryfikuj HEAD-y obu `main`;
3. policz diff od snapshotu;
4. przeczytaj finalny kontrakt API v1;
5. kontynuuj wyłącznie od ostatniego potwierdzonego punktu.

Nie odtwarzaj stanu z pamięci modelu.
