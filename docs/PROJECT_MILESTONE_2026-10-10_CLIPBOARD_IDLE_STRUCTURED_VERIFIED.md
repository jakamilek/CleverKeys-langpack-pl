# Clipboard, opening words and complete dictionary entries — verified build

## 1. Identity and bases
UTC2026-10-10 / Europe-Warsaw2026-10-10. Runtime trial head 8375724e2527b48b0c7e048d98ff894bb37f46e8; runtime main before this docs-only checkpoint 4ec61b65e5a51820be59e11dc0862150534160d6; producer main 9f2c6da95900643dfc38bdb0d2b3ed44a18df327. Same11-section status file on both mains; previous checkpoints/source retained.

## 2. Architecture
Geometric + original opt-in HerBERT FP32 compact-case-v4/context32/deadline350ms/privacy/editor single-publish unchanged. Separate clipboard chip uses existing panel. Opening frequent words use gated personal counts and primary dictionary fallback. Explicit structured ExactAdd writes existing personal dictionary without editor rewrite.

## 3. Accepted work
User reports completion. Verify both exact-head runs, every gate and installable APK identity, then provide phone build/checklist. Retain clipboard icon+Schowek/tap paste/hold panel, frequent idle words and full email/hyphen entry add. Accepted ordinary-field BS/autocorrect behavior preserved.

## 4. Exclusions
No merge/release/tag/version/dependency/settings-default/langpack/producer/model change. No test/lint/security/conformance bypass, invented local Kotlin execution or device pass. No subagents. Completed-run verification uses no wait loop; monitoring<=60s/run.

## 5. Implementation and resolved harness causes
Feature implementation35c7ba28 unchanged by last two repairs. Narrow3ce3b70 repair supplies typed predictor result for g instead of real uninitialized Android dictionary implementation. Second8375724e repair explicitly returns no contraction mapping for g/grzeje and no paired variants for g, eliminating relaxed mock empty String. All44 cases preserved with exact grzeje/one typed call/editor g assertions. Production typing/invalidation/queued callback paths still run.

## 6. Verified results and pending
Live38070883727/job114267869451 and CI38070886854/job114267878673 COMPLETED/SUCCESS at exact8375724e2527b48b0c7e048d98ff894bb37f46e8. All required steps passed. Runtime+instrumentation compilation;2896 pure tests including mandatory original conformance2471token vectors/232batches/532candidates/five inputs PASS. Live11 integration suites238tests; standard18 suites315tests PASS, overlapping, not additive. LearningFunnelBookkeepingTest44/44 and clipboard controller11/11 PASS.
Debug lint XML locally inspected:0 Error/Fatal,235 Warning; release vital lint PASS. Security114267878796/codequality114267878897/size114270447321 PASS. Live assemble, packaging audit and uploads PASS. Mock backing-field and existing lint warnings remain; not a zero-warning claim.
No local Kotlin/Android build/test; source check and artifact hash/archive verification locally. Instrumented View tests compile only. New phone functionality/quality tests pending.

## 7. Branches, PR and runs
Draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated around final behavior, exact validation and artifacts.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38070883727 and standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38070886854 SUCCESS. Trial ref remains8375724e2527b48b0c7e048d98ff894bb37f46e8; no new code push or gratuitous run. Producer diagnostic branch86ab57abecebcff3c290fc269fd78ab5e2a7cf60/draftPR13 unchanged; both mains docs only.

## 8. Artifact and model identities
ARM64 artifact11677595285/cleverkeys-herbert-live-trial-arm64, expires2026-10-24.
ZIP35825481B SHA256 d5fdd7854739ac35c5f372d906c208a19d4396fb1bbd4f186802d90a00f67b9e.
APK35823944B SHA256 ff3571fc0509f8f35d3ff626d1ff4fd321e5b7efb6b871ac0e8e5ed4d6cee354.
Both locally downloaded/rehashed; metadata commit matches8375724e2527b48b0c7e048d98ff894bb37f46e8, byte size and clipboardLabelAndHoldPanel/startupFrequentWords/explicitStructuredDictionaryAdd=true. ARM64 ORT libraries; no >50MB ONNX or portable-tokenizer/tokenizer-conformance/android-score-vectors fixtures.
Reports11677695099,22739B, SHA2565cb43fc40b824633f8251952a2b65f98923d254082906fea637a60fff37b981c locally downloaded/rehashed; debug lint XML235warnings.
Original separately imported FP32 model SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged. Existing model import retained; this APK is no model reimport.

## 9. Limits and backlog
Phone icon/label/tap/hold/idle/complete-add and editor/autocorrect regression checks pending. Idle usage remains process-wide with active-language membership filtering, not per-language counters. No new mid-address completion.
Polish/base labels done; other locales deferred. Dictionary nine reported missing keys plus kapitalizacją/kapitalizacje, source usage priors, native AI RAM/quality and stationary BS timings remain separate.

## 10. Next phone checks
Install verified ARM64 update. Copy sample text/open keyboard: Schowek plus frequent words; tap pastes exactly; hold opens clipboard without paste. Type first letter/switch field: no late idle overwrite. Explicitly save complete przykład.ten@gmail.com and czarno-biały: original text/space preserved, saved entries persist and prompt disappears. Check short BS restores typed autocorrection in ordinary/search fields. Retain private/password clipboard/learning restrictions. If accepted, return to agreed dictionary backlog.

## 11. Delta
Both repaired harness runs green; full required gates passed and exact feature APK verified, ready for phone testing. Runtime production code and producer unchanged in this completion turn. PR and matching docs-only mains now record successful automated validation, identity and remaining manual checks.
