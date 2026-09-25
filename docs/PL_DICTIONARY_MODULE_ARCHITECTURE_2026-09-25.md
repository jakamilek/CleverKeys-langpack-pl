# Polish dictionary architecture: immutable frequency core + additive modules
Date: 2026-09-25

## Decision

The production dictionary is not defined by a single hard total such as 150,000.
It consists of:

1. an immutable **100,000-word frequency core**;
2. additive, auditable **category modules**.

The 100k core is selected from the Polish wordfreq candidate universe after the normal linguistic and quality filters. Category modules must not remove or displace a core key.

## Key identity and deduplication

Dictionary identity is case-insensitive for the purpose of capacity accounting.

Therefore:

- warszawa already present in the 100k core + module entry Warszawa = **one dictionary key**;
- the module may replace the core surface with the audited canonical surface Warszawa, but it does not consume another slot;
- a module form absent from the core consumes one additional unique key;
- the same key appearing in several modules is stored once and carries multiple category/provenance attributes.

The final size is therefore:

100,000 + net-new unique keys from all modules.

## Current modules

### First names

Source selection is the audited official first-name set. Singular forms are generated through Morfeusz 2 / SGJP and the surface policy controls capitalization and common-noun homonyms.

### Polish localities

Current official city names are sourced from GUS TERYT/SIMC. Singular inflection is generated from Morfeusz 2 / SGJP and reviewed overrides where the official proper-name form needs additional source-backed evidence.

### Polish administrative units

Planned module based on GUS TERYT/TERC. TERC contains the names and identifiers of the three-level territorial division: voivodeships, powiats and gminas, with distinct types including cities with powiat rights and Warsaw districts/delegations.

### Countries and capitals

Planned module based on the official KSNG/GUGiK 2025 list. This source provides recommended Polish spellings of country and capital names, selected inflection information, country adjectives and inhabitant names.

### Brands / trade names

Planned as a **controlled practical-keyboard module**, not as an import of all registered trademarks.

A brand candidate should have:

1. evidence that the name is an actual current brand/trade name;
2. evidence of practical relevance in Polish usage;
3. a provenance record identifying the evidence and date;
4. a separate linguistic decision about capitalization and whether Polish inflection is actually used.

UPRP and EUIPO/TMview are suitable for verifying trademark existence. Independent market/brand research can be used only as a selection signal, not as the linguistic source of the spelling.

Registered-trademark databases alone must not be used as a dump: they contain many marks that are irrelevant to normal keyboard typing.

## Retired early proper-noun pilot

The former `reviewed_proper_nouns` pilot was created for early runtime testing and
anchor/regression probing. It is **not an active production module** and is not
included in module capacity accounting or retention decisions.

Its historical source is preserved at:
- `sources/archive/reviewed_proper_nouns_pilot_2026-09-25.tsv`

The archived entries must not be automatically promoted. A future reuse requires
fresh assignment to the appropriate category (for example first names or a
controlled locality/country/brand module), fresh source audit, and explicit
inclusion. Duplicate keys already represented by the 100k core or another active
module do not justify retaining a second proper-noun entry.

## Category admission and inflection protocol

Adding a new category is a defined two-stage process.

### Stage 1 — build the category completely enough to measure it

1. Prepare the audited set of **base words/items** for the category.
2. Validate provenance, identity and capitalization of those base items.
3. Generate the **complete validated singular inflection paradigm** for every applicable base item.
4. Validate the generated forms linguistically and record provenance.
5. Deduplicate case-insensitively against the immutable 100k core and all already-active modules.
6. Measure the category's:
   - number of base items;
   - number of generated surface forms;
   - unique case-insensitive keys;
   - overlap with the 100k core;
   - net-new keys versus the core;
   - overlap with earlier modules;
   - incremental contribution to the final union.

The capacity decision is made **after this measurement**, not before.

### Stage 2 — choose the retained set

**Default:** when the measured category size is comfortably within its agreed capacity envelope, retain **all validated base items and all validated inflection forms**.

A category capacity envelope is not assumed globally. It is established per category only when needed, based on the actual measured cost of that category and the current remaining dictionary capacity.

When the measured category would exceed that envelope:

