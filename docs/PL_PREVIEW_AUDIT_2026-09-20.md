# Polish preview audit — 2026-09-20

## Result

A first 50,000-word Polish CleverKeys preview was generated from controlled external evidence.

This is a **preview/staging artifact**, not a production promotion to `source/`.

## Locked inputs

- CleverKeys runtime: `tribixbite/CleverKeys@263bd0abc03dec420f60fa073a9d2c5e25a176b5`
- Language project main baseline: `jakamilek/CleverKeys-langpack-pl@e1a136ea84d4365a36e9ba4fc405d1c6d27a71c8`
- `wordfreq`: `rspeer/wordfreq@912caf64b657478d1dff1138efdc078947d54bb1` (3.2.0)
- Polish `wordfreq` large-data blob: `3be96f3eacf5b8d886a2df3eeb9d4e893212eef5`
- AOSP Polish word list SHA-256: `75a7a488e014ec3b9dbdb2527f09bca6bb28c250232d9ba50cb0ee1f8738ea45`
- LibreOffice Polish Hunspell source: commit `32b006a2c22a4ac7e8ed3f03346f7b3d85a970a4`

## Evidence run

Input candidates: 100,000.

- AOSP headword set: 191,690
- AOSP overlap with candidate universe: 81,117
- Hunspell-accepted candidates: 85,111
- candidates containing Polish diacritics: 38,542
- edit-distance typo candidates identified: 442
- foreign-dominance candidates identified: 1,596

Selection:

- final preview dictionary: 50,000 words
- band 1: 48,891
- band 2 with positive oracle: 1,085
- explicit project guards: 24
- reviewed typo blocklist rows: 16
- reviewed error forms present in the candidate stream: 14
- active dictionary contained 0 of the reviewed error forms after filtering

## Runtime package

The package was generated with the current CleverKeys build tools at the locked runtime SHA:

- CKDT magic: `0x54444B43`
- CKDT version: 2
- dictionary word count: 50,000
- package version: 2
- `hasPrefixBoost: false`
- ZIP entries: `dictionary.bin`, `manifest.json`, `unigrams.txt`

Preview ZIP SHA-256:

`6139d243f0137f24ca510103b163f1fffefa6f516991f481efa0cab8929025ea`

GitHub Actions preview run: 35498880429

## Regression checks

Canonical one-word forms present:

- `rzeczywiście`
- `można`
- `cześć`
- `wziąć`
- `włączać`
- `który`
- `naprawdę`
- `już`

Reviewed error forms absent from the active dictionary:

- `rzeczywiscie`
- `mozna`
- `czesc`
- `wogole`
- `napewno`
- `wziąść`
- `włanczać`
- `ktory`
- `ktury`
- `wogule`
- `odrazu`
- `narazie`
- `niewiem`
- `naprawde`
- `jusz`
- `wziasc`

Note: multiword corrections such as `wogole -> w ogóle`, `napewno -> na pewno`, `niewiem -> nie wiem` are retained in the separate autocorrect corpus. The current CleverKeys runtime's direct autocorrect alias path is not a general arbitrary multiword replacement engine, so those mappings must not be represented as fake single-word dictionary entries.

## Promotion status

Not promoted to `source/`.

Next human-controlled step: install this preview in CleverKeys and test prediction/autocorrect behaviour. After app validation, the approved word list can be promoted from staging through the controlled source pipeline.

## Later size-study clarification (2026-09-23)

The 50,000-word result above is the initial preview checkpoint. A later reproducible size study compared 50,000, 75,000 and 100,000-word variants from a common 200,000-candidate window using the pinned CleverKeys CKDT V2 runtime. The runtime did not impose a 50,000-word hard maximum. The 100,000-word variant was therefore retained as a valid importable candidate, while 50k/75k/100k remain comparison points for quality/size trade-offs.

For the current project pipeline, **100,000 words is the working preview target** unless a later evidence-based decision changes it. This does not mean lower-quality candidates bypass filters: the same source, typo, foreign-language and regression gates remain active.
