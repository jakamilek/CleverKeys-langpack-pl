# Architecture Decision Record
# Runtime / Langpack separation

Date: 2026-10-02

Status: ACCEPTED

## Decision

`CleverKeys-langpack-pl` and `CleverKeysPL` remain separate repositories.

The repositories are not merged.

## Repository ownership

### CleverKeys-langpack-pl

Source of truth for:

- Polish language data
- dictionary sources
- morphology
- capitalization rules
- proper names
- language metadata
- future language models

### CleverKeysPL

Source of truth for:

- Android runtime
- swipe engine integration
- candidate handling
- ranking integration
- runtime APIs

## Integration model

The integration model is:

```
CleverKeysPL runtime
        |
        v
Language Intelligence API
        |
        v
versioned language package artifact
```

## Rejected alternative

Monorepo model:

```
CleverKeysPL
 └── langpack-pl
```

Reason for rejection:

- language data has an independent lifecycle
- language evolution should not require runtime releases
- language packages should remain independently auditable
- future languages should be supported by the same runtime architecture

## Experimental branches

Branches containing unified runtime and langpack experiments are experimental only.

They are not the canonical repository architecture.

## Future work

Possible future extensions:

- language metadata API
- context scoring API
- POS metadata
- capitalization metadata

No repository merge is planned.

## Project rule

GitHub is the source of truth. Do not recreate a monorepo design without a new architecture decision.