# NEXT CHAT PROMPT — CleverKeysPL / CleverKeys-langpack-pl — 2026-10-02

Kontynuuj istniejący projekt. GitHub jest jedynym źródłem prawdy. Nie zaczynaj od pełnego audytu historycznego.

## Dokumenty wejściowe — czytaj w tej kolejności

1. `docs/PROJECT_CONTINUITY_RULE_MILESTONES.md`
2. `docs/PROJECT_MILESTONE_2026-10-02_STATE_RECONSTRUCTION.md`
3. `docs/PROJECT_MILESTONE_2026-10-02_LANGUAGE_INTELLIGENCE_API_V1.md`
4. `docs/LANGUAGE_INTELLIGENCE_API_V1_FINAL_2026-10-02.md`

Kanoniczny milestone przekrojowy znajduje się w:
`jakamilek/CleverKeys-langpack-pl`.

Fork runtime:
`jakamilek/CleverKeysPL`.

Upstream:
`tribixbite/CleverKeys`.

## Obowiązująca architektura

Repozytoria pozostają rozdzielone.

```
CleverKeys-langpack-pl
        ↓
zweryfikowana wiedza językowa PL
        ↓
wersjonowany artefakt + Language Intelligence API
        ↓
CleverKeysPL runtime
        ↓
wzbogacenie istniejących kandydatów
        ↓
istniejący context reranking
        ↓
prezentacja / commit
```

Runtime jest uniwersalnym silnikiem, a pakiet językowy dostawcą wiedzy językowej.

Nie tworzyć monorepo.
Nie tworzyć drugiego polskiego rerankera.
Language Intelligence API nie generuje nowych kandydatów.
UserDictionary pozostaje osobnym źródłem.

## Kontrakt v1 — stan zaakceptowany

Opcjonalny człon artefaktu:
`language-intelligence.json`

Logika obejmuje m.in.:
- surfaceKey;
- canonicalForm;
- frequencyRank;
- morphology;
- capitalization;
- commonNoun;
- properName;
- metadata.

Manifest może deklarować:
- `apiVersion=1`;
- capabilities;
- plik sidecara;
- schemaVersion;
- SHA256.

CKDT V2 pozostaje kompatybilnym fallbackiem.

## Reguły PL utrwalone w kontrakcie

- common noun ma pierwszeństwo przed proper name;
- przymiotniki pozostają lowercase;
- dual-casing jest wieloma wariantami powierzchni jednego klucza;
- `Łódź` / `łódź` nie są dwiema niezależnymi pozycjami CKDT;
- brak capability / brak pola oznacza brak wiedzy, nie automatyczne `false`.

## Punkt kontynuacji

Następny etap jest implementacyjny, ale przed każdą zmianą ponownie zweryfikuj bieżące HEAD-y GitHub.

Po stronie pakietu PL:
1. zbudować pierwszy deterministyczny `language-intelligence.json` z bieżących, zweryfikowanych wyników audytów;
2. nie zmieniać reguł selekcji 100k core;
3. dodać walidator sidecara;
4. rozszerzyć manifest generowany przez build;
5. dodać raport coverage/konfliktów i testy deterministyczności.

Po stronie runtime:
1. model `LanguageIntelligence` i capability;
2. provider legacy oparty o CKDT;
3. parser/walidator sidecara;
4. integracja z `LanguagePackManager`;
5. lookup dla już istniejących kandydatów;
6. testy legacy/v1/fallback/dual-casing;
7. dopiero potem użycie metadanych w scoringu.

## Reguły operacyjne

- ZERO DOMYSŁÓW.
- Nie promuj gałęzi eksperymentalnych do `main` bez osobnej autoryzacji.
- Nie kopiuj hurtowo historycznych branchy.
- Znaczące zmiany zapisuj atomowymi commitami.
- Po etapie: push, weryfikacja SHA, CI jeśli możliwe, nowy milestone.
- Jeśli statusu CI nie da się potwierdzić dostępnym interfejsem, oznacz go dokładnie jako niezweryfikowany.
