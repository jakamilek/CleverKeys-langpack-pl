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
- frequency-aware reduction is reserved for future capacity pressure and does not justify pruning a validated active addition while sufficient capacity exists.

### Retired reviewed morphology pilot

The former `reviewed_morphology` pilot has been retired from active production, using
the same treatment as the early proper-noun pilot.

- active staging file removed: `sources/staging/reviewed_morphology.tsv`
- historical copy: `sources/archive/reviewed_morphology_pilot_2026-09-25.tsv`
- preview builder no longer loads or protects these forms
- preview and size-study workflows no longer account for or publish the pilot
- its historical 123-form measurement is not part of current active capacity accounting
- future reuse requires fresh assignment to an appropriate category or explicitly defined new category, fresh source audit, and explicit promotion

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
- historical pilot TSVs were parsed by their respective form fields;
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
- reviewed morphology: 46/123 seen; this is historical pilot evidence only and is no longer part of active module accounting
- reviewed proper nouns: NKJP seen 63/76; zero 13
  Note: this 76-form figure belongs to historical run #79 only; the pilot is now retired and excluded from active production accounting.

No retention thresholds have been chosen. The zero-count forms remain candidates
for later analysis, not automatic exclusions.


### Latest clean size study before reviewed-morphology retirement

Size-study #86 (run `36178666213`, commit `b28ef44c98069847ad6405655f7d164b67868cd0`) was the last clean measurement before retiring the reviewed-morphology pilot.

Its active-module result of 2,611 net-new keys and 102,611 total keys is now **superseded**, because it included the 123-form reviewed-morphology pilot. The exact active total after this retirement must be taken from a fresh size-study run; it must not be inferred by subtraction because cross-module overlaps and case-insensitive deduplication affect the union.

Historical figures from the retired pilot:
- reviewed morphology: 123 unique keys; 48 overlapped the 100k core; 75 were net-new versus the core
- these figures are retained only for traceability and are excluded from all current capacity decisions

The old 3,635 / 2,623 figures are also historical because they included the retired proper-noun pilot.

The same #86 run also passed the pinned NKJP1M acquisition and module-frequency audit. NKJP nonzero surface distribution in this clean active set: P10/P25/P50/P75/P90/P95 = 1 / 1 / 2 / 6 / 21 / 44. Wordfreq nonzero Zipf: 1.49 / 2.00 / 2.56 / 3.09 / 3.776 / 4.13.

### What remains to do next

A. Inspect the module distributions and NKJP/wordfreq disagreements by module
   and individual form, especially forms absent from NKJP1M but supported by
   wordfreq or category semantics.

B. Validate the current active net-new set after the reviewed-morphology retirement for provenance/capitalization/regressions; do not remove forms merely for low frequency.

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


## 16. Stan potwierdzony tuż przed zmianą czatu — 2026-09-25

Najnowszy stan workflowów sprawdzony na branchu:
- preview #167 — uruchomiony na SHA `83bdbeeb2d3a63ee1e6e9c4e705528e74eb500ca`;
- size-study #143 — uruchomiony na tym samym SHA.

Wcześniejsze runy:
- preview #166: zatrzymał się na walidacji `build/pl-terc-inflections-selected.tsv` z komunikatem o schema mismatch;
- size-study #142: ten sam problem;
- preview #165: chwilowy `FileNotFoundError` dla NKJP1M;
- size-study #141: nieudane pobranie NKJP1M.

Aktualna poprawka selektora TERC została zapisana w commitcie:
`83bdbeeb2d3a63ee1e6e9c4e705528e74eb500ca`

Dodatkowo utworzono osobny, gotowy do wklejenia prompt:
`docs/NEXT_CHAT_PROMPT_2026-09-25.md`
(commit `820816fee84173bb8e2ec14c0768866fd02f1a8d`).

Ten handoff i powyższy prompt są trwałym źródłem kontekstu przy zmianie okna/instancji. Najpierw sprawdzać aktualny GitHub/CI, dopiero potem kontynuować pracę.


## 17. Kontynuacja 2026-09-26 — TERC schema synchronization

