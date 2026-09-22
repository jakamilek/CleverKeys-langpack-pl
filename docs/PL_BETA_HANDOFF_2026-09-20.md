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
- Importable pack SHA-256: `ad66869e8f2ad28e3a5c699eba7be44b39487878e0e3e37c4f4fb45eb752027f`
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

## Next review
Inspect the morphology pilot build for supplemental forms, any 50k-cap displacement, regression-guard results, CKDT/ZIP, and real-device behavior.
