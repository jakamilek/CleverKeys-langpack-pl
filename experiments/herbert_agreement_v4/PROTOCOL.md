# HerBERT agreement V4 — frozen diagnostic, not a live change

This experiment follows rejected V2 raw-sum and V3 context-gain policies. The original live FP32 mean scorer, model bytes, tokenizer, APK and dictionary remain unchanged. Geometric remains responsible for finger-trace matching; this host diagnostic has no gesture data and does not measure geometric quality.

## Two stages registered before actual inference

Stage 1 compares at most two already supplied lower-case form keys and four declared surfaces. Forms must share an exact source lemma/POS from lexicalReadings, generatedFormProofs or interpretations, or the existing Polish diacritic fold. Larger/unrelated historical slates bypass this method. This is a conservative experiment scope, not a new production gate or dictionary generation rule.

Select the last two alphabetic lexical words of the existing context (Unicode lexical spans, spelling preserved). For every context word and every candidate surface, mask that **same context word** and leave the candidate visible at the end. All surfaces for a given probe have identical target IDs, target counts and positions. This reverses the original diagnostic question: compare how well the observed nearby words fit each visible proposed form, avoiding directly comparing candidate likelihoods with different target lengths. It is a hypothesis; masked-LM scores are not a grammatical parser or full-sentence likelihood.

The exact formula is fixed: for each context-word probe, pool mean log probabilities across a lower-case key's declared case variants using logmeanexp, i.e. `max + log(sum(exp(score-max))/number_of_variants)`. Average those pooled values across the one or two probes. No fitted coefficients, suffix rules, manual dictionary descriptions, estimated rarity threshold or geometric score mixing. Case pooling can still affect the grammatical score and does not make form selection fully independent of spelling. Stable ties retain supplied source order.

Pack all probes and surfaces in **one actual native batch**, B<=8, S<=512, T<=32. Middle-of-sequence masks and right-hand visible words use the original five-input/two-output graph; no re-export. Portable/fast tokenizer parity and actual single/batched native parity must pass for the new feeds. Sequence/target limits and special tokens are validated before scoring.

Stage 2 performs the original candidate-masked mean scoring for the selected form's case variants only, B<=2, in a second native call. Both native mean and sum outputs must reproduce the original full-batch baseline within 0.001 and preserve its case rank. After that check, retain the original exact case/tie order. Other forms retain their original case preferences and all alternatives remain present.

The proposed order presents one best case per key in form-score order, followed by remaining case alternatives in original mean order. Compare it against (a) original flat mean order and (b) the **same one-best-case-per-key presentation** with original mean selecting form order. Ordinal rank values are used solely to reuse outcome counters, never as model confidence or scores combined with geometry. Unsupported slates retain the complete original order.

## Source provenance and datasets

CI retrieves original model artifact 11312693984 / run 37230171787. All seven original bundle members are rehashed by the immutable V1 trust contract. ORT1.21.1 CPU, threads2/1 and pinned dependencies remain unchanged.

CI separately retrieves dictionary artifact 11303920512 / run 37202645255, source commit 041b28ae4587c531ef73e62933e9151cadb84c33. The inner ZIP must be exactly1713402 bytes with SHA256 aa27d8fdcf8fad698491127de68dc1ebd31a5f9f687621429b25435ba16904cb. Its exact bounded five members, dictionary and metadata hashes and CKDT106363 canonical keys are verified. The 21 complete metadata entries and binary ranks are re-extracted and compared byte-for-byte with the frozen fixture. Original nine metadata entries are unchanged; twelve extra entries provide six real pairs: jagoda/jagodą, róża/różą, kruk/krukiem, kot/kotem, piła/piłą, buk/bukiem. No languagepack modifications.

304 requests remain separately reported:

* Original232 historical requests (224 labelled,8 unknown,4 missing gold). Most are case-only or unrelated multi-key slates and bypass stage1; their preservation cannot validate grammar.
* Existing24 form requests from V1, with actual fresh baseline reproduction.
* V3's24 new case-only controls, with fresh baseline reproduction. Case preservation here is by construction and is not new case-accuracy evidence.
* New24 form requests, six known-source families with one lower/upper-case nominative and instrumental gold each. Contexts are authored, frozen before inference and exact-overlap checked against all280 prior contexts. Forms include new instrumental keys. These are not blinded held-out accuracy data.

Preserve original tokenizer2471 vectors/native232 batches and all V1/V2/V3 contracts, score/rank reproduction and raw source evidence. Archive all new middle-mask feeds, scores, case-stage results, outcomes and eligibility counts, including failures. Report exact Top1, raw candidate-group Top3, form Top1, conditional case correctness, repairs, regressions and explicit denominators for each dataset/population/window and both comparators. Candidate-group Top3 is not full keyboard-strip Top3.

## Acceptance and costs

Quality gate: zero exact Top1, raw Top3, form or conditional-case regressions in every group in both comparators, **and at least one actual form repair** in either form dataset versus the same-presentation baseline. Gains in one group do not cancel regressions in another. A successful workflow only means the diagnostic ran; it does not accept quality or authorize deployment. Any failure keeps live mean unchanged. A future implementation needs fresh independent language cases and Android tests even if this diagnostic passes.

The prospective path uses two sequential native calls, at most eight grammar rows then two case rows; greater compute than one baseline batch is a material cost. Record host preparation/conversion/inference times separately by stage and primary-path p50/p95. `primaryPipelineHostMs` includes diagnostic portable/fast token-parity checks, so is not a clean production latency measurement. Full original replay and extra single-row validation calls are outside primary-path timing; report their total call count separately. No claim about Android latency, RAM or deadline compliance. No editor content, logging, network inference, new APK, release or score thresholds.
