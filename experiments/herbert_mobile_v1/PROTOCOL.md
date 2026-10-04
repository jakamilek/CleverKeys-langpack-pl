# HerBERT mobile export trial v1

2026-10-04. Preparation for Android, not production integration. Frozen before real export.

## Identity and goal

Parent results c4cf02a52c9c71fa1a8c3d7d6e66091f696bd07b. Preserve all earlier freezes/results.
HerBERT allegro/herbert-base-cased, revision 50e33e0567be0c0b313832314c586e3df0dc2297.
Torch CPU 2.8.0, Transformers 4.57.6 and prior requirements; ONNX 1.17.0, ORT 1.21.1.
ORT matches verified Android/JVM dependencies at runtime 6b3b2580094170384e1e0f9a4b72138546ebd884;
the runtime README still says 1.20.0 and is not the dependency source of truth.

Export a graph which implements the previously evaluated whole-word mask score:
mask ALL target subtokens simultaneously, BERT, selected hidden positions, MLM head,
log-softmax over the entire original vocabulary, gather the real target IDs, sum and mean.
No cropped vocabulary, retraining, textual metadata prefix or per-word prompt.
Batch candidates with independent rows and right padding. Dynamic candidates/sequence/target axes.

## Input/output contract

Five inputs, order fixed: input_ids, attention_mask (int64 [B,S]); target_positions,
target_ids (int64 [B,T]); target_mask (float32 [B,T], valid ones followed by padding zeros).
Outputs: mean_log_probability and sum_log_probability, float32 [B].
Maximum S=512, B=12, T=32. Target positions inside attended input and not special boundaries;
zero position/ID padding has target_mask=0. Mean divides by actual target count, never padded count.
No explicit token_type_ids: identical to earlier scoring. Eager attention permits portable ONNX
operators; any resulting numerical/ranking drift is subject to the archived reference gate.

Context is case/punctuation preserving, at most 64 whitespace-delimited words/4096 UTF-16 units
for future Android capture. Only oldest context may be removed for the token budget, jointly for
all candidates. The conversion evaluation requires zero removal because archived contexts fit.
Actual tokenizers must match HerbertTokenizerFast, not generic WordPiece or byte BPE.
Generate real conformance vectors including combining marks, controls, emoji, CJK and added tokens.
Tokenizer implementation on Android must pass those vectors before integration is enabled.

## Pre-registered gates

Use every nonempty plain request (both windows) from the frozen metadata trial. Report every suite,
population and window separately. Missing/duplicate/nonfinite/extra scores fail closed.
Compare batched Torch eager, ONNX FP32 and ONNX INT8 against persisted original scores/ranks.
FP32 and batched Torch require maximum absolute score error <= 0.001 AND zero full-rank changes.
INT8 preservation requires zero top-1 regressions AND zero top-3 regressions relative to reference
on gold-labelled cases in every group. Repairs cannot cancel regressions. Retain all rank changes
including unlabelled ambiguity. These are conversion gates, not an independent quality result.

INT8: dynamic per-channel signed 8-bit constant matrix weights, MatMul/Gemm only,
MatMulConstBOnly=true, reduce_range=false. Shape preprocessing separate; skip graph fusion.
No quantization parameter tuning after results. Export/checker or FP32 parity failure fails job.
INT8 degradation is an explicitly reported completed experiment; no candidate bundle is created.
Neither passing gate certifies phone latency, energy, memory or editor integration.

## Artifacts and privacy

Reports retain source/code/freeze identity, hashed original weights, loading info, individual scores,
paired rank changes, file sizes and host p50/p95. ONNX host feed construction is outside timed region;
three sessions share a host process, so peak RSS is not an isolated INT8 footprint or phone result.
No weights in Git. Upload only an INT8 candidate bundle if BOTH conversion gates pass; include
model/tokenizer hashes, exact tokenizer/score vectors, model revision and CC BY 4.0 NOTICE.
FP32 weights stay temporary on CI. Generated data uses existing synthetic contexts, no phone text.

## Android rollout plan

First live scope: reorder only the source-confirmed case pair of geometric rank 1 in ordinary
Polish text, preserving both choices, original key ranks/scores/languages and commit provenance.
Do not use raw MLM scores to promote other geometric keys; that needs separate calibration.
Explicit Shift/Caps Lock, sentence auto-capitalization and manually selected forms retain priority.
Skip password/private/search/URL/email/non-Polish/selected-text fields; unavailable context/model or
unknown target means unchanged geometric slate. No cloud/network requirement.

Capture editor text just before swipe insertion, on the editor thread, using bounded live
InputConnection reads. Do not enlarge/lowercase the existing two-word n-gram tracker. Async work
must carry editor session, text revision, selection, request ID, language/pack identity and settings
revision; revalidate all on return. Never replace committed text or an already displayed/selected
slate after a late model result. Initial shadow measurements precede visible reranking. Worker
queues at most one latest request; release/cancel closes runs safely; no inference on UI thread.

Future Polish UI: "SI w podpowiedziach", default off; status/model import/removal, modes
"Pomiar bez zmiany podpowiedzi" then "Kolejność wariantów pisowni", context window and later timeout
only after phone measurement. Include search, backups of preferences (not weights/text), reset,
attribution and privacy surfaces. These settings/import/live dispatch are not implemented here.
Separate punctuation head is possible later; no promise this MLM scorer solves punctuation.

## Execution

Stdlib contract tests run before freeze and in CI. Push on experiment/herbert-mobile-v1 runs
export/inference once; PR path runs contract only. No repeated inference while monitoring.
Monitor at most 60 seconds TOTAL per build; user reports completion. No merge/release/version bump.
Next: inspect export/quantization results, implement real tokenizer conformance/import and a phone
shadow benchmark, then independent real contexts/slates and review before enabling live ranking.

Primary references: https://onnxruntime.ai/docs/performance/model-optimizations/quantization.html
https://onnxruntime.ai/docs/tutorials/mobile/
https://huggingface.co/allegro/herbert-base-cased
https://github.com/huggingface/transformers/blob/v4.57.6/src/transformers/convert_slow_tokenizer.py
