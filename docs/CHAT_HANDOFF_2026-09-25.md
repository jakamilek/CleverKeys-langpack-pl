# CleverKeys Polish Language Pack — CHAT HANDOFF
Date: 2026-09-25
Repository: https://github.com/jakamilek/CleverKeys-langpack-pl

## 0. How to resume

This document is the durable migration state for a new chat/instance. Read it before making changes.

Official project baseline rule:
- GitHub repository is the only official baseline.
- Do not assume any local/uncommitted state or work from previous chat instances exists.
- Earlier Codex/other-instance work is migration material and must be audited before inclusion.
- Never perform an automatic merge of unverified material.
- Commit important changes to GitHub continuously so the state survives chat/instance migration.

Current working branch:
- ops/baseline-sync-2026-09-20

Current project direction:
- Production dictionary architecture = immutable 100,000-word frequency core + additive auditable modules.
- The old 150k experiment is diagnostic only, not the production target.
- Final production size is not fixed in advance. It is 100,000 + union of net-new case-insensitive module keys after the retention policy is applied.

## 1. Core architecture (accepted decisions)

### Immutable 100k core
- Exactly 100,000 core entries.
- Built from the pinned Polish wordfreq candidate universe after the normal project linguistic/quality filters.
- Base-only mode exists in scripts/build_pl_preview.py:
  --base-only
- Module expansion must never displace a core key.
- Capacity accounting uses case-insensitive key identity.

### Additive modules
Current / planned modules:
1. Polish first names
2. Polish localities / cities
3. Polish administrative division (GUS TERYT / TERC): voivodeships, powiats, gminas
4. Countries and capitals (official KSNG/GUGiK list)
5. Controlled brands / trade names (planned; not a raw trademark dump)
6. Other reviewed morphology only; the early proper-noun pilot is retired and excluded from active module accounting

Case-insensitive capacity rule:
- core 'warszawa' + module 'Warszawa' = one key, not two;
- module may replace the canonical surface/casing after audit;
- module key absent from core = one net-new slot;
- same key across several modules = stored once with combined category/provenance metadata.

Final size:
100,000 + union(net-new module keys)

### Morphology and category admission strategy
Every new category follows this protocol:
1. Prepare and audit the category's base words/items.
2. Generate the complete validated singular paradigm.
3. Validate provenance, morphology and capitalization.
4. Deduplicate case-insensitively against the 100k core and active modules.
5. Measure the category before deciding what to retain.
6. When the measured size is within the category's agreed capacity envelope, retain all validated base items and forms.
7. When the category is too large, retain the base items and reduce inflection forms using frequency, grammatical usefulness and source confidence.
8. Keep the complete generated paradigm and evidence for any excluded forms in audit artifacts.
9. Re-measure the final retained set and its net-new union contribution.

Capacity is evaluated primarily on net-new unique keys, not raw generated-form counts. A low-frequency valid form is not removed when there is sufficient capacity. A category-specific capacity envelope is established only when needed and only after its cost has been measured. No numeric frequency threshold is set before measurement.

Current status:
- name/city modules use full retention;
- frequency-aware reduction is reserved for future capacity pressure and does not justify pruning the current 2,611-key active addition set.

## 2. Frequency policy (accepted decision)

For module items that are absent from the 100k core:
- absence from core must NOT be interpreted as zero frequency.

Accepted measurement model:
- Primary frequency signal: NKJP-derived frequency data.
- Secondary independent signal: pinned wordfreq Polish frequency.
- Module-specific importance is a separate evidence dimension, not a replacement for linguistic corpus frequency.
  Examples:
  - first names: official population/name statistics can be an importance signal;
  - cities: official geographic status / practical keyboard relevance;
  - countries/capitals: official status;
  - brands: current practical relevance and provenance.
- Do not invent one combined frequency number by silently merging NKJP and wordfreq.
- Measure lemma/base and, where possible, individual inflected surface forms separately.
- Retention thresholds must be calibrated from observed distributions and keyboard usefulness. Do NOT hard-code thresholds before seeing the data.

