# Source casing variants — first producer implementation

Status: trial producer implemented; Android integration pending. No AI/CTC changes.

`scripts/build_variant_trial.py` adds the accepted Language Intelligence API v1
member to a pinned successful Polish preview. CKDT and unigrams are copied byte
for byte. It does not rebuild or promote the production vocabulary.

The input is the automatically generated Morfeusz casing proof frozen at
`e654720e5bcbe9825747b74df2b7d82cdfac4eaa`, with results at
`90b836adb4970c3fcc1cf44bbbc3a2ea45e2da52`. The copied fixture has SHA256
`6bbdf928c338d44ab3eddb76f8a1fe9f0b4a789cb1d51f55740f55826a21e2e2`.
It is evidence from nine audited keys, not a manually curated production
allowlist and not full dictionary coverage. No per-word meanings are added.

Output entries have `surfaceKey`, `canonicalForm`, `capitalization.defaultSurface`
and `capitalization.variants`. Full raw interpretations, categories, form proofs
and source records are retained under optional `metadata.sourceEvidence`.
All source provenance remains in the top-level `provenance`. It is optional
audit information; the rendering provider only needs the capitalization fields.
The manifest declares only the capabilities actually exported: lexicon,
frequency, capitalization, metadata. It does not claim normalized morphology
features or complete common-noun/proper-name coverage.

The producer verifies source and base hashes, CKDT identity/count, unique
lowercase keys, original canonical forms, interpretation IDs, proof links and
category/form associations. It requires source attribution and emits stable
UTF-8 JSON and ZIP member order/timestamps. Byte identity of compressed ZIPs
is verified within the same Python/zlib environment; cross-version compression
identity is not claimed.

The base is preview run `36916501466`, artifact `11189614575`, source commit
`a1fa0193fc504e5fe81d9d43c23fd9a1e52ad307`, not regenerated current main.
There are 106363 CKDT keys, 9 metadata entries, 8 dual-form entries and one
single-form control (`łódzki`). No surname `Łódzki` or street interpretation
is invented. The trial increments package version 2 to 3; it is not a release.

Run:

```sh
python3 -m unittest discover -s tests -p 'test_variant_trial.py' -v
python3 scripts/build_variant_trial.py \
  --base-pack <downloaded-preview>/build/cleverkeys-langpack-pl-preview.zip \
  --evidence tests/fixtures/source-casing-proof-v1.json \
  --evidence-sha256 6bbdf928c338d44ab3eddb76f8a1fe9f0b4a789cb1d51f55740f55826a21e2e2 \
  --notice docs/VARIANT_TRIAL_NOTICE.txt --out-dir build/variant-trial
```

The new CI workflow runs the 21 producer/source contract tests, downloads the
pinned preview and publishes a trial artifact, including its report/SHA file.
It does not install a keyboard or assert swipe accuracy. The historical
artifact must remain downloadable; hashes prevent substitution if it changes.

Old keyboards do not consume the new sidecar. Importing this trial there does
not enable dual-form suggestions. The Android work remains explicitly pending
in `SOURCE_VARIANTS_ANDROID_INTEGRATION_V1.md`.