Po ponownym uruchomieniu CI wykryto dwa kolejne, zależne od siebie problemy ze zmianą kontraktu TERC.

1. Commit `2c7c22eb136ec323525cd4e3ad1ccf3d21d7887b` rozszerzył walidację selektora do 10 pól: `category, name, level, terc, number, case, form, case_policy, source, morfeusz_version`.
2. Commit `c5cd8b9cf74331ec2e7c24eb2859e495acc7af2d` dostosował `scripts/build_pl_preview.py` do tego 10-polowego selected-TERC TSV.
3. Commit `a5ff83b0a522293aec68c47f74a13277f624e2d4` naprawił ważniejszy problem generatora: jednostki TERC nie mogą być deduplikowane po nazwie, ponieważ różne kody TERC mogą mieć tę samą nazwę. Tożsamość jednostki jest teraz oparta na `level + terc`.

Runy:
- preview #168 i size-study #144 na SHA `2c7c22e...` przeszły krok 14, ale zatrzymały się później na krokach zależnych od starego kontraktu buildera.
- po `c5cd8b9...` uruchomiono preview #170 oraz size-study #146 na SHA `a5ff83b0...`.
- preview #170 jest oczekujący, size-study #146 jest uruchomiony; wynik końcowy należy zweryfikować bez założeń.
- first-name audit #77 na `c5cd8b9...` zakończył się błędem wyłącznie przy pobraniu przypiętego AOSP; nie traktować tego jako błędu danych językowych.

### Obowiązkowa kontrola po zakończeniu CI

Najpierw zweryfikować #170 i #146. Następnie sprawdzić rzeczywiste artefakty TERC i policzyć:
- 16 województw z pełną odmianą,
- 380 powiatów z selektywną retencją,
- 2479 gmin z mianownikiem w warstwie produkcyjnej,
- pełną odmianę zachowaną jako audit artifact,
- selected TERC jako produkcyjny input.

Nie wolno używać historycznej wartości 2,611 jako aktualnego net-new kosztu, ponieważ obejmowała wycofany pilot. Po zakończeniu obecnego size-study należy odczytać nowy `module-study-report.json` i `module-frequency-report.json` oraz dopiero wtedy podejmować decyzję o kalibracji selekcji powiatów.

Aktualny branch HEAD: `a5ff83b0a522293aec68c47f74a13277f624e2d4`.


## 18. Decyzja architektoniczna 2026-09-26 — identity vs dictionary surface

Rozróżniamy dwie warstwy:
- tożsamość obiektu źródłowego: dla TERC `level + terc`, zachowywana w pełnym audycie;
- tożsamość klucza słownikowego: case-insensitive `surface_key`, używana do unii i pojemności CKDT.

W efekcie dwie różne gminy/powiaty o tej samej nazwie nie są dublowane w słowniku. Ich dwa identyfikatory i provenance pozostają w audycie, a CKDT dostaje jeden klucz powierzchniowy.

Kapitalizacja nie może wynikać wyłącznie z kategorii modułu. Każda finalna powierzchnia musi mieć audytowaną politykę kapitalizacji. Dla TERC należy rozróżniać m.in. województwa i powiaty przymiotnikowe (mała litera), miasta (wielka litera) oraz gminy zależnie od tego, czy nazwa ma postać rzeczownikową/proprialną czy przymiotnikową. Konflikt kapitalizacji dla tego samego klucza case-insensitive nie może być rozstrzygany automatycznie.

Nowa polityka została zapisana w:
`docs/PL_MODULE_SURFACE_IDENTITY_AND_CAPITALIZATION_POLICY_2026-09-26.md`
(commit `e246e849b51bc39dba382e3d3522f1bfe7ace520`).

Przy dalszej implementacji nie cofać ochrony provenance przez `level + terc`, ale także nie pozwalać, aby identyfikator jednostki powodował duplikację kluczy w finalnym CKDT.


### Doprecyzowanie 2026-09-26 — selected TERC jako jedyny production surface layer

