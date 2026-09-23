# CleverKeys Polish langpack — project handoff / resume point

## Official baseline and branch

- Official language-project repository: `https://github.com/jakamilek/CleverKeys-langpack-pl`
- Official runtime repository: `https://github.com/tribixbite/CleverKeys`
- Work only on branch: `ops/baseline-sync-2026-09-20`
- Never auto-merge/promote to `main`; `main` must remain untouched.
- GitHub is the only official baseline. Prior Codex/chat changes are migration material and must be audited before promotion.
- Current language-project HEAD at time of this handoff: `2f05a6edf3d978cc36f9ba8a07a806213385b115`
- Latest HEAD message: `Correct first-name surface policy documentation`

## Current product target

- Working preview/package target: **100,000 words**.
- 50k and 75k are comparison variants only; 100k is the established working target and has previously been successfully imported/tested by the user.
- Previous known importable 100k package SHA256: `b7e7b948937aba177c9903149ad78f0cd956d9bf4473847df0a2152b00a1e734`.
- Previous 100k size-study package can be recovered from Actions artifact `10770931374` (size-study run #13), if needed as a reference artifact.

## First-name selection

The selected first-name scope is **470 entries**:

- **215 female + 215 male** from the official 2006–2025 name-history aggregation.
- **20 female + 20 male** historical candidates from `sources/staging/historical_name_candidates.tsv`.
- Combined selection = **235 female + 235 male = 470 selected names**.
- Historical candidates remain staging/review data and are marked `pending-direct-Rymut`; do not treat that status as direct Rymut verification.

Relevant files:
- `scripts/audit_name_history.py`
- `scripts/audit_first_name_core.py`
- `scripts/audit_first_name_homonyms.py`
- `sources/staging/historical_name_candidates.tsv`
- `sources/staging/first_name_surface_policy.tsv`
- `docs/PL_NAME_HISTORY_SOURCE_POLICY_2026-09-23.md`

## First-name surface/casing policy — USER-APPROVED

The Morfeusz/SGJP audit previously detected 53 selected-name forms that also have common-noun analyses.

Final user decision:
- lowercase ordinary-word surfaces: **Jagoda, Lilia, Malina, Melisa, Róża**
- the other **49** detected common-noun homonyms remain **capitalized as first names**
- **Oleksandr** is excluded completely
- **Maila is NOT a special-case first-name exception**; it may remain normally as the inflected/common-word form of `mail`.

Important: `Maila` was not one of the 53 common-noun homonyms in the previous audit. Do not reintroduce it into `first_name_surface_policy.tsv`.

Policy file:
`sources/staging/first_name_surface_policy.tsv`

Current policy file must contain exactly these six rows:
```
Jagoda	lowercase_common_noun
Lilia	lowercase_common_noun
Malina	lowercase_common_noun
Melisa	lowercase_common_noun
Róża	lowercase_common_noun
Oleksandr	exclude
```

The generator must preserve lowercase exceptions through final CKDT emission. Do not let proper-noun canonical-casing logic turn them back into `Jagoda`, `Lilia`, `Malina`, `Melisa`, or `Róża`.

## Homonym audit rule

- Oracle: Morfeusz 2 / SGJP.
- Audit only; Morfeusz/SGJP data is not copied into the distributable dictionary.
- Common-noun homonym detection is an audit signal, not an automatic removal rule.
- User-reviewed surface policy is authoritative.
- File: `scripts/audit_first_name_homonyms.py`
- The audit emits the detected homonym set and the user-approved split into lowercase vs capitalized names.

## Generator / CI requirements

`scripts/build_pl_preview.py` must:
- accept `--first-name-surface-policy`;
- keep the 470 selected-name scope explicit;
- preserve the five lowercase surface exceptions;
- exclude `Oleksandr`;
- keep the remaining selected first names capitalized;
- never allow the old blanket “all common-noun homonyms are removed” rule to return;
- remain deterministic;
- retain the hard swipe-regression blocklist.

Current hard swipe-regression blocklist includes:
`chopin, chopina, goebbels, goebbelsa, catherine, catalina, cameron, carli, carlo, castillo, cali, celli, casino, calli, carrillo, caroli, cassino, compos, gourami, celastial`

Do not reintroduce these as ordinary dictionary entries without a new reviewed decision.

## CleverKeys runtime/testing context

The user's runtime test app is **CleverKeys debug 2.0.0**.

Observed test configuration:
- QWERTY (Polski)
- geometric swipe
- other dictionaries disabled
- swipe typing enabled
- user is testing actual swipe ranking, not tap typing.

Known swipe regression observation:
`SWIPE -> "carli"`
with geometric engine produced candidates headed by:
`carli, carlo, castillo, cali, celli, casino, calli, carrillo, caroli, cassino`.
The runtime candidate `carli` was not found in the inspected `dictionary.bin`, so that specific observation must not automatically be blamed on the Polish pack; user dictionary/custom-word residency is a separate path.

CI runtime baseline remains pinned to:
`263bd0abc03dec420f60fa073a9d2c5e25a176b5`

Do not replace that runtime pin with debug 2.0.0 unless the runtime change is separately audited and intentionally promoted.

## Known successful historical checkpoints

These are useful evidence, but they are **not the final current package** because the first-name surface policy was subsequently changed.

- Polish preview run #41 — success (older configuration)
- First-name 235-per-gender audit run #17 — success (older configuration)
- Size-study run #21 — success; 50k/75k/100k variants built and verified
- Proper-noun coverage audit run #23 — success (older configuration)

Earlier size-study evidence established:
- 50k dictionary.bin ~1.33 MB
- 75k dictionary.bin ~2.03 MB
- 100k dictionary.bin ~2.74 MB
- 100k ZIP was importable and successfully tested by the user.

## Recent failures that should NOT be treated as data-quality verdicts

Several runs failed because CI was being rewired while the surface-policy design changed. Examples:
- stale `Maila` assertion;
- stale expectation of 48 capitalized homonyms;
- old `blocked_names` report key;
- YAML/artifact-path wiring errors;
- old blanket homonym exclusion checks.

These failures were implementation/CI issues, not evidence that the underlying 100k vocabulary target is bad.

## Current CI state at handoff creation

The latest Actions runs are listed in the repository's Actions UI/API. At handoff creation, new runs may still be pending/in progress because every atomic workflow/source change on the work branch triggers CI.

The rule for resuming is:
1. query the newest run on `ops/baseline-sync-2026-09-20`;
2. inspect the actual job/step result, not only the run title;
3. when green, download the fresh preview/size-study/audit artifacts;
4. verify the final 100k CKDT directly;
5. confirm:
   - 470 selected names considered;
   - 469 active after excluding `Oleksandr`;
   - exactly five lowercase first-name surfaces;
   - `Oleksandr` absent;
   - remaining selected names capitalized;
   - hard regression blocklist absent;
   - reviewed morphology and proper-noun forms present;
   - manifest/CKDT are valid and deterministic;
   - ZIP SHA256 recorded;
6. only after all checks pass should a package be offered for user phone testing.
7. Never merge to `main` automatically.

## Repository continuity rules

At the beginning of a resumed session:
- refresh the language-project branch SHA;
- refresh the CleverKeys runtime SHA;
- inspect current CI status;
- inspect the latest relevant artifacts;
- do not trust stale local files over GitHub.

Every change:
- small atomic commit;
- work branch only;
- preserve provenance;
- keep staging/quarantine sources separate from production;
- no automatic promotion.

## Immediate next step

Wait for the first fully fresh CI cycle after the final surface-policy correction, then inspect the generated 100k artifact rather than relying only on the audit JSON.

The desired final surface semantics are:
- `jagoda`, `lilia`, `malina`, `melisa`, `róża` → lowercase ordinary words;
- selected proper names including the 49 retained homonyms → capitalized;
- `Oleksandr` → absent;
- `maila` → ordinary vocabulary/morphology path, not a first-name special case.

Do not change these decisions without an explicit new user decision.
