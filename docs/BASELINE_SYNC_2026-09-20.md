# CleverKeys PL baseline sync snapshot

Snapshot date: 2026-09-20

## Official baselines

- CleverKeys application main: 263bd0abc03dec420f60fa073a9d2c5e25a176b5
  - observed commit date: 2026-09-10
- CleverKeys-langpack-pl main: e1a136ea84d4365a36e9ba4fc405d1c6d27a71c8
  - observed commit date: 2026-09-19

## Recovery rule

The application repository is the runtime-format authority. The PL repository is the language-data project baseline.

Before any language-data change:
1. re-read both main refs;
2. record both SHAs in the change metadata;
3. never overwrite a newer main history with an older local snapshot;
4. keep generated packs reproducible and hash them;
5. keep unapproved external data in quarantine;
6. never promote quarantine/staging data automatically.

## Polish language architecture

- flat CKDT V2 dictionary with explicit inflected forms;
- unigrams/frequency support;
- contractions/canonical mappings where applicable;
- autocorrect error corpus and guards;
- allowlist/blocklist;
- phrases and abbreviations as separate curated layers;
- legacy prefix_boost.bin is not a required runtime asset in current CleverKeys; its historical consumer was removed.

## Important backup principle

This file is a point-in-time snapshot, not a substitute for Git history. A later work session must refresh it against current GitHub main before changing language data.
