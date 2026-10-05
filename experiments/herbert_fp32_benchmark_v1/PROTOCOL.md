# HerBERT FP32 benchmark package v1

Explicit follow-up to herbert_mobile_v1, whose FP32 passed and INT8 preservation failed.
No edits to the previous freeze, comparisons, requests or quantization gate. No training.
The same exporter and pinned environment must reproduce the exact FP32 SHA256
f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 and 651798883 bytes.
Any different hash stops publication and requires investigation, not automatic repinning.
FP32 archived score tolerance remains 0.001 with zero full-ranking changes on 232 requests.

Portable tokenizer tables are derived from the original cased Char-BPE fast tokenizer:
50000 vocabulary entries, original merge ranks/IDs, </w> suffix, no unknown fusion,
no byte fallback, no dropout, five unnormalized special tokens. Unsupported attributes fail.
Probe pinned Rust normalizer/pre-tokenizer behaviour for every Unicode scalar; persist
compressed classification ranges rather than depending on Android Unicode categories.
Independent reference interpreter must match the original tokenizer on archived contexts,
surfaces, seeded random Polish/Unicode inputs, special-token edges, every range boundary
and 4352 exhaustive scalar blocks. Android/Kotlin must separately match the saved vectors
and all five inputs of every archived candidate batch before a phone benchmark is accepted.

Weights are uploaded only after exact identity, FP32 parity and reference tokenizer checks.
Upload reports separately (small downloadable metadata); the benchmark bundle has model.onnx,
tokenizer.json, portable-tokenizer.json, tokenizer-conformance.json, android-score-vectors.json,
NOTICE.txt and manifest.json. Android imports must bind every file hash to a trusted identity,
not accept a manifest's own self-declared hashes as authentication. Stage privately, bound
actual decompressed bytes, reject unknown/duplicate/unsafe members and clean up failures.
The manifest is benchmarkOnly; it grants no live-IME activation. No model in Git or APK.

No renewed quality claim, timing claim or reduced threshold. Actual phone load latency,
tokenization/feed/inference p50/p95, peak process RAM, thermal behaviour and repeated runs
remain required. Baseline geometric and both source-confirmed case surfaces stay intact.