Important distinction:
- wordfreq remains useful for the immutable 100k core.
- NKJP is now the preferred primary frequency evidence for additive modules.
- wordfreq remains as an independent cross-check and fallback signal for module forms not seen in NKJP.

## 3. Frequency implementation status

New script:
- scripts/audit_module_frequency.py
Purpose:
- NKJP primary + wordfreq secondary module frequency audit.
- Records NKJP surface frequency, exact form+lemma frequency where available, wordfreq Zipf, source provenance and distribution statistics.
- Explicitly records that retention thresholds are not yet set.

Pinned NKJP source:
- ENIAM revision: be02836cf3aa0286ad8961d2e4528cdc2f72d044
- File: resources/NKJP1M/NKJP1M-tagged-frequency.tab
- Successful reproducible acquisition: legacy GitLab repository archive endpoint restricted to resources/NKJP1M.
- Verified file SHA-256: fee31b1d6a682970b4e8ca68b593aea8dadbc8541e875e2d287480d83601e79c
- Verified size: 12,181,895 bytes
- Verified data rows: 183,181
- Verified column count: 8

Size-study #79 (run 36175350217) is the first valid NKJP + wordfreq frequency measurement. Its results are historical measurements and include the early proper-noun pilot, which has now been retired from active module accounting.
Do not treat the 76 pilot forms as an active production module or as a retention target.

Relevant web verification:
- ENIAM/NKJP1M directory exposes NKJP1M-frequency.tab, NKJP1M-tagged-frequency.tab and related files.
- Official ENIAM documentation for NKJP1M-tagged-frequency.tab states it contains 7 columns and identifies columns 1-4 as word form, lemma, tag, frequency.
- The NKJP1M material is a manually annotated 1-million-word subcorpus (not the full 1.5B searchable NKJP corpus). Treat the NKJP1M frequency table as an NKJP-derived frequency snapshot, and document that scope explicitly.

## 4. Source pins and evidence

### wordfreq
Pinned git commit:
- 912caf64b657478d1dff1138efdc078947d54bb1
Project requirement file:
- scripts/requirements-pl-audit.txt

Base builder explicitly lowercases wordfreq raw candidates:
- word = raw.lower()

### AOSP LatinIME Polish dictionary
Pinned SHA256:
- 75a7a488e014ec3b9dbdb2527f09bca6bb28c250232d9ba50cb0ee1f8738ea45
Source:
- dictionaries/pl_wordlist.combined.gz
Branch:
- refs/heads/main

AOSP is supporting mobile-keyboard evidence, not an authority for Polish casing or unrestricted name expansion.

### Hunspell
- hunspell
- hunspell-pl
Used as spelling/acceptance oracle.

### Morfeusz / SGJP
- morfeusz2==1.99.15
- polish-inflection==0.7.3
Used for selected inflection generation and reverse validation.

### GUS TERYT / SIMC
Current state date:
- 2026-09-24
Archive SHA256:
- 678444fbdcfc631738d8280f78d2edf4b29c489d9e61c28b368907b9e0cab15a
Current extracted figures:
- 1026 RM=96 city rows
- 850 one-token city rows
- 844 unique one-token city names
- 176 skipped non-single-token rows
- 6 lowercase duplicate names
Current city policy:
- all 844 official one-token city names in city module;
- multiword/hyphenated names deferred;
- current generator provides full singular inflection for top 300 wordfreq-ranked cities + explicit reviewed priority cities, plus reviewed source-backed overrides.

### First names
Official source strategy:
- dane.gov.pl first-name statistics 2006-2025
Selection currently:
- top 215 female + top 215 male
- 20 historical female + 20 historical male
- 470 selected before exclusion
- 469 active after excluding "oleksandr"
Current generator output observed previously:
- 2282 inflection records
- 296 names with at least one non-nominative form
- 173 names nominative-only
Capitalization policy:
- ordinary names/proper names are capitalized;
- lowercase common-noun homonym exceptions: jagoda, lilia, malina, melisa, róża and their generated forms;
- excluded first name: oleksandr.

