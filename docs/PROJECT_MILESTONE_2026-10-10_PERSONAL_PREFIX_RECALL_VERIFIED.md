# Personal prefix recall — verified ARM64 build

## 1. Identity and bases
UTC2026-10-10 / Europe-Warsaw2026-10-10. Runtime trial53767fdf57684aed459226b824a0885a3e031e6c. Runtime main before this docs-only checkpointdb06020459baf1f9536d24087ceaded80a62647a; producer main79fb15e5e0d54adb637bf011c0db418b0d50f0a4. Matching11-section file on both mains; prior source/checkpoints retained.

## 2. Architecture
Geometric + original opt-in HerBERT FP32 compact-case-v4/context32/deadline350ms/privacy/single-publish unchanged. Active explicit personal entries have a derived first1..3-character index. Prefix matching spans punctuation/digits; literal stored spelling preserved. Letters-only prefixes merge personal first + aligned/deduped ordinary results; structured prefixes use literal path.

## 3. Accepted task
User reports completion of both extension runs. Verify exact head, all gates, APK identity and hashes; provide installable phone update and focused prefix recall checklist. Prior clipboard/idle/whole-entry-save behavior was phone accepted but recall missing. New recall has not yet been phone tested.

## 4. Exclusions
No model/langpack/producer/geometry/gesture/settings-default/dependency/version, merge/release/tag change. No tests/gates bypassed, subagents or fabricated local build/device result. Completed-run inspection only, no waiting/poll loop; monitoring<=60s/run.

## 5. Implementation
DictionaryManager invalidates structured completion index on existing userWords mutations/language reload. Bounded whole-token/collapsed absolute caret/editor/field snapshots protect taps. Entry presence and disabled status rechecked. Selection+commitText atomically replaces both halves, keeps surrounding text and follows field spacing policy; refused commit restores caret without pre-deletion. Private/password/selection/Termux suppression; no absolute caret=>ordinary path. Recognized identifiers bypass fragment autocorrect/learning, capitalization and SI. Clipboard/startup/explicit add unchanged.

## 6. Verified results and remaining checks
Live38073753788/job114276317462 and CI38073754846/job114276321058 COMPLETED/SUCCESS at exact53767fdf. All required steps passed.
Runtime/instrumentation compilation;2906 registered pure tests; original2471tokenvectors/232batches/532candidates/five-input conformance PASS. Live11 integration suites246tests and standard18 suites323tests PASS (overlapping; never additive). Bookkeeping52/52 (44 retained+8 new), ten new pure completion cases and clipboard controller11 passed.
Debug lint XML0 Error/Fatal236 Warning, release vital lint PASS. Security114276320969/codequality114276320843/size114280009087 PASS. Assemble/ARM64 audit/uploads PASS.
One extra InlinedApi warning for EditorInfo.IME_FLAG_NO_PERSONALIZED_LEARNING API26/min24; integer constant is inlined, not a newly invoked Android method. Record consolidation into existing LearningGate for a later code change; no minSDK/suppression/gate change in completion turn.
Local archive/hash/identity/XML verification only; no local Kotlin/Android execution. Instrumented View tests compile-only. Phone recall/latency/editing verification pending.

## 7. Branches, PR and runs
Draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with final behavior, successful exact validation and artifact identity.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38073753788 and CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38073754846 SUCCESS. Trial unchanged53767fdf; no new code push/run just for completion.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60/draftPR13 unchanged. Both mains docs only.

## 8. Artifact/model identity
Artifact11678128425/cleverkeys-herbert-live-trial-arm64 expires2026-10-24.
ZIP35834829B SHA256f1bc004b753c52b7b0dc19dd77df9fbf1d6be4c01759d7fe1b66602c98585d4b.
APK35833244B SHA256752faacfa02d4dfb0aaa2db8713f4b4227585d0ec64753b7eaedda5b75e67cee.
ZIP+APK locally downloaded/rehashed; metadata commit53767fdf, byte size and structuredDictionaryPrefixCompletion/clipboardLabelAndHoldPanel/startupFrequentWords/explicitStructuredDictionaryAdd=true verified. Libraries all arm64-v8a; no >50MB ONNX or portable-tokenizer/tokenizer-conformance/android-score-vectors fixtures.
Reports11678442914/22865B SHA25616cdbad4f31440b2c2f66b13d7b1c3e349823f45a12c2fa3cb414dbef51216a8 locally downloaded/rehashed, lint XML inspected.
Original separate FP32 SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged; no model reimport. Previous APK11677595285 lacks recall, do not confuse them.

## 9. Limits/backlog
Explicit keyboard-managed active-language entries indexed, no new cross-language/Android-provider store. Case-insensitive literal prefixes do not invent diacritics. Same-prefix entries shorter then spelling, no usage calibration. Absolute readable collapsed caret required. Actual phone prefix behavior and native performance pending.
InlinedApi consolidation above; Polish priority retained, no new strings. Other locales, nine missing dictionary keys+kapitalizacją/kapitalizacje/source usage priors, SI native RAM/quality and stationary BS timing options remain separate.

## 10. Phone next
Install verified ARM64 update without deleting app data; retain saved words and imported model. Type beginning of saved email, then punctuation-bearing prefix; choose it, check no duplicated prefix/suffix and exact case. Check hyphenated entry, BS refresh, middle cursor replacement, email/search no trailing space and ordinary options after letters-only prefix. Deleted entry should disappear. After acceptance return to agreed dictionary task.

## 11. Delta
All required automated gates passed; new prefix-recall APK locally verified and ready for phone testing. No new production or producer code in completion turn. PR and both docs-only mains record actual results, warning and manual checks. Phone success is not yet claimed.
