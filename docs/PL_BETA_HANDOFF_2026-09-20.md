# CleverKeys PL beta handoff

## Verified baseline
- Repository: `jakamilek/CleverKeys-langpack-pl`
- Working branch: `ops/baseline-sync-2026-09-20`
- Pre-pilot verified commit: `43d946b6c27381983d49984a96f2e455f2c28b6c`
- CleverKeys runtime pin: `263bd0abc03dec420f60fa073a9d2c5e25a176b5`
- Historical language-main baseline: `e1a136ea84d4365a36e9ba4fc405d1c6d27a71c8`

## Verified build #12
- Run ID: `35503835188`
- Result: SUCCESS
- Artifact: `cleverkeys-pl-preview`
- Artifact ID: `10603226852`
- Outer artifact SHA-256: `777ed9bae197df05bcb947ef7f45afb4c43f4f9bfc3d24a3aeb55fc2386823c6`
- Importable inner ZIP contains exactly: `dictionary.bin`, `manifest.json`, `unigrams.txt`
- Importable pack SHA-256: `ad66869e8f2ad28e5a3c699eba7be44b39487878e0e3e37c4f4fb45eb752027f`
- Manifest: `code=pl`, `version=2`, `wordCount=50000`, `hasPrefixBoost=false`

## Regression guard
The canonical CKDT must reject:
`chopin`, `chopina`, `goebbels`, `goebbelsa`, `catherine`, `catalina`, `cameron`, `carli`, `carlo`, `castillo`, `cali`, `celli`, `casino`, `calli`, `carrillo`, `caroli`, `cassino`, `compos`, `gourami`, `celastial`.

## Real-device status
The verified #12 pack imported successfully and was tested on a real device. Swipe works very well; no major problems found so far.

## Morphology pilot
Source: `sources/staging/reviewed_morphology.tsv`
Families:
- `dopasować`
- `przypomnieć`
- `zweryfikować`
- `zobaczyć`
- `czat`
- `kukurydza`

The pilot uses explicit reviewed forms. It does not relax the global foreign-language filters or the hard regression blocklist. Review its Actions artifact and real-device behavior before expanding it.

## Working rules
1. Never modify `main`.
2. No automatic merge/promote.
3. Keep functional changes small and auditable.
4. Verify each concrete Actions run and artifact before declaring a build current.
5. Distinguish language-pack contamination from Android UserDictionary/custom words.
6. Hunspell is a build-time oracle, not a runtime source.
7. `sources/staging/autocorrect_errors.tsv` is regression/audit data, not runtime source.
8. Prefer explicit reviewed morphology families before introducing a general-purpose inflection generator.
9. Dictionary membership is checked directly from the built CKDT artifact; real-device testing is reserved for runtime ranking/selection behavior.

## Next review
Inspect the morphology pilot build for supplemental forms, any 50k-cap displacement, regression-guard results, CKDT/ZIP, and real-device behavior.


## Morphology pilot result — run #20 (2026-09-22)

- Run ID: `35770028140`
- Commit: `fd94429e49b1e4c968467d72089b577308be2f88`
- Result: `SUCCESS`
- Reviewed morphology families: `6`
- Reviewed forms: `82`
- Supplemental forms outside the original top-100k candidate stream: `38`
- Reviewed morphology forms present in final preview word list: `82/82`
- Final kept words: `50000`
- Regression blocklist: `13` blocked forms
- Inner importable ZIP SHA-256:
  `04d40eb12025795b52baff08e3ed2549288880287dd88ba525c1ce2673a7f7d1`
- Artifact ID: `10713961189`
- Outer artifact SHA-256:
  `a74220a7bc5eca2cc40439694ef373d1f1331f2c82331de77fc724ee8009bef9`

A single pilot conflict was found in run #19: `kukurydze` was removed by the existing diacritic-alias suppression even though it was an explicitly reviewed morphology form. The fix was to exempt reviewed morphology forms from that suppression. Run #20 confirmed all 82 reviewed forms are retained.

## Morphology pilot result — run #21 (2026-09-22)

- Run ID: `35772138965`
- Commit: `76e0bdd68f27305c0b6d0db7851a9a58ac37bcd1`
- Result: `SUCCESS`
- Reviewed morphology families: `6`
- Reviewed forms: `83`
- Supplemental forms outside the original top-100k candidate stream: `39`
- Reviewed morphology forms present in the final CKDT: `83/83`
- Final CKDT word count: `50000`
- Regression blocklist present in final CKDT: `0`
- Required spot-checks: `zweryfikują` present; `czatu` present
- Inner importable ZIP SHA-256: `3dc38c5cd67269f8245641c37f9ceb0a5e0f38aeaccfc0b0dbb2d64d695f9c28`
- Artifact ID: `10713929544`
- Outer artifact SHA-256: `8ff7f7c39a5826b22de264a0f39122efbe1ef2475481ac44e265bfde06a6fbac`

The run #21 artifact was parsed directly from CKDT V2 using the same word-record structure enforced by the workflow. The final binary contains exactly the same 50,000 words as `build/pl_words_preview.txt`, and all 83 explicitly reviewed morphology forms are present. The new form `zweryfikują` is present in CKDT; `czatu` was also confirmed present, so any remaining phone-side issue for `czatu` is a runtime ranking/selection question rather than pack membership.
