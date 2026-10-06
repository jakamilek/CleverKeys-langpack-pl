# Polski MLM — świeże konteksty v3

| Populacja/okno | HerBERT | distilHerBERT |
|---|---:|---:|
| fresh_short_known_key/forms/16 | 15/16 | 16/16 |
| fresh_short_known_key/forms/32 | 15/16 | 16/16 |
| fresh_long_known_key/forms/16 | 16/16 | 15/16 |
| fresh_long_known_key/forms/32 | 13/16 | 15/16 |
| fresh_short_new_key/forms/16 | 16/16 | 16/16 |
| fresh_short_new_key/forms/32 | 16/16 | 16/16 |
| fresh_long_new_key/forms/16 | 15/16 | 16/16 |
| fresh_long_new_key/forms/32 | 13/16 | 14/16 |
| regression_v5/forms/16 | 50/64 | 46/64 |
| regression_v5/forms/32 | 50/64 | 46/64 |

Świeże autorskie konteksty; nie niezależny benchmark. Pełne regresje i limity okien w JSON.
Brak aktywacji SI, zmiany domyślnego kontekstu, pomiaru telefonu i publikacji wag.

{"freshStrata": {"fresh_short_known_key/forms/32": {"top1AtLeastReferenceMinusOne": true, "baselineRegressionsAtMostReferencePlusOne": true, "candidateTop1": 16, "referenceTop1": 15}, "fresh_long_known_key/forms/32": {"top1AtLeastReferenceMinusOne": true, "baselineRegressionsAtMostReferencePlusOne": true, "candidateTop1": 15, "referenceTop1": 13}, "fresh_short_new_key/forms/32": {"top1AtLeastReferenceMinusOne": true, "baselineRegressionsAtMostReferencePlusOne": true, "candidateTop1": 16, "referenceTop1": 16}, "fresh_long_new_key/forms/32": {"top1AtLeastReferenceMinusOne": true, "baselineRegressionsAtMostReferencePlusOne": true, "candidateTop1": 14, "referenceTop1": 13}}, "knownRegression": {"top1AtLeastReferenceMinusOne": false, "candidateTop1": 46, "referenceTop1": 50}, "exploratoryCaseCandidate": false, "productionApproved": false, "default16Approved": false}
