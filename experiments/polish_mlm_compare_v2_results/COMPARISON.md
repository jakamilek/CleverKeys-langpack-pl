# Polski MLM v2 — Geotrend / distilHerBERT / historyczny HerBERT

| Populacja/zadanie/okno | HerBERT (referencja v1) | Geotrend Distil | distilHerBERT |
|---|---:|---:|---:|
| regression_v5/forms/16 | 50/64 | 40/64 | 46/64 |
| regression_v5/forms/32 | 50/64 | 40/64 | 46/64 |
| regression_v5/recorded_replay/16 | 7/8 | 1/8 | 7/8 |
| regression_v5/recorded_replay/32 | 7/8 | 1/8 | 7/8 |
| regression_v5/single_variant/16 | 6/6 | 6/6 | 6/6 |
| regression_v5/single_variant/32 | 6/6 | 6/6 | 6/6 |
| regression_v5/ambiguous/16 | 0/0 | 0/0 | 0/0 |
| regression_v5/ambiguous/32 | 0/0 | 0/0 | 0/0 |
| regression_v5/missing_key/16 | 0/2 | 0/2 | 0/2 |
| regression_v5/missing_key/32 | 0/2 | 0/2 | 0/2 |
| regression_v5/punctuation_before_word/16 | 15/20 | 10/20 | 17/20 |
| regression_v5/punctuation_before_word/32 | 15/20 | 10/20 | 17/20 |
| new_natural/forms/16 | 24/32 | 21/32 | 25/32 |
| new_natural/forms/32 | 24/32 | 21/32 | 25/32 |
| new_distance_control/forms/16 | 16/32 | 16/32 | 16/32 |
| new_distance_control/forms/32 | 18/32 | 16/32 | 19/32 |
| new_punctuation/punctuation_before_word/16 | 20/24 | 11/24 | 16/24 |
| new_punctuation/punctuation_before_word/32 | 20/24 | 11/24 | 16/24 |

Autorska diagnostyka znanych kluczy, historyczna referencja; brak niezależnego benchmarku.
Top3 par nasycone z konstrukcji; naturalne 16/32 mają identyczne wejście.
Pełne rankingi, naprawy/regresje i osobny dystans/interpunkcja w comparison.json.
Brak pomiaru telefonu, aktywacji SI i redystrybucji wag. Licencja distilHerBERT niewyjaśniona.

{"geotrend_distil": {"caseOnlyMobileCandidate": false, "identicalShortInputsCheck": true, "productionApproved": false, "limitations": "Known diagnostic data; natural contexts <=14 words have identical 16/32 inputs. No default-window decision; artificial distance/punctuation separate."}, "distilherbert": {"caseOnlyMobileCandidate": true, "identicalShortInputsCheck": true, "productionApproved": false, "limitations": "Known diagnostic data; natural contexts <=14 words have identical 16/32 inputs. No default-window decision; artificial distance/punctuation separate."}}
