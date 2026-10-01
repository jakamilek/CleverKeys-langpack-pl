# Dual-casing runtime patch — 2026-10-01

This directory contains the first runtime experiment prepared against the pinned
CleverKeys runtime SHA:

`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

The patch is intentionally NOT wired into the runtime pipeline yet.

## Files

- `src/main/kotlin/tribixbite/cleverkeys/casing/CaseVariantResolver.kt`
- `src/test/kotlin/tribixbite/cleverkeys/casing/CaseVariantResolverTest.kt`

## Behavior

One lowercase lexical key can expose two first-letter casing surfaces.

Example:

`malina` -> `malina`, `Malina`

The resolver keeps one lexical identity. It does not add two dictionary candidates.

The preferred surface starts from the already audited default. A learned preference
can switch the primary surface only after:

- at least 5 observed uses of the candidate variant;
- a lead of at least 2 uses over the competing variant.

These numbers are experimental parameters, not a production decision.

Sentence-start capitalization, Shift and Caps Lock stay outside this resolver.

## Why this is not wired yet

The current runtime's geometric ranker deduplicates candidate words by lowercase,
and the current `PredictionResult` has no case-variant field. The intended next seam
is after lexical ranking and before suggestion-bar presentation.

The next integration stage must test:

1. carrying variant metadata alongside one lexical candidate;
2. rendering primary + alternate in the suggestion bar;
3. selecting the alternate without rewriting the word manually;
4. learning the selected surface locally;
5. preserving sentence-start capitalization separately.

## Verification

The resolver logic was independently compiled and exercised on the host JVM.

Result:

`CASE_VARIANT_RESOLVER_SELFTEST=PASS`

The GitHub runtime patch should later be executed with the project's pure JVM
test runner, for example:

`./gradlew runPureTests -PtestClass=casing.CaseVariantResolverTest`

No dictionary, core membership, swipe geometry or ranking changes are part of this patch.