Nowa polityka powierzchni modułów została rozszerzona: `build/pl-terc-inflections.tsv` i `build/pl-terc-flat.tsv` są wyłącznie materiałem źródłowym/audytowym. Jedynym kontraktem produkcyjnym warstwy TERC ma być `build/pl-terc-inflections-selected.tsv`.

Builder CKDT nie powinien równolegle dodawać nazw z pełnego TERC i nazw z selected TERC. Pełna warstwa pozostaje do provenance, audytu wykluczeń i kontroli tożsamości jednostek; selected layer jest jedynym źródłem powierzchni produkcyjnych TERC.

Polityka została zapisana w `docs/PL_MODULE_SURFACE_IDENTITY_AND_CAPITALIZATION_POLICY_2026-09-26.md`, commit `41c2f2847349d98bd66df3b9e8bfe0d0e410f8e9`.


## 19. Uogólnienie architektury — 2026-09-26

Przyjęta zasada identity-vs-surface obowiązuje projektowo dla **całego pakietu**, nie tylko dla TERC.

- Tożsamość źródłowa pozostaje granularna i audytowalna.
- Tożsamość słownikowa jest globalnym, case-insensitive `surface_key = Unicode-lowercase(surface)`.
- Wszystkie moduły i immutable core uczestniczą w tej samej logice unii kluczy.
- Jeden klucz CKDT może wystąpić tylko raz, ale może mieć wielu kontrybutorów/provenance.
- Kapitalizacja jest decyzją dla konkretnej powierzchni, a nie cechą całego modułu.
- Niezgodne polityki kapitalizacji dla tego samego klucza są konfliktem audytowym i blokują promocję; system nie wybiera automatycznie zwycięzcy.
- Ogólny docelowy przepływ: `source records -> validated forms -> surface registry -> CKDT`.

Dokument nadrzędny:
`docs/DICTIONARY_SURFACE_IDENTITY_AND_CAPITALIZATION_POLICY_2026-09-26.md`
(commit `2224036550eba4b752624862cdb143ee9e9e16a2`).

Dokument szczegółowy TERC pozostaje dokumentem implementacyjnym dla tego modułu.

### 19a. Naprawy pipeline TERC

Po błędzie preview #170 wykryto, że rozdzielenie tożsamości źródłowej od surface identity odsłoniło błąd w generatorze: po przejściu na klucz `level+terc` kod nadal pobierał metadane przez `names[lower_name]`, co powodowało `KeyError: 'bolesławiec'`.

Naprawiono kolejno:
- `f7a9173a5991512022c14c4793d6476fc53c3aee` — generator korzysta z bieżącego rekordu jednostki;
- `ff667a7fb66794bd9684d07d0f7775940dfbaf15` — builder przestał dodawać pełny TERC równolegle z selected TERC;
- `a439f0c3e07cd6251f9c249c405400d9bb5273fa` — preview workflow przekazuje TERC do buildera przez selected layer;
- `d9a74bb5eec2f9b8b6b22b6dbeb50c9f93364b2d` — size-study i frequency audit mierzą produkcyjny selected TERC, bez pełnego TERC jako osobnego modułu;
- `c0fd25634f736d96d04c795f4ea1061c3bd2563a` — builder akceptuje opcjonalną kolumnę auditową `retention` w selected TERC;
- `f0eb0d0b2422b75d9cf8061270868ffa5aec0e34` — voivodeship TERC jest generowany jako lowercase zgodnie z przyjętą polityką ortograficzną.

Pełny TERC pozostaje materiałem audit/source; selected TERC jest jedyną produkcyjną warstwą surface dla TERC.

### 19b. Otwarte zadanie kapitalizacji gmin

Nie uznajemy jeszcze problemu kapitalizacji gmin za zakończony. Obecny extractor nadal nie implementuje rozstrzygnięcia językowego „rzeczownik/proper-name vs przymiotnik” dla każdej gminy. Jest to kolejny etap audytu surface registry; nie wolno zastąpić go prostą regułą „wszystkie gminy wielką literą”.

### 19c. CI

