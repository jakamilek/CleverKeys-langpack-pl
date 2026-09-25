# Dictionary sources strategy

## Goal

Build the Polish CleverKeys language pack using high quality open data where licensing allows redistribution.

## Candidate source categories

### Hunspell Polish dictionaries

Use existing Polish Hunspell-compatible dictionaries as a starting point.

Verification:
- license compatibility,
- update history,
- number of words,
- duplicate rate,
- invalid forms,
- archaic and rare entries,
- encoding quality.

### Language corpora

Use open corpora only as a frequency reference, not as direct word import.

Processing:
- frequency extraction,
- normalization,
- profanity filtering where needed,
- manual review of technical terms.

### Custom mobile layer

Maintain separate additions:
- Android terminology,
- IT terms,
- communication words,
- common abbreviations.

## Import pipeline

external source
    -> license check
    -> normalization
    -> quality analysis
    -> frequency ranking
    -> CleverKeys format

No external dictionary should be merged directly without validation.
