# Dictionary surface identity and capitalization policy
Date: 2026-09-26

## Status

This is a project-wide architectural rule. It applies to the immutable core,
all additive modules, all generated inflection layers, and the final CKDT build.

The TERC-specific document
`docs/PL_MODULE_SURFACE_IDENTITY_AND_CAPITALIZATION_POLICY_2026-09-26.md`
remains the detailed TERC implementation companion.

## 1. Two identities — never conflate them

Every source-backed record participates in two distinct identity systems:

1. **Source-unit identity** — identifies the real object in the source and is
   preserved for provenance, audit, reproducibility, and review.
2. **Dictionary-surface identity** — identifies the spelling key that can occur
   only once in the final CKDT dictionary.

The source-unit identity may be specific to the source:
- TERC: `level + terc`;
- SIMC/city sources: the source identifier plus its source context;
- first names: audited name record and selection provenance;
- countries/capitals: official source record;
- manual/custom: explicit row identity and provenance.

Dictionary-surface identity is always case-insensitive:

`surface_key = Unicode-lowercase(surface)`

This rule is global, not module-specific.

## 2. Consequences for dictionary capacity

Two source records may be distinct while contributing the same dictionary key.

Examples:
- two different TERC units with the same name;
- a city already present in the 100k core;
- a first name and another module that produce the same surface;
- a country/capital surface that overlaps ordinary vocabulary.

Such overlap is resolved by set union, not by deleting source records.

Capacity accounting therefore uses:

`final_size = 100000 + union(net-new case-insensitive module keys)`

A duplicated surface consumes one dictionary key, while every contributing source
record remains visible in provenance/audit data.

The immutable 100k core is never displaced to make room for an additive module.

## 3. Canonical surface is a separate decision

Each case-insensitive key entering CKDT must resolve to one canonical surface.

A surface record must carry, directly or through the audit registry:
- canonical spelling;
- capitalization policy;
- category;
- source/provenance;
- all contributing source-unit references;
- resolution status.

The final builder must not silently pick one spelling or capitalization when
multiple active sources disagree.

For a single normalized key, compatible duplicate surfaces may be collapsed.
Incompatible capitalization or spelling policies create an audit conflict.

An unresolved conflict must block CKDT promotion.

## 4. Project-wide processing pipeline

All active categories should follow the same conceptual flow:

`source records -> validated forms -> surface registry -> CKDT`

The surface registry is the boundary at which source provenance is separated from
dictionary uniqueness.

Required behavior:

1. preserve source-unit identity in audit material;
2. validate each generated or imported form;
3. assign an explicit category-appropriate capitalization policy;
4. normalize to a case-insensitive surface key;
5. collect all contributors under that key;
6. resolve compatible duplicates deterministically;
7. report and block unresolved conflicts;
8. emit exactly one canonical surface per final key.

No module is allowed to bypass this model merely because its source is small.

## 5. Capitalization is lexical/surface-specific

Capitalization must never be inferred solely from module membership or from the fact that a key belongs to the immutable 100k core.

The capitalization audit runs on the core before module assembly. This is necessary because frequency sources may normalize all candidates to lowercase and can therefore lose proper-name capitalization.

For every source surface, including multiword and hyphenated names, the pipeline preserves the full source record and also analyzes individual word components. Each component is evaluated independently for:
- source capitalization;
- ordinary lexical use, including common nouns and other ordinary parts of speech;
- conflicts with other sources;
- explicit surface policy.

When a non-first-name capitalized candidate has an ordinary lexical homonym and no explicit audited exception, the context-free CKDT surface defaults to lowercase. A selected first name follows its explicit first-name policy. An unresolved mixed-source conflict blocks promotion.

Examples of the general principle:
- ordinary vocabulary: lowercase;
- proper names: capitalized;
- cities/localities: capitalized according to the audited official/linguistic form, after per-component lexical collision analysis;
- first names: capitalized unless an explicitly audited common-noun homonym policy says otherwise;
- geographic/administrative adjectives: lowercase;
- countries and capitals: audited official Polish spelling;
- manual/custom: explicit row-level policy.

A module may therefore contain both lowercase and capitalized surfaces.

The same case-insensitive key may also have contributors with different intended
capitalization. That situation requires explicit resolution rather than an automatic
“module wins” or “uppercase wins” rule.

## 6. Morphology is generated before surface deduplication

Inflection generation is performed per source item so that provenance is retained.

After generation:
- validate the form;
- apply the appropriate lexical/capitalization policy;
- project to the case-insensitive surface key;
- deduplicate only at the dictionary-surface layer;
- retain all contributing provenance in audit data.

Frequency evidence is used for retention decisions only where the category policy
requires it. Frequency must not be used to erase provenance or to decide silently
between incompatible capitalization policies.

## 7. Audit requirements

CI should be able to demonstrate at minimum:

1. source-unit identities remain distinct where the source distinguishes them;
2. final CKDT keys are unique case-insensitively;
3. cross-module overlaps are counted once for capacity;
4. canonical surface selection is deterministic and auditable;
5. unresolved capitalization conflicts cannot enter CKDT;
6. category-specific capitalization rules are enforced;
10. core capitalization is audited before modules so absent modules cannot cause loss of capitalization evidence;
11. multiword/hyphenated source names are preserved for provenance and audited component-by-component;
7. generated inflections retain source and generator provenance;
8. excluded forms remain available in audit artifacts where the category policy
   requires complete-paradigm retention for review;
9. the immutable 100k core remains unchanged by module expansion.

## 8. TERC-specific application

TERC is the first implementation case for this project-wide rule.

For TERC:
- `level + terc` remains the source-unit identity;
- equal names from different units collapse to one case-insensitive dictionary key;
- full TERC material remains audit/source material;
- selected TERC is the sole production TERC surface layer;
- administrative capitalization is determined per linguistic form, not by one
  blanket TERC rule.

The exact 16/380/2479 retention policy is unchanged.

## 9. Migration rule for future modules

When adding a new module, do not invent a new deduplication or capitalization
architecture.

The module must provide:
- source identity;
- validated surface/form;
- explicit capitalization policy;
- provenance;
- deterministic conflict behavior.

It then joins the common surface-registry stage.

This makes the same architecture reusable for first names, cities, TERC,
countries/capitals, controlled brands, and future audited additions.