Preview #170 zakończył się błędem na generatorze TERC z `KeyError: 'bolesławiec'` — był to błąd implementacyjny, nie błąd źródła TERC.
Po zmianach od `f7a9173...` do `f0eb0d0...` powinny zostać sprawdzone nowe runy preview/size-study od najnowszego HEAD przed użyciem jakichkolwiek liczb końcowych.


## 20. Rejestr powierzchni wdrożony w budowaniu — 2026-09-26

Zasada identity-vs-surface została zastosowana na poziomie wspólnego etapu przed CKDT, a nie tylko w dokumentacji TERC.

- `scripts/build_pl_preview.py` buduje wspólny rejestr powierzchni dla zwykłego słownictwa i aktywnych modułów.
- Klucz słownikowy jest case-insensitive (`Unicode-lowercase`).
- Zwykłe słownictwo ma domyślną politykę lowercase; moduły źródłowe dostarczają jawne polityki kapitalizacji.
- Kompatybilne duplikaty są łączone pod jednym kluczem.
- Sprzeczne jawne powierzchnie/polityki dla jednego klucza są konfliktem i zatrzymują budowę.
- Raport preview zawiera `surface_registry` z liczbą kluczy i konfliktów.

Commit wdrażający rejestr:
`2297c97e83aa8586848f2bd84b6e0f9b60c22ca9`

## 21. Wynik size-study #151 — punkt odniesienia przed kolejną zmianą

Run #151 na `f0eb0d0b...` zakończył się sukcesem. Raport modułów wykazał:
- 6975 unikalnych kluczy modułowych przed porównaniem z rdzeniem;
- 1531 kluczy modułowych już obecnych w immutable 100k;
- 5444 klucze netto ponad rdzeń;
- 105444 klucze jako `100000 + 5444` po unii case-insensitive.

TERC w tym badaniu: 2263 unikalne powierzchnie w selected TERC; 755 już w rdzeniu. Źródłowy TERC nadal zawiera 2875 jednostek (16/380/2479), a 288 kluczy nazw występuje w więcej niż jednej jednostce źródłowej. Oznacza to, że rozdzielenie tożsamości jednostki i powierzchni działa zgodnie z przyjętą zasadą.

Te liczby są ważnym pomiarem bieżącej architektury, ale po poprawce filtra aliasów oraz po wdrożeniu rejestru należy je potwierdzić w świeżym size-study przed decyzjami końcowymi.


## 22. Doprecyzowanie rejestru powierzchni — 2026-09-26

Rejestr powierzchni w budowniczym analizuje konflikty wyłącznie dla kluczy, które mają zostać zachowane w końcowym słowniku. Formy odrzucone wcześniej przez twarde blokady lub inne bramki nie powodują fałszywego zatrzymania budowy.

Commit:
`5ab8372a0446f81a3c08b61f3e302438454e56b5`


## 23. Paczka testowa do telefonu — 2026-09-26

Preview #187 na commit `6901c0841273ed78c26882656e14146a478da931` zakończył się sukcesem.

Powstała paczka produkcyjna w kształcie testowym:
- immutable core: 100000;
- net-new module keys: 5444;
- final CKDT keys: 105444;
- rejestr powierzchni: 105444 klucze, 0 nierozstrzygniętych konfliktów;
- kontrola kapitalizacji: 105444 sprawdzonych powierzchni, 0 naruszeń;
- CKDT: wersja 2;
- zawartość ZIP: `dictionary.bin`, `manifest.json`, `unigrams.txt`;
- `hasPrefixBoost=false`.

Plik testowy:
`CleverKeys-PL-phone-test-187.zip`
SHA-256: `1615e64c6829bd3a8749133f27ae57000f2a007a38475d4c1cb7cb78cf0a17b9`.

To jest **paczka do testu na telefonie**, nie promocja do produkcji. Po teście należy zebrać konkretne przypadki błędnych rankingów/przekształceń, szczególnie krótkie słowa, oraz osobno sprawdzić kapitalizację imion i nazw miejscowości.

## 24. Zmiana architektury kapitalizacji i nazw wieloczłonowych — 2026-09-26

