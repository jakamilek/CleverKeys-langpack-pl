# HerBERT agreement V4 — measurement complete, policy rejected

Run [38050273413](https://github.com/jakamilek/CleverKeys-langpack-pl/actions/runs/38050273413) completed SUCCESS on code ca2b8e347edba036f2be2d9af3a8e2984a0d32ea. Contract/measure and every step passed. The pre-registered quality gate failed: allPreservationPassed=false, hasFormImprovement=true, qualityGatePassed=false. Do not implement this agreement policy in the keyboard. The existing original FP32 mean runtime remains unchanged.

V4 scored the same last two observed context words with each candidate visible, pooled case variants by logmeanexp, selected a form, then checked the original mean capitalization stage in a second native call. Cases, formula and source evidence were frozen before inference; no fitted coefficients or dictionary exceptions.

| Separate dataset | Labelled | Exact Top1 mean → V4 | Repairs / regressions | Form Top1 mean → V4 | Form repairs / regressions | Raw group Top3 mean → V4 | Top3 regressions |
|---|---:|---:|---:|---:|---:|---:|---:|
| Historical232 requests | 224 | 157 → 157 | 0 / 0 | 9 → 9 of16comparable | 0 / 0 | 218 → 218 | 0 |
| Existing form24 | 24 | 18 → 19 | 3 / 2 | 20 → 19 | 3 / 4 | 23 → 23 | 0 |
| Case-only controls24 | 24 | 20 → 20 | 0 / 0 | No form comparison | 0 / 0 | 24 → 24 | 0 |
| New form24 | 24 | 20 → 17 | 1 / 4 | 23 → 20 | 1 / 4 | 23 → 23 | 0 |

Both comparators (original flat mean, and the same one-best-case-per-key presentation) have the same aggregate accuracy and regression counts. Full per-population/window metrics and every changed outcome remain in raw scores.json. Repairs do not cancel regressions in another group.

Case preference within the gold form is unchanged: history144/200, form24 22/24, case controls20/24, new forms21/24. This is preservation by construction, not a new capitalization-quality gain. Historical216case-only and16large unrelated slates bypass the grammatical stage; their unchanged results do not validate grammar. History has8unknown labels and4missing gold, explicitly retained.

## Examples that matter

* “Gdzie leży wieś ” still chooses **Pracą**, then Praca, praca, pracą. Form score praca−9.975818310055748, pracą−9.641812208952356. It did not fix the originally reported example.
* Three other Praca nominative cases improved, including “Ta wieś nazywa się ”, “Na mapie widnieje wieś ” and “Pytam o wieś o nazwie ”.
* “Spotkam się z panią ” regressed Maliną→Malina; “Rozmawiam z panem ” regressed Laską→Laska.
* Existing form errors also appeared after “Spotkamy się obok wsi ” and “Podróż zaczniemy od wsi ”: correct lower-key pracy became praca, with capitalization errors already present in the mean baseline.
* New form regressions: “Do klasy dołączyła uczennica o imieniu ” Jagoda→Jagodą; “Stolarz tnie deskę ostrą ręczną ” piłą→piła; “Trasa przebiega między Poznaniem a ” Piłą→Piła; “Wykład wygłosi dziś profesor ” Buk→Bukiem.
* New repair: “Nowym trenerem został pan ” Kotem→Kot.

There were no Top3 regressions within these small candidate groups. This does not establish full phone-strip Top3 or universal candidate availability. Correct case is still ranked fourth in some previously failing groups; preserving alternatives alone is not evidence of a better form scorer.

## Technical verification and cost

CI: mobile13 + portable5 + V1 13 + V2 7 + V3 18 + V4 18 tests PASS. Original2471 tokenizer vectors,232 batches/532 candidates native/feed parity and fresh V1/V2 replay PASS. Source pack re-extraction of21 complete metadata entries and binary keys/ranks PASS. Actual middle-mask single/batched native outputs and selected-case mean/sum reproduction PASS, maximum recorded error0.

Independent post-download audit checked all304 IDs/context/surfaces/gold; reproduced280 prior mean/sum scores and ranks; compared all frozen hashes; reconstructed all48 active middle-mask batches including exact visible candidates, targets, positions, padding, masks and budgets; independently recalculated pooling/form order, both presentation orders, all conditional-case/outcome/group counters and timing quantiles. This was a result/feed audit using the original portable tokenizer, not a local new inference. Source re-extraction and frozen contract were rechecked locally.

Active stage1:24existing forms+24new forms, B8; total528 native calls in the measurement script (48 baseline calls plus96 two-stage calls plus384 single-row parity calls), in addition to the separate V1/V2 replay. Single-row validation is outside primary-path timers.

Host p50/p95: grammar batch80.64/114.76ms; selected-case stage26.64/36.19ms; primary pipeline109.54/152.64ms. These are CPU host timings on this runner, not Android, RAM or deadline measurements. Batch-stage timers include array conversion and native scoring/checking, without isolated tokenization preparation. Primary pipeline includes input preparation and diagnostic portable/fast tokenizer parity checks. There is no fair same-shape production speed comparison or clean preparation/inference decomposition. This increases compute and requires two sequential calls; quality failure already blocks deployment.

## Artifact identity and preserved evidence

Artifact11669641343 herbert-agreement-v4-reports, ZIP93808B, SHA25698b19809aa6cce328887598fceeeec0b4c445eb79673ffbeacc7fa279fa59b46; downloaded, rehashed and bounded extraction verified.
Raw scores.json706925B, SHA25616aa94eeac63cff130a411405685893e09c09a3e7f7afb18ee68c588852c1027, Git blobddc56838a4c3dc02c40a7886c458469a78de9407. Stored verbatim alongside this report. Every feed and score used by the new policy is preserved in the raw file.
Model unchanged:651798883B SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2; ORT1.21.1 CPU2/1, numpy2.2.3,tokenizers0.22.2. Original model artifact11312693984/run37230171787 and source pack artifact11303920512/run37202645255.

No scorer/APK/model/export/langpack/threshold/editor/privacy/release changes. No new run. The architecture can still separate geometry, form selection and capitalization; this particular observed-context scoring hypothesis failed to provide a safe improvement. Do not fit a threshold on these48 form labels or add word-specific fixes. A new grammatical method needs independent evidence and source-backed morphology; dictionary coverage remains a deferred separate task.
