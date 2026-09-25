# NKJP1M acquisition audit — 2026-09-25

## Verified source

The module-frequency audit uses the NKJP1M tagged frequency snapshot at pinned
revision:

- project: `wojciech.jaworski/ENIAM`
- revision: `be02836cf3aa0286ad8961d2e4528cdc2f72d044`
- file: `resources/NKJP1M/NKJP1M-tagged-frequency.tab`
- acquisition route used successfully in CI: legacy GitLab
  `repository/archive.tar.gz` endpoint, restricted to `resources/NKJP1M`
- SHA-256 of the extracted target file:
  `fee31b1d6a682970b4e8ca68b593aea8dadbc8541e875e2d287480d83601e79c`

## Validation performed in size-study #79

Run: `36175350217`  
Commit: `7633c863d162fff869ad37d5b2b09db2b749b102`

Validated file properties:

- size: 12,181,895 bytes
- valid data rows: 183,181
- total positive frequency count across rows: 1,215,509
- exact column count: 8
- UTF-8 decoding: passed
- HTML/login/error-page rejection: passed
- expected SHA-256 pin: passed

The previous direct raw endpoint is **not** treated as the successful acquisition
route. The reproducible acquisition now uses the host-supported archive endpoint,
and CI is pinned to the verified SHA-256.

## Frequency audit result from #79

The historical #79 audit covered 4,020 unique surface/lemma pairs across:

- first-name forms: 1,759
- official one-token city names: 844
- selected city inflections: 1,218
- reviewed morphology: 123
- reviewed proper nouns: 76 (historical early-test pilot; retired from active module accounting after #79)

Global surface-frequency distribution:

| Signal | P10 | P25 | P50 | P75 | P90 | P95 |
|---|---:|---:|---:|---:|---:|---:|
| NKJP1M count among nonzero surfaces | 1 | 1 | 2 | 7 | 24 | 51 |
| wordfreq Zipf among nonzero surfaces | 1.49 | 2.01 | 2.58 | 3.13 | 3.83 | 4.18 |

Observed source coverage:

| Module | NKJP seen | NKJP zero |
|---|---:|---:|
| first-name forms | 736 / 1,759 | 1,023 |
| city names | 292 / 844 | 552 |
| city inflections | 537 / 1,218 | 681 |
| reviewed morphology | 46 / 123 | 77 |
| reviewed proper nouns | 63 / 76 | 13 |
Interpretation rule:

- NKJP remains the primary frequency signal.
- wordfreq remains an independent secondary signal.
- A zero NKJP count is not treated as linguistic frequency zero.
- No retention threshold has been selected from this run.

## Next measurement step

The next step is to inspect the module distributions and NKJP/wordfreq
disagreements by module and by individual form, then document data-driven
retention tiers. The immutable 100k core remains unchanged and protected.

## Active-module interpretation after #79

The 76-form reviewed proper-noun pilot was an early runtime-test/anchor set, not a production category. It has been removed from active staging and preserved only as historical material at `sources/archive/reviewed_proper_nouns_pilot_2026-09-25.tsv`.

Therefore the 76 forms and their 63/13 NKJP coverage are retained as an auditable historical result, but they must not be used in current module-capacity totals or retention-threshold calibration. A new frequency audit is required after active-module cleanup before setting any thresholds.