Test telefonu wykazał konkretny problem: Łódź zostało zapisane wielką literą mimo kolizji z rzeczownikiem pospolitym łódź. Następnie wykryto tomaszów w rdzeniu 100k, mimo że źródłowa nazwa własna Tomaszów powinna być skapitalizowana.

Przyjęto od tej chwili zasadę nadrzędną:
- obecność klucza w immutable 100k nie rozstrzyga kapitalizacji;
- rdzeń jest audytowany osobno zaraz po zbudowaniu, przed złożeniem modułów;
- każda powierzchnia będąca kandydatem do kapitalizacji jest sprawdzana pod kątem zwykłego użycia leksykalnego, niezależnie od obecności w rdzeniu;
- audyt obejmuje nie tylko rzeczowniki pospolite, ale także inne zwykłe części mowy;
- jeśli istnieje zwykłe użycie leksykalne i brak jawnej decyzji właściwej dla danego przypadku, kanoniczna powierzchnia może zostać znormalizowana do lowercase;
- wybrane imiona zachowują osobną, audytowaną politykę kapitalizacji, z istniejącymi wyjątkami lowercase/exclude;
- konflikty polityk różnych źródeł wymagają jawnego wpisu w sources/staging/surface_registry_policy.tsv.

### Nazwy wieloczłonowe

Nie odrzucamy już nazw wieloczłonowych tylko dlatego, że nie są pojedynczym tokenem.
- scripts/surface_components.py rozbija pełną nazwę na człony słowne.
- Pełna nazwa pozostaje w warstwie źródłowej dla provenance („pochodzenia danych”).
- Człony są osobno analizowane pod kątem kapitalizacji i kolizji leksykalnych.
- Dotyczy to miast, TERC, państw, stolic i przyszłych modułów.
- Dla CKDT człony są reprezentacją słownikową; pełna fraza pozostaje materiałem audytowym.
- Nazwy z łącznikiem również są rozbijane na człony do audytu, bez utraty pełnej nazwy źródłowej.

Przykład: Tomaszów Mazowiecki -> osobna analiza Tomaszów i Mazowiecki.

### Nowe narzędzia

- scripts/audit_core_capitalization.py — audyt i rozstrzyganie kapitalizacji dla kluczy rdzenia 100k przed złożeniem modułów.
- scripts/audit_capitalization_common_noun_homonyms.py — wspólny audyt kapitalizacji modułów i emitowanie kanonicznych powierzchni.
- scripts/surface_components.py — wspólne rozbijanie nazw wieloczłonowych na człony.
- scripts/build_additive_phone_test.py — przyjmuje wyniki obu audytów i nie pozwala na rozbieżność między audytem rdzenia i modułów.

### Znane przypadki zapisane w rejestrze

- łódź -> łódź — wspólny klucz nazwy miasta Łódź i rzeczownika pospolitego łódź.
- łodzi -> łodzi oraz łodzią -> łodzią — analogiczna kolizja form odmiany.
- miński -> miński — kolizja z członem nazwy własnej i przymiotnikiem administracyjnym.
- kłodzki -> kłodzki — kolizja między przymiotnikiem powiat kłodzki a członami nazw miejscowości typu Lewin Kłodzki.
- tomaszów -> Tomaszów — powierzchnia właściwa dla nazwy własnej, której klucz wcześniej pochodził z rdzenia 100k.

### Aktualizacja źródeł miast

extract_teryt_cities.py nie ogranicza już warstwy źródłowej do nazw jednoczłonowych.
Aktualny poprawny pomiar pokazał:
- 1020 miast w źródle;
- 844 nazw jednoczłonowych;
- 176 nazw wieloczłonowych.

Generator odmiany jednoczłonowej nadal pracuje tylko na nazwach jednoczłonowych, ale pełne nazwy wieloczłonowe pozostają dostępne dla audytu i składania warstwy powierzchniowej.

### Aktualny etap CI

Po tych zmianach trwają nowe przebiegi preview/size-study. Nie należy używać paczki #187 jako bieżącej wersji testowej kapitalizacji, ponieważ została zbudowana przed powyższymi zmianami.

## 25. Kontynuacja 2026-09-26 — Unicode English possessive w tokenizerze surface components

