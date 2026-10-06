# Polski MLM — ostrożny ranking v4

| Populacja/okno | HerBERT raw | distil raw | distil gated |
|---|---:|---:|---:|
| fresh_short_known_key/forms/16 | 15/16 | 13/16 | 13/16 |
| fresh_short_known_key/forms/32 | 15/16 | 13/16 | 13/16 |
| fresh_long_known_key/forms/16 | 12/16 | 12/16 | 11/16 |
| fresh_long_known_key/forms/32 | 11/16 | 11/16 | 11/16 |
| fresh_short_new_key/forms/16 | 12/16 | 12/16 | 11/16 |
| fresh_short_new_key/forms/32 | 12/16 | 12/16 | 11/16 |
| fresh_long_new_key/forms/16 | 11/16 | 11/16 | 11/16 |
| fresh_long_new_key/forms/32 | 10/16 | 11/16 | 11/16 |
| regression_v5/forms/16 | 50/64 | 46/64 | 46/64 |
| regression_v5/forms/32 | 50/64 | 46/64 | 46/64 |

Nowe autorskie konteksty; nie zewnętrzny benchmark. regression_v5 to development replay. Próg zamrożony przed inferencją.
Brak aktywacji SI, zmiany domyślnego kontekstu, pomiaru telefonu i publikacji wag.

{"primaryWindow": 16, "newValidationCases": 64, "gatedTotals": {"cases": 64, "top1": 46, "baselineTop1": 32, "repairs": 15, "regressions": 1, "overrides": 16, "utility": 11}, "rawTotals": {"top1": 48, "repairs": 17, "regressions": 1, "utility": 13}, "checks": {"regressionsAtMostTwo": true, "regressionsAtMostRaw": true, "utilityAtLeastRaw": false, "top1ImprovesDefault": true, "atLeastEightOverrides": true, "allStrataAtLeastBaseline": true, "allStrataAtMostOneRegression": true}, "exploratorySafeCandidate": false, "developmentReplayReferenceQualityGate": {"candidateTop1": 46, "referenceTop1": 50, "oldRequirementReferenceMinusOne": false, "usedForNewPolicyQualification": false}, "productionApproved": false, "default16Approved": false}
