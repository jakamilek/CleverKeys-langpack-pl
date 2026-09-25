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

## Inflection policy

Every category generator should be capable of producing the complete validated singular paradigm first. The final dictionary then decides which forms are retained.

Retention should depend on:

- frequency of the base lemma;
- practical usefulness of the particular grammatical case;
- source confidence of the generated form;
- available dictionary capacity.

This preserves full provenance even when a rare form is not selected into CKDT.

## Capitalization gate

Every retained surface must pass a final capitalization gate before CKDT creation.

Policies are:

- ordinary vocabulary: lowercase;
- adjectives derived from proper/geographical names: lowercase;
- proper names and their grammatical forms: audited capitalization;
- city and administrative names: canonical capitalization from the controlled source.

A capitalization violation fails the build.

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