Na podstawie najnowszego CI wykryto problem architektoniczny w rozbijaniu zagranicznych nazw wieloczłonowych.

Objaw:
- preview #231 kończył się na `Unresolved common-noun capitalization collisions: s`;
- size-study #178 kończył się na `Conflicting capital source component casing ...: 's' vs 'S'`.

Źródłem był fałszywy komponent jednoliterowy `s` pochodzący z angielskiej konstrukcji possessive `'s` zapisanej także typograficznym apostrofem `’s`. Nie jest to niezależne słowo słownikowe CKDT i nie może trafiać do surface registry.

Zmiana architektoniczna:
- commit `78e80b4da950c40b688ac3023181fa1de6736bfa`;
- `scripts/surface_components.py` używa teraz wspólnej reguły Unicode dla `'s`, `’s` i `＇s`, niezależnie od wielkości litery;
- nie dodano wyjątku dla żadnej konkretnej stolicy ani nazwy;
- provenance pełnej nazwy pozostaje nienaruszone.

Regresja CI:
- commit `0ff4276ca4871f70394f51d1a6d78b3859fd9c07`;
- preview workflow otrzymał testy dla `Saint John’s`, `King’s College` i `D’Arcy`, obok istniejących testów ASCII.

Stan CI przy zapisie:
- size-study #179 na `78e80b4...` — in progress;
- preview #232 na `78e80b4...` — in progress;
- preview #233 na `0ff4276...` — pending;
- wcześniejsze #178/#231 na `c6fdb1...` są historycznie failed i nie należy ich traktować jako stanu po poprawce.

Kryterium akceptacji:
1. tokenizer nie emituje `s` z angielskiego possessive;
2. preview przechodzi audit capitalization;
3. size-study przechodzi przez budowę 50k/100k/125k/150k;
4. dopiero po green CI odczytać nowe `module-study-report.json`, `module-frequency-report.json` i artefakty;
5. nie wykonywać automatycznego merge/promote.

Nie zmieniono CKDT core ani zasad 100k.


## 26. Kontynuacja 2026-09-26 — kompletność ranking/evidence dla modułów

Po usunięciu fałszywego komponentu `s` size-study #179 ujawnił drugi problem pipeline:
`KeyError: 'szulborze'` w `scripts/build_pl_preview.py`, w sortowaniu:
`key=lambda w: (rank_of[w], -zipf[w], w)`.

Przyczyna:
- część `terc_forms` była dodawana do `ranked` dopiero po obliczeniu `zipf`, `spell` i po utworzeniu `rank_of`;
- przez to legalna, jawna nazwa TERC mogła wejść do wspólnego zbioru kandydatów bez odpowiadającego wpisu metryki.

Naprawa:
- commit `cecf1e1f76182a3346c2e88dacaecf31e93cdc23`;
- wszystkie source-backed module forms są dopisywane do `ranked` przed wyliczeniem `zipf`, `aosp`, `spell` i `rank_of`;
- `base_candidate_words` nadal pozostaje wcześniejszym snapshotem czystego wordfreq i nie jest rozszerzany;
- nie zmieniono immutable core ani zasady net-new union.

CI po tej poprawce:
- preview #234 — in progress;
- size-study #180 — in progress;
- first-name audit #94 — in progress;
- wszystkie trzy są uruchomione na `cecf1e1f...`.

Poprzedni preview #233 zakończył się błędem w kroku AOSP, niezwiązanym z kodem kapitalizacji.
Poprzedni size-study #179 zakończył się `KeyError: szulborze`; ten błąd jest adresowany przez powyższą poprawkę.

Po green CI obowiązuje dalsza kontrola:
- rzeczywisty net-new union,
- `module-study-report.json`,
- `module-frequency-report.json`,
- selected/full TERC,
- finalny audit capitalization,
- paczka testowa telefonu dopiero po przejściu wszystkich bramek.


## 27. Kontynuacja 2026-09-26 — pierwszeństwo audytowanej kapitalizacji imion