### Countries / capitals
Planned official source:
- KSNG/GUGiK 2025 official list of state/territory names.
Use it for canonical Polish spelling and official status; do not treat it as a raw frequency source.

### Brands
Planned controlled module:
- not all registered trademarks;
- require current real brand evidence;
- require practical relevance in Polish usage;
- provenance + date;
- separate linguistic decision for capitalization and actual Polish inflection.
UPRP / EUIPO / TMview are verification signals, not a raw import source.

## 5. Capitalization policy

Final capitalization gate is mandatory immediately before CKDT creation.

Rules:
- ordinary vocabulary: lowercase;
- geographic/proper-name-derived adjectives: lowercase
  e.g. warszawski, warszawska, warszawskie;
  wrocławski, wrocławska, wrocławskie;
  toruński, toruńska, toruńskie;
  gdyński, gdyńska, gdyńskie;
- proper names/cities and their grammatical forms: audited capitalization;
- ordinary lower-case homonym exceptions among selected first names stay lowercase;
- any capitalization violation must fail CI.

Examples already protected/verified:
- Wrocław, Wrocławia, Wrocławiem, Wrocławiowi, Wrocławiu
- Toruń and reviewed forms
- Gdynia and reviewed forms
- lower-case derived adjectives remain lower-case.

## 6. City overrides currently accepted

File:
- sources/staging/reviewed_city_inflection_overrides.tsv

Reviewed overrides:
Gdynia:
- nom Gdynia
- gen Gdyni
- dat Gdyni
- acc Gdynię
- inst Gdynią
- loc Gdyni
- voc Gdynio

Toruń:
- nom Toruń
- gen Torunia
- dat Toruniowi
- acc Toruń
- inst Toruniem
- loc Toruniu
- voc Toruniu

Wrocław:
- nom Wrocław
- gen Wrocławia
- dat Wrocławiowi
- acc Wrocław
- inst Wrocławiem
- loc Wrocławiu
- voc Wrocławiu

Sources are recorded in the TSV and include authoritative linguistic evidence such as WSJP PAN / NCK OJczysty.

## 7. Retired early proper-noun pilot

The early `reviewed_proper_nouns` staging file was created for first-round runtime tests and anchor/provenance probing. It is no longer an active production module.

Archived copy:
- `sources/archive/reviewed_proper_nouns_pilot_2026-09-25.tsv`

The original 76-form pilot must not be included in module-cost accounting, frequency retention calibration, or production CKDT generation. Any future reuse requires fresh assignment to the correct active category, fresh source audit, and explicit promotion.

## 8. Regression protection

Current hard regression blocklist contains:
- chopin
- chopina
- goebbels
- goebbelsa
- catherine
- catalina
- cameron
- carli
- carlo
- castillo
- cali
- celli
- casino
- calli
- carrillo
- caroli
- cassino
- compos
- gourami
- celastial

The blocklist is based on observed/regression failures and should remain enforced unless a specific item is separately audited and the regression rationale is revisited.

Key runtime symptom being targeted:
- CleverKeys 1.5.0/build 1.5.0
- QWERTY (Polski)
- geometric swipe engine
- other dictionaries disabled
- autocorrect=false, swipe=true
- user observed short Polish words being misrecognized or dominated by foreign/proper-name candidates.
A debug example produced "carli" with candidates:
carli, carlo, castillo, cali, celli, casino, calli, carrillo, caroli, cassino.
This motivates reducing irrelevant foreign/proper-name noise and improving Polish ranking/lexicon quality.

## 9. Current CI / run history

Recent successful runs:
- Polish preview #109 — success, commit 1e4b3fb4ace8d595249d0026b41518df14b0e9a2
- Proper-noun coverage audit #43 — historical pilot audit; the pilot is now retired and its workflow has been removed
- First-name audit #58 — success, commit b44697e5181f303caa8465ae91d921c09e621434
- Size study #74 — success, commit 2bac611c35b30c2ce544c834204cda295ade7f0a
- Size study #73 — success, commit 8556c258f3790b8bc8256c592378a6c99c9b0a83