- retain all validated base items unless a separate quality/provenance rule excludes an item;
- retain inflection forms selectively;
- use frequency evidence together with grammatical usefulness and source confidence;
- prefer a transparent, deterministic retention order;
- preserve the full generated paradigm and the evidence for every excluded form in the audit artifacts;
- after selection, re-measure the category and its **net-new contribution**, including cross-module deduplication.

### Important refinement

Capacity should be evaluated primarily on the **net-new union contribution**, not on the raw count of generated forms. This prevents the same word appearing in several categories from consuming multiple capacity slots.

Frequency is a selection signal only when capacity is genuinely constrained. A low-frequency but linguistically valid form must not be removed merely because it is rare when there is sufficient room.

No arbitrary frequency threshold is introduced before the category has been measured. The threshold, if one is eventually necessary, is calibrated from the observed distribution for that category and documented in the commit that introduces the constraint.

This protocol applies to every future category, including administrative units, countries/capitals and controlled brands.

## Capitalization gate

Every retained surface must pass a final capitalization gate before CKDT creation.

Policies are:

- ordinary vocabulary: lowercase;
- adjectives derived from proper/geographical names: lowercase;
- proper names and their grammatical forms: audited capitalization;
- city and administrative names: canonical capitalization from the controlled source.

A capitalization violation fails the build.

## Retention decision after clean module measurement (2026-09-25)

The clean post-pilot measurement found 2,611 net-new unique keys over the protected
100k core across the active modules. This is sufficiently small that dictionary
capacity is **not** a reason to cut validated low-frequency inflection forms.

Therefore the current active modules use the **full-retention default**: validated
base items and validated generated forms are retained unless there is a separate
quality/provenance/capitalization/regression reason to exclude them.

The frequency-aware selection branch remains available as a **capacity-control
mechanism for future category expansion**, but it is not applied merely because a
form is rare. If a future category exceeds its agreed capacity envelope, the
selection is made after full-paradigm generation and measurement, and the retained
set is chosen deterministically using frequency, grammatical usefulness and source
confidence while preserving the complete excluded-form audit trail.

No numeric frequency threshold is to be invented for the current 2,611-key active
addition set.

## Capacity policy

The 100k frequency core is protected.

Module accounting must report for every module:

- source surface count;
- unique case-insensitive keys;
- overlap with the 100k core;
- net-new keys versus the core;
- overlap with earlier modules;
- cumulative final key count.

Only after all modules are measured should the final CKDT capacity be chosen.

The previous 150k experiment remains a diagnostic measurement, not the definition of the final production size.

## Practical consequence

The correct question is not:

"Can we squeeze everything into 150k?"

It is:

"How large is the union of the protected 100k core and the validated modules?"

If that union is 112k, the production dictionary should be about 112k.
If it is 137k, the production dictionary should be about 137k.
If it grows substantially beyond that, we can then use frequency-based inflection retention to control only the additional forms, without sacrificing core words.

## Audit principle

No module may silently displace a word from the 100k core.

The build system must make every net-new module key and every replacement of a core surface traceable to its source and category.

## Frequency evidence for additive modules

For additive module retention, frequency is measured independently of the immutable 100k core. Absence from the core is not treated as zero frequency.

The primary batch signal is the pinned NKJP1M tagged frequency table derived from the manually annotated one-million-word NKJP subcorpus. The table provides word form, lemma, grammatical tag and frequency; its provenance is pinned to ENIAM revision be02836cf3aa0286ad8961d2e4528cdc2f72d044. The project audit records the downloaded file SHA-256 and explicitly labels the corpus scope as NKJP1M rather than the full searchable NKJP corpus.

The secondary signal is pinned wordfreq Polish frequency. It is used as an independent cross-check and can provide evidence for forms absent from the NKJP1M snapshot.

The two measurements are stored separately. They are not silently combined into one invented frequency number.

Retention tiers are not hard-coded before measurement. First the observed distribution of module-form frequencies is recorded; only then are retention thresholds calibrated together with grammatical usefulness and source confidence. A rare module item therefore does not automatically disappear merely because it falls outside the 100k core, and a frequent module item can remain fully inflected even when all of its forms are net-new keys.

For names and places, source-specific importance (for example official name statistics or controlled geographic status) is treated as a separate evidence dimension, not as a substitute for linguistic corpus frequency.