Preview #236 (na cc073ea1...) przeszedł wszystkie wcześniejsze bramki, ale końcowa walidacja wykazała brak 48 wybranych imion w formie wielkiej litery, m.in. Albert, Daniel, Marek, Mikołaj, Paweł, Wiktor, Wiktoria.

Diagnoza architektoniczna:
- audit_first_name_homonyms.py jawnie klasyfikuje 48 nazw jako capitalized_homonym_names;
- generate_first_name_inflections.py generuje formy selected first-name jako capitalized, poza 5 jawnie wskazanymi wyjątkami lowercase-common-noun;
- ogólny audit kapitalizacji wykonywał jednak wcześniej regułę common-noun -> lowercase;
- zmienna selected_first_names nie wystarczała dla form odmiany, ponieważ modułowy audyt pracuje na first-name-inflection.

Naprawa:
- commit 7601712915622521c9b0f52a896cec17445cc32e:
  - core capitalization audit traktuje first-name-inflection z polityką wyłącznie capitalized jako jawnie audytowaną kategorię przed generic common-noun lowering;
  - module capitalization audit stosuje tę samą zasadę dla form first-name inflection;
  - lowercase_common_noun pozostaje wyjątkiem jawnie zdefiniowanym w first_name_surface_policy.tsv;
  - mieszane źródła (lowercase + capitalized) nadal wymagają jawnego rozstrzygnięcia;
- commit 52aa2abe5d6a7c48cc98288ffe2a382a083c0c5e doprecyzował kontrakt w nagłówku modułowego audytu i uruchomił nowe CI.

Stan branch:
- ostatni commit zmieniający kod: 52aa2abe5d6a7c48cc98288ffe2a382a083c0c5e;
- aktualny HEAD branch jest późniejszym commitem dokumentacyjnym; przed dalszą pracą zawsze odczytaj rzeczywisty HEAD z GitHub.
- nie wykonano merge/promote;
- CKDT 100k nie został automatycznie zmieniony.

CI po tej zmianie:
- preview #238 — 52aa2a..., in progress;
- size-study #184 — 52aa2a..., in progress;
- first-name audit #96 — cc073e..., success;
- starszy size-study #182 na cc073e... zakończył się success i potwierdził budowę wariantów 50k/100k/125k/150k bez błędów pipeline;
- starszy preview #236 na cc073e... jest failed wyłącznie na końcowej asercji 48 imion, którą adresuje powyższa poprawka.

Zielony size-study #182 dał:
- net_additions_over_100k_base = 5688;
- warianty: 50k, 100k, 125k, 150k;
- new_words_from_50k_to_100k_pct = 100.0;
- new_words_from_100k_to_125k_pct = 25.0;
- new_words_from_125k_to_150k_pct = 14.75;
- pełna weryfikacja CKDT/paczki zakończyła się success.

Nie traktować #182 jako ostatecznego audytu kapitalizacji po poprawce imion; ostateczna akceptacja wymaga green run na 52aa2a....

Następny krok:
1. sprawdzić wynik preview #238 i size-study #184;
2. jeśli green, odczytać aktualne artefakty module-study-report.json, module-frequency-report.json, raport kapitalizacji i paczkę preview;
3. dopiero potem przejść do testu telefonu/swipe;
4. nie wykonywać merge/promote.


## 28. Kontynuacja 2026-09-26 — `Gdynia` i zawężenie definicji homonimu

Preview #238 na 52aa2a... zakończył się końcową asercją `assert "Gdynia" in ckdt_raw`. Wszystkie wcześniejsze bramki przeszły, w tym audyty kapitalizacji. Oznaczało to, że problem leżał na granicy `core audit -> final CKDT surface`.

Analiza kodu wykazała, że audyt core i modułowy używały szerokiej kategorii `common_lexical` do decyzji lowercase. Dedykowany `audit_first_name_homonyms.py` stosuje natomiast węższą i audytowalną definicję: homonim wymaga rzeczownikowej analizy z klasą `nazwa_pospolita`.

