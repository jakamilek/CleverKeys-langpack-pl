# Polish language data plan for CleverKeys

## Runtime model

Current CleverKeys consumes a flat CKDT V2 vocabulary. Polish morphology therefore must be represented as explicit word forms in the generated dictionary; a Hunspell `.aff` file is not the runtime morphology engine for the current langpack format.

## Data layers

1. Canonical/frequency vocabulary — common Polish forms ranked for mobile prediction.
2. Inflection coverage — explicitly enumerated Polish forms, validated against a morphology oracle and/or high-quality corpus evidence.
3. Autocorrect errors — `wrong -> canonical`, with error class, confidence and provenance.
4. Keyboard typos — adjacency/transposition patterns are handled by the CleverKeys engine; the dictionary must not be polluted with misspellings.
5. Diacritic aliases — missing Polish diacritics such as `ę`, `ą`, `ł`, `ń`, `ś`, `ź`, `ż`, `ć`, `ó` are handled by the engine's accent-normalization path; canonical dictionary output keeps the correctly accented form.
6. Phrases — separate multiword source for high-value mobile phrases.
7. Abbreviations — separate curated source with expansion/context; never treated as ordinary words without review.
8. Allowlist/blocklist — explicit review boundary for proper names, brands, foreign bleed, profanity policy, malformed tokens and false positives.
9. Unigrams — generated from the accepted frequency-ranked vocabulary for language detection.

## Prefixes

Typed-prefix suggestions are a core dictionary behaviour, but the historical `prefix_boost.bin` asset is not a current CleverKeys runtime dependency. Do not generate legacy prefix-boost assets for Polish unless the application runtime changes and a new consumer is verified.

## Classic Polish error suite

Keep a reviewed regression set including, at minimum:

- `rzeczywiscie -> rzeczywiście`
- `mozna -> można`
- `czesc -> cześć`
- `wogole -> w ogóle`
- `napewno -> na pewno`
- `wziąść -> wziąć`
- `włanczać -> włączać`
- `ktory -> który`

These examples are test fixtures, not permission to mass-import arbitrary typo forms into the dictionary.

## Quality gates

- no duplicate canonical words;
- no accidental typo variants in the active dictionary;
- high-frequency words must be present with correct diacritics;
- inflected forms must be supported as real forms, not generated at runtime from `pl_PL.aff`;
- corrections must only point to accepted canonical forms;
- URLs, e-mails, paths and tokens containing digits/special syntax must remain outside correction lists;
- every external source must retain provenance and licence status;
- every generated package must be deterministic and hashed;
- no quarantine/staging source is promoted automatically.

## Backup / synchronization rule

At the start of every work session, record the current SHA of both repositories:

- `jakamilek/CleverKeys-langpack-pl` main — language project baseline;
- `tribixbite/CleverKeys` main — runtime/package-format baseline.

Every data change should be committed in small atomic commits on a work branch. Before merge/promotion, refresh both SHAs and rebuild the package from the current approved inputs. Never merge an older local snapshot over a newer GitHub main.

Current snapshot: see `docs/BASELINE_SYNC_2026-09-20.md`.
