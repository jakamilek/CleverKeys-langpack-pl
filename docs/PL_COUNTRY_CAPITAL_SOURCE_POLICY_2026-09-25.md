# Country and capital source policy — 2026-09-25

## Official source

The country and capital modules use the official Commission on Standardization of Geographical Names (KSNG) / GUGiK publication:

- *Urzędowy wykaz polskich nazw geograficznych świata*, Wydanie VIII zaktualizowane, Warszawa 2025;
- 2026 update no. 1, which changes the capital of Equatorial Guinea to **Ciudad de la Paz**.

The 2025 publication's Part I contains 197 states recognized by Poland and gives Polish short country names, inflection information and capitals.

## Module split

Countries and capitals are separate production modules even though they share the same official source.

### Countries

The country module contains the official Polish short name of each state. The base surface is capitalized as a proper geographical name.

Where the official source supplies genitive, locative or indeclinability information, it is retained as provenance. Complete validated paradigms are generated before the category cost is measured.

### Capitals

The capital module contains the primary capital name associated with each state. The 2026 update is authoritative over the 2025 entry for Equatorial Guinea.

Complete validated paradigms are generated before the category cost is measured.

## Flat CKDT rule

The current CleverKeys runtime uses a flat single-token dictionary. Therefore:

- one-token country and capital names can enter the flat CKDT layer;
- multiword and hyphenated country/capital names remain in the complete source/audit data;
- they are not truncated, rewritten or silently discarded;
- they are candidates for a future phrase/multiword layer.

## Morphology

The project first generates all validated forms available from the official source and Morfeusz 2 / SGJP. Retention then follows the general category-admission protocol:

- retain all validated items and forms when the measured category fits its capacity envelope;
- only under real capacity pressure, reduce inflection forms using deterministic frequency, grammatical usefulness and source-confidence evidence;
- never remove a valid form merely because its corpus frequency is low when sufficient capacity exists.

## Capitalization

Country and capital proper-name surfaces are emitted with audited capitalization. Generated forms inherit the explicit case policy recorded with the source item.

A capitalization error fails the build.

## Update policy

When KSNG/GUGiK publishes a subsequent official update, the project must:

1. preserve the previous source hashes and provenance;
2. acquire the new update separately;
3. apply only explicitly documented amendments;
4. rerun source extraction, morphology generation, module measurement and CI;
5. record the new effective source state in a new audit commit.

This policy does not authorize automatic promotion to the production baseline.