Recent failures and what they mean:
- size #70: module analyzer delimiter bug
- size #71: module analyzer sorted dicts without a key
- size #72: same/related analyzer correction stage; later fixed
- size #73: green after manifest count assertion corrected
- size #74: green after reviewed TSV form parsing was corrected
- size #75: FAILURE at new NKJP audit because the downloaded NKJP file was not usable; NO valid NKJP frequency report exists from #75.

The #75 failure is technical and not evidence against NKJP itself.

## 10. Module-cost analyzer

Script:
- scripts/analyze_dictionary_modules.py

It reports:
- source surface count;
- unique case-insensitive keys;
- overlap with 100k;
- net-new keys vs 100k;
- overlap with previous modules;
- surface replacements (e.g. base "warszawa" -> module "Warszawa");
- cumulative unique-key count.

Fixed bug:
- replacement records now sort via key=lambda item: item["key"].

Also fixed reviewed TSV parsing:
- reviewed_morphology.tsv uses the semicolon-separated forms field;
- reviewed_proper_nouns.tsv uses its forms field;
- analyzer must measure actual dictionary surfaces, not whole metadata lines.

Run #74 successfully executed module-cost analysis.

## 11. Previous observed size-study facts

A prior successful/inspected build showed:
- 150,000 requested target was only 140,711 kept after filters in one study, exposing that "requested limit" != "actual kept".
- That study also showed a large number of additional module words and displaced words, but those numbers are NOT final and must not be reused as final production counts.
- Architecture was subsequently changed to protected 100k core + additive modules.
- Do not restore any previously displaced basic words automatically. User explicitly wants to know exactly what is displaced before any restoration, and wants to test the current build before deciding what to restore.

Previous successful 100k artifact (older diagnostic build):
- 100,000 entries
- 96,526 lowercase-initial
- 3,474 uppercase-initial
Do not treat those casing counts as final without reproducing against the current exact commit.

Previous preview artifact:
- preview #97 from commit 03682963...:
  artifact id 10829265487
  size 4,798,653 bytes
  sha256:cba1b21c88f672a422a0e16fede142364c19efd857524f18eca3f5439f9bde09
This is historical reference only.

## 12. Important commit trail

