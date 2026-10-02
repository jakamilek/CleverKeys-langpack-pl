# Polish source matrix — 2026-09-20

Purpose: define the controlled source stack for the Polish CleverKeys dictionary before any production data is promoted.

## Decision

Do not use a single downloaded Polish dictionary as the production base.

Use an evidence pipeline:

1. frequency-ranked candidate stream;
2. mobile-keyboard spelling oracle;
3. Polish spelling/morphology oracle;
4. negative filters;
5. curated allowlist/blocklist;
6. manual review artifacts;
7. only then CKDT V2 generation and langpack packaging.

## Candidate sources

| Source | Role | Status | Licence/provenance note |
|---|---|---|---|
| wordfreq, language pl | frequency-ranked candidate universe | PRIMARY CANDIDATE | Code is Apache-2.0; included data has additional attribution/licensing terms including CC BY-SA 4.0. Preserve NOTICE/attribution. |
| Android AOSP LatinIME pl_wordlist.combined.gz | mobile-keyboard positive oracle | PRIMARY ORACLE CANDIDATE | Present in current AOSP LatinIME main. CleverKeys' current builder documents AOSP snapshots as Apache-2.0; pin exact upstream commit and retain provenance metadata. |
| LibreOffice pl_PL / Hunspell | Polish spelling and inflection validation oracle | SECONDARY ORACLE CANDIDATE | The Polish dictionary README documents a mixed licensing history (GPL/LGPL/MPL/Apache/CC-SA). Prefer using it as a validation input and do not copy raw source files into the distributable pack unless licensing is resolved for the exact version. |
| keybr lang-pl/dictionary-pl.csv | secondary frequency/corpus evidence | QUARANTINE ONLY | Useful as independent evidence, but root licence for the dataset was not established in the current audit. Do not promote or redistribute yet. |
| wooorm/dictionaries pl | Hunspell packaging/source reference | NOT PRIMARY | index.aff exists, but the corresponding index.dic was not usable as a full source in the current audit. Keep only as a provenance/reference lead. |
| curated project allowlist/blocklist | explicit human review boundary | PROJECT-OWNED | Must be committed with rationale/provenance for additions. |
| GUS TERYT / SIMC | official city/locality-name source | PRIMARY GEOGRAPHIC SOURCE | Current official SIMC catalog; city rows are selected with RM=96. One-token names are eligible for the flat CKDT layer. Preserve SIMC ID, catalog state and SHA256 in CI artifacts. |\n| Morfeusz 2 / SGJP | common-noun homonym audit + selected first-name inflection oracle | PRIMARY CURATED ORACLE | Used to audit selected first-name/common-noun collisions and to generate explicit singular forms for the already-selected first names. The full SGJP database is not redistributed; generated forms and version/provenance metadata are retained. The official Morfeusz 2 licensing page states that the inflectional data needed for morphological analysis is under the 2-clause BSD terms. |

## Proposed build architecture

### A. Candidate universe

Use wordfreq Polish ranking to generate a broad candidate universe. Start broad enough to avoid hiding long-tail real words; apply the final size cap only after evidence filtering.

### B. Positive evidence

A candidate is strengthened by:

- AOSP Polish mobile dictionary membership;
- acceptance by a Polish Hunspell spellchecker;
- explicit project allowlist;
- accepted contractions/abbreviation rules where applicable.

### C. Negative evidence

Reject or review candidates showing:

- likely typo relationship to a much more frequent valid Polish word;
- clear foreign-language dominance;
- malformed token patterns;
- unwanted proper-name/brand/entity leakage;
- prohibited or policy-defined content;
- accidental keyboard-noise forms.

### D. Inflection

The runtime does not perform Polish morphology from pl_PL.aff. Valid Polish inflected forms therefore need to survive as explicit entries in the generated CKDT V2 word list.

For general vocabulary, Hunspell remains a spelling/inflection validation oracle. For the already-selected first-name set, Morfeusz 2 / SGJP is used as a curated morphology oracle to generate explicit singular substantive forms; those generated forms are audited and then inserted into CKDT as explicit surfaces.

### E. Separate corpora

Keep these outside the canonical dictionary:

- autocorrect_errors.tsv — wrong → canonical, with error class and provenance;
- phrases.tsv — multiword expressions;
- abbreviations.tsv — abbreviation → expansion/context;
- optional terminology lists for technology/legal/engineering domains;
- regression fixtures for known difficult Polish cases.

Misspellings must not be inserted into the active dictionary just to make autocorrection possible.

## First production target

Do not freeze the final word count before the first evidence run.

Operationally, use a broad candidate stream and evaluate a first ship cap around the current CleverKeys non-English pack scale (roughly 40k–50k), then adjust from measured coverage, false positives and app behaviour.

## Acceptance gates for the first Polish dataset

- correct Polish diacritics preserved;
- explicit inflected forms present where needed;
- no systematic typo families;
- no obvious English/other-language bleed;
- no raw URLs/e-mails/paths/digit tokens;
- frequency ordering is deterministic;
- every retained external source has recorded provenance and licence status;
- generated CKDT V2 word set exactly matches the approved text source;
- package is byte-reproducible and hashed;
- main is never modified directly during source intake.

## Current upstream anchors

CleverKeys runtime baseline:
- tribixbite/CleverKeys main: 263bd0abc03dec420f60fa073a9d2c5e25a176b5

Language project baseline:
- jakamilek/CleverKeys-langpack-pl main: e1a136ea84d4365a36e9ba4fc405d1c6d27a71c8

Work branch:
- ops/baseline-sync-2026-09-20
- current commit before this document: f132d0515036b88ca35af66893e996559b089f47

These SHAs must be refreshed before promotion or release.

### City coverage

The project uses the official GUS TERYT/SIMC catalog for city names. Every eligible one-token city receives a canonical proper-name surface in the flat CKDT layer. Full singular inflection is limited to the top 300 one-token city names by Polish wordfreq frequency plus reviewed priority cities. Multiword/hyphenated city names are not truncated or altered; they remain candidates for the separate phrase layer.