Naprawa architektoniczna:
- commit `ae7563140232d7e091d4c95a67288822b9c10ae7`:
  - core capitalization audit: lowercase override następuje tylko dla zweryfikowanej klasy `nazwa_pospolita`;
  - module capitalization audit: `common_noun` jest podstawą decyzji lowercase, a nie samo `common_lexical`;
  - zachowano pełne informacje `common_lexical_matches` do audytu, ale nie używa się ich samodzielnie jako autorytetu kapitalizacji;
- commit `c9078c6e007e91a768c7f7e7813661c3b6dc2c9c`: normalny push komentarza/kontraktu do uruchomienia CI na zmianie `ae7563...`.

Bieżący kod do testowania: `c9078c6e...` (zawiera `ae7563...` oraz komentarz; bez zmian semantycznych po `ae7563...`).

Stan CI przy zapisie:
- preview #240 — SHA `c9078c...`, pending;
- preview #239 — SHA `ae7563...`, in progress;
- size-study #186 — SHA `c9078c...`, in progress;
- size-study #185 — SHA `ae7563...`, in progress.
Starszy preview #238 (`52aa2a...`) failed tylko na `Gdynia`; ta asercja ma teraz zostać przetestowana przez nową regułę.

Ważne: `Gdynia` nie jest poprawiana przez wpis do `surface_registry_policy.tsv`. Źródłem decyzji ma być poprawna klasyfikacja wspólnego audytu; ręczny wyjątek dla nazwy byłby obejściem problemu.

Po green CI sprawdzić szczególnie:
- `Gdynia` i inne oficjalne nazwy geograficzne pokrywające się z bazą 100k;
- `Tomaszów` oraz lowercase `łódź`;
- 48 `capitalized_homonym_names` i 5 `lowercase_common_noun_names`;
- rzeczywisty net-new union oraz raporty modułów;
- dopiero potem paczkę do testu swipe.


## 29. Kontynuacja 2026-09-26 — przymiotniki administracyjno-geograficzne

Preview #240 i size-study #186 na `c9078c...` ujawniły 17 unresolved core capitalization collisions: `brzeski, chełmiński, gdański, jasielski, lubelski, lubelskie, lubuskie, mazowieckie, mazurskie, opolski, opolskie, pomorskie, sandomierski, wschodni, ząbkowicki, łukowski, łódzki`.

Nie dodajemy tych 17 kluczy ręcznie do surface registry. Ich wzorzec jest zgodny z przyjętą zasadą językową: człony przymiotnikowe nazw administracyjnych/geograficznych mają podstawową powierzchnię lowercase.

Diagnoza kodowa:
- generic capitalization audit używał wcześniejszej kategorii `common_lexical` do obniżania tylko wtedy, gdy był to homonim; jednocześnie mixed source policies pozostawały unresolved;
- dedykowany audyt imion definiuje homonimię wężej jako `nazwa_pospolita`;
- zatem dla przymiotników potrzebna jest osobna, jawna reguła ortograficzna, a nie wymuszanie kolejnych wpisów ręcznych.

Naprawa:
- commit `9f0b45755289c260650c7d4cc2d2f67b4195e9d2`: core capitalization audit rozpoznaje zwykłe analizy `adj:` jako podstawę lowercase, przy zachowaniu ochrony przed innymi POS;
- commit `88320090cb42cc38ba235c380566f160092925ef`: module capitalization audit stosuje tę samą regułę dla surface modułów i zapisuje analizę przymiotnikową w raporcie.

Ważne:
- `surface_registry_policy.tsv` nie został rozszerzony o te 17 pozycji;
- `Tomaszów` pozostaje jawnie `capitalized`;
- `mazowiecki`, `pomorski`, `śląski` itd. mają pozostać lowercase jako przymiotniki;
- `łódź` pozostaje lowercase na podstawie jawnej polityki rzeczownika pospolitego.

Ostatnie CI przed tą poprawką:
- preview #240 — failed na 17 unresolved core capitalization collisions;
- size-study #186 — failed na tym samym audycie core.

Po commit `8832009...` oczekiwane są nowe runy. Następna bramka to sprawdzenie, czy unresolved core = 0 bez ręcznego dodawania 17 wyjątków.