Key accepted implementation commits:
- 9ac5a6f4e4e53b061591976d51499e7c84081fbb — capacity displacement audit
- 90d7a17071cce9715ca275bd3fdfb6733af8a5a0 — TERYT/SIMC city source for nominative + Morfeusz/SGJP non-nominative
- a97c8ae8e6ac0c5eaf4e6ba55af2db8edcf1263 — explicit audited proper-name/city inflection surface handling
- 74bc93c6ef3c9d76af79ca46878a8bc759f60c93 — first-name generator invocation fix
- 3dc94185652eaabce766951c8bfc000aedad8db5 and f7157a50a629d24af73ed7071c412f36ee54911e — TSV delimiter fixes
- 92f5c678e4a7f9f817d4d53d6d138348bb491991 — diacritic alias suppression fix
- 73952263e2bb9a369f1c6998722c639ac4bfc385 — Gdynia overrides
- 036829fb31b0693dc61a5e7317d7be30d40b434 — city override support/fix
- aa4fcaa1598f6f0d534ff0c8f839d9fde4a6e2f4 — preview workflow invokes overrides
- ffc09c52a16573466f5b1100dcb98fb28987274 — size workflow invokes overrides
- 06b60c719067cb78bd888ec41f473c5bc1f4dfec — Toruń/Wrocław overrides
- 8080a1b18a2820c02e7c006f2fe7a2fad4f0fcd7 — Zośka
- 2f7b4e2a344c59c7426cbd59971e56ac27ece696 — Wrocław/Toruń capitalization regressions
- 00673d29b5fca12043943e290b3280f0040ca62a — mandatory capitalization gate
- 76ac62632182b058e871c4c190fdc5aa44f4175d — capitalization CI assertions
- 1967896c3ba5fc765a88e6541fd604be5f064e59 — systematic lowercase inflection handling for common-noun homonym first names
- 8105341b65b2f490a2586fac0f22561f00ee87f1 — adjective lowercase policy
- 3f9a8a1ceb98dc35cd975d576b8100993e56c960 — adjective capitalization regressions
- b44697e5181f303caa8465ae91d921c09e621434 — base-only build mode
- 9f164aeb4a83da59c1836632b7658f517556ed8a — module-cost analyzer initial
- af55ba2ed8c989a516bf759c9a8adad7654838ed — surface replacement reporting
- 1ff0093e24e4874da941a04d7e35d444880feaf8 — TSV delimiter fix in analyzer
- 0f3a93449309b4bcd296eaf2593f12ab47ce012f — trigger size study on analyzer path
- 1e4b3fb4ace8d595249d0026b41518df14b0e9a2 — AOSP download retry
- ead33476c0ee4b70e1df9660853e7dee3185db13 — size workflow retry configuration
- e616f355c0ae70c7ef961446f6c31886b5324e82 — module architecture documentation
- 608b76557ba54bd885a17b6e63bc35838e2e5f50 — analyzer sort correction (size #72 attempt)
- 8556c258f3790b8bc8256c592378a6c99c9b0a83 — size study assertion fix (#73)
- 2bac611c35b30c2ce544c834204cda295ade7f0a — reviewed TSV parser correction (#74)
- 6546b3d186e18db0ec6e9513c779d6d0f063796e — NKJP audit workflow added; #75 failed at NKJP source parsing.

Current branch also contains a documentation update for NKJP frequency policy.

## 12a. Early proper-noun pilot retirement (2026-09-25)

The early `reviewed_proper_nouns` pilot has been retired from active production data.

- active staging file removed: `sources/staging/reviewed_proper_nouns.tsv`
- historical copy: `sources/archive/reviewed_proper_nouns_pilot_2026-09-25.tsv`
- active preview and size-study workflows no longer pass or account for the pilot
- standalone `pl-proper-noun-audit.yml` workflow removed
- the pilot's 76-form NKJP measurement remains historical only and is excluded from current module-capacity totals
- future reuse requires explicit reassignment to the correct category and a fresh source audit

Commits:
- `0116eb83014b8998f69e69aceee44af62a9f6417` — archive pilot
- `f9effdd24b52b49929ef0b38c6e499a96f645ac2` — remove active staging file
- `6e80025bf81b1eac7406c3ff2de05a316f81a51c` — remove from size-study accounting
- `79df50082a40cc1d9373038894a6e687298b9e44` — architecture decision
- `848d8ce6bb70d1ff3bc53fafa0659d97c7c784c9` — update handoff
- `b28ef44c98069847ad6405655f7d164b67868cd0` — remove pilot from builder
- `7492c23ec0577c5e38360796c5a5b10c32f6420d` — remove pilot from preview workflow
- `1331104065b5aab84ac9acc6b2c2df4803c5a79d` — remove standalone pilot audit workflow

Current branch HEAD: verify directly from the GitHub branch ref before resuming (this handoff file is itself updated by commits).

## 13. Current NKJP acquisition and frequency-audit state

As of 2026-09-25, the former NKJP acquisition blocker is resolved and
reproducibly pinned.

- size-study #79: run 36175350217
- verified commit: 7633c863d162fff869ad37d5b2b09db2b749b102
- NKJP1M pinned revision: be02836cf3aa0286ad8961d2e4528cdc2f72d044
- successful acquisition method: legacy GitLab repository archive endpoint
- verified file size: 12,181,895 bytes
- verified data rows: 183,181
- verified column count: 8
- verified SHA-256: fee31b1d6a682970b4e8ca68b593aea8dadbc8541e875e2d287480d83601e79c

The direct raw endpoint is not the successful route and must not be described as
such. CI is now pinned to the verified SHA-256 and stores acquisition provenance
with the size-study artifacts.

The first successful NKJP + wordfreq audit covered 4,020 unique surface/lemma
pairs. Global distributions were:

- NKJP nonzero P10/P25/P50/P75/P90/P95: 1 / 1 / 2 / 7 / 24 / 51
- wordfreq nonzero P10/P25/P50/P75/P90/P95: 1.49 / 2.01 / 2.58 / 3.13 / 3.83 / 4.18

Module coverage:

- first-name forms: NKJP seen 736/1,759; zero 1,023
- city names: NKJP seen 292/844; zero 552
- city inflections: NKJP seen 537/1,218; zero 681
- reviewed morphology: NKJP seen 46/123; zero 77
- reviewed proper nouns: NKJP seen 63/76; zero 13
  Note: this 76-form figure belongs to historical run #79 only; the pilot is now retired and excluded from active production accounting.

No retention thresholds have been chosen. The zero-count forms remain candidates
for later analysis, not automatic exclusions.


### Latest clean size study after proper-noun pilot retirement

Size-study #86 (run `36178666213`, commit `b28ef44c98069847ad6405655f7d164b67868cd0`) completed successfully with the retired proper-noun pilot excluded.

Active module measurement:
- first-name forms: 1,736 unique keys; 308 overlap the 100k core; 1,428 net-new vs core
- city names: 844 unique keys; 372 overlap the 100k core; 472 net-new vs core
- city inflections: 1,218 unique keys; 493 overlap the 100k core; 725 net-new vs core; 89 overlap earlier active modules
- reviewed morphology: 123 unique keys; 48 overlap the 100k core; 75 net-new vs core
- union of active module keys: 3,620
- active module keys already in core: 1,009
- net-new active module keys over the protected 100k core: 2,611
- current measured union before any future frequency-aware retention: 102,611 unique keys

The old 3,635 / 2,623 figures are superseded because they included the retired proper-noun pilot. The 76-form proper-noun result remains historical only.

The same #86 run also passed the pinned NKJP1M acquisition and module-frequency audit. NKJP nonzero surface distribution in this clean active set: P10/P25/P50/P75/P90/P95 = 1 / 1 / 2 / 6 / 21 / 44. Wordfreq nonzero Zipf: 1.49 / 2.00 / 2.56 / 3.09 / 3.776 / 4.13.

### What remains to do next

A. Inspect the module distributions and NKJP/wordfreq disagreements by module
   and individual form, especially forms absent from NKJP1M but supported by
   wordfreq or category semantics.

B. Validate the active 2,611 net-new keys for morphology/provenance/capitalization/regressions; do not remove forms merely for low frequency.

C. Keep full validated paradigms in the active modules; retain NKJP/wordfreq measurements as audit evidence and diagnostics.

D. Recalculate final net module cost only after any quality-based exclusions.

E. Continue planned modules only after the above audit is stable:
   TERC administrative units, countries + capitals, controlled brands, and
   later broader practical language additions.

## 14. User's testing setup and practical goal

CleverKeys:
- version/build 1.5.0
- QWERTY (Polski)
- swipe engine geometric
- other dictionaries disabled
- autocorrect=false
- swipe=true
- latency observed 15 ms in playground

Main practical objective:
- improve Polish swipe recognition and ranking for short/common words;
- reduce foreign proper-name contamination;
- preserve correct Polish capitalization;
- support useful Polish names/places and their inflection;
- make all source additions auditable and reversible.

Do not optimize only for dictionary size. Quality, source safety and auditability come first.

## 15. Prompt guidance for next chat

Start by saying you have read:
- this handoff file;
- docs/PL_DICTIONARY_MODULE_ARCHITECTURE_2026-09-25.md;
- current GitHub Actions state;
and then verify the current branch/head and the newest size-study run before making assumptions.

The next chat must NOT:
- ask the user to repeat the project history;
- assume #75 succeeded;
- do not regress the verified NKJP1M acquisition/pin;
- invent retention thresholds;
- change the immutable 100k core to make room for modules;
- auto-merge inherited material;
- restore previously displaced words without an explicit audited comparison.

The next chat SHOULD:
- continue from the GitHub state on branch ops/baseline-sync-2026-09-20;
- keep the verified NKJP acquisition pin and rerun the measurement after active-module cleanup;
- keep commits small and auditable;
- rerun CI after each meaningful fix;
- report exact results and artifacts.
