# Module surface identity and capitalization policy
Date: 2026-09-26

## Decision

The project uses two different identities and must never confuse them:

1. **Source-unit identity** — identifies the real source object for provenance and audit.
2. **Dictionary-surface identity** — identifies the normalized word/surface key stored in the CKDT dictionary.

For TERC, the source-unit identity is `level + terc`.
For dictionary capacity and CKDT uniqueness, identity is case-insensitive surface key.

Therefore two distinct TERC units may share one dictionary word without creating two dictionary entries.

Example:
- unit A: gmina X, TERC code A
- unit B: gmina X, TERC code B

The audit retains both source-unit records and provenance, but the production dictionary contains one case-insensitive key for the surface X.

## Required pipeline

### 1. Keep source identity intact

Generators and audit artifacts retain one record per real TERC unit:
- level;
- TERC code;
- source name;
- generated case/form;
- provenance.

A generator must not collapse two source units merely because their names are equal.

This is necessary for traceability, but it is **not** a reason to duplicate dictionary keys.

### 2. Deduplicate at dictionary-surface level

Before final CKDT construction, all active modules and the immutable core are projected to:

`surface_key = Unicode-lowercase(surface)`

The same key is stored once.

Capacity accounting uses the union of these case-insensitive keys.

Cross-module duplication therefore has zero additional capacity cost.

The final dictionary remains:

`100000 + union(net-new case-insensitive module keys)`

### 3. Canonical surface is a separate decision

Each normalized key has one canonical CKDT surface.

The canonical surface must carry:
- selected surface spelling;
- capitalization policy;
- category/source provenance;
- all contributing source-unit/category references in the audit layer.

The builder must not silently choose a capitalization when two modules provide conflicting canonical surfaces.

If the same normalized key has incompatible surface policies (for example lowercase lexical adjective versus capitalized proper name), the condition is an **audit conflict**, not an automatic merge decision. CI should report the conflict and block CKDT promotion until the canonical surface is explicitly resolved.

## Capitalization policy

Capitalization is determined for the **dictionary surface**, not inferred from the fact that an item belongs to a module.

### General categories

- ordinary vocabulary: lowercase;
- first names: capitalized, except explicitly audited common-noun homonyms that are intentionally lowercase;
- cities/localities: capitalized;
- countries and capitals: use the audited official canonical Polish spelling;
- manual/custom forms: explicit row-level capitalization policy;
- geographic/proper-name-derived ordinary adjectives: lowercase.

### TERC

TERC must not use one blanket capitalization rule.

The capitalization audit distinguishes the linguistic form of the administrative name:

- **voivodeship names** used as administrative names: lowercase;
- **powiat adjectival names**: lowercase;
- **city names / cities with powiat rights**: capitalized;
- **gmina names**: determine from the actual name:
  - noun/proper-name form: capitalized;
  - adjectival administrative name: lowercase.

The gmina rule must be evaluated from the controlled source plus the linguistic analysis used by the project; it must not be implemented as “all gminas uppercase”.

Rada Języka Polskiego states that names of contemporary administrative districts are written lowercase when the name element is adjectival, e.g. `województwo małopolskie`, `powiat krakowski`, `gmina warszawska`. A gmina whose name element is an independent proper noun can be capitalized, e.g. `gmina Będzin`. citeturn371147search0turn838405search26

## Consequence for the current TERC implementation

The change in commit `a5ff83b0a522293aec68c47f74a13277f624e2d4` that preserves `level + terc` identity is retained because it protects provenance.

It must not be interpreted as permission to emit duplicate CKDT surfaces.

The correct architecture is:
- one row per TERC unit in the full audit material;
- selected production candidates may still reference multiple TERC units;
- final surface registry collapses equal case-insensitive keys;
- CKDT contains one canonical surface per normalized key;
- conflicts in canonical casing are audited explicitly.

## No automatic capitalization winner

When two active sources contribute the same normalized key with different capitalization policies, the system must not guess.

Instead record:
- normalized key;
- all candidate surfaces;
- category;
- source/provenance;
- policy;
- selected canonical surface, once explicitly resolved.

This prevents silent loss of linguistic information while keeping the CKDT dictionary free of duplicate keys.

## Relationship to morphology

Inflection generation is performed per source item/lemma for auditability.

After generation:
1. validate each form linguistically;
2. apply the category-specific capitalization policy;
3. normalize to the case-insensitive dictionary key;
4. deduplicate across source units and modules;
5. preserve all contributing provenance in audit records;
6. run the final capitalization gate on the chosen canonical surface.

A low-frequency form is not removed merely because it is duplicated by another source unit. Duplication is solved by set union, not by arbitrary frequency pruning.

## Tests that must exist

CI should assert at minimum:

1. duplicate TERC source units can coexist in audit data;
2. duplicate case-insensitive surfaces consume one dictionary key;
3. all final CKDT keys are unique case-insensitively;
4. no unresolved capitalization conflict reaches CKDT;
5. TERC voivodeship and adjectival powiat forms are lowercase;
6. city proper names are capitalized;
7. gmina capitalization is decided per name, not by one blanket rule;
8. first-name lowercase homonym exceptions remain protected;
9. ordinary derived adjectives remain lowercase.

This policy is an architectural clarification, not a change to the immutable 100k core or to the agreed TERC retention counts:
- 16 voivodeships — full inflection;
- 380 powiats — selective inflection;
- 2479 gminas — nominative only in production.


## TERC production boundary

The complete `build/pl-terc-inflections.tsv` / `build/pl-terc-flat.tsv` material is audit/source material.

The production TERC surface layer should be represented by `build/pl-terc-inflections-selected.tsv` only. It contains the nominative records needed for all retained units plus the retained inflection forms according to the 16/380/2479 policy.

The preview/CKDT builder should not independently inject TERC names from the full audit layer in addition to the selected production layer. This prevents two TERC representations from becoming competing capitalization authorities.

The full TERC artifact remains available for:
- provenance;
- excluded-form audit;
- source-unit identity;
- retention review;
- regression testing.

The selected TERC artifact is the single production contract for the TERC module.
