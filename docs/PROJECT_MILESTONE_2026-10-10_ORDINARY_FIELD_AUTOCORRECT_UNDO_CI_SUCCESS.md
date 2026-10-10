# Ordinary-field autocorrect undo — CI success and verified APK

## 1. Identity and bases
UTC2026-10-10. Runtime main before docs-only checkpointb0bc7208e15ba145c7cb7da55942beb17fb50b08; producer main25bba739d2b9d6593464c17034f27f091334b6fe. Active runtime trial57c15c38389418a01801502a9ae8b3b92eccf7e3 unchanged. All preceding checkpoints/source preserved.

## 2. Architecture
Geometric + original opt-in HerBERT FP32, compact-case-v4, context32/deadline350ms and privacy/editor single-publish guards unchanged. Clipboard remains separate. Typed-autocorrect bookmark is the authoritative corrected/original pair for immediate BS, independent of transient prediction tracking.

## 3. Accepted task
User reported fresh runs complete. Verify actual CI/test/artifact outcomes, offer the current APK for ordinary-field phone retest and save state on both mains. No long monitoring or automatic restart of dictionary/SI work.

## 4. Scope exclusions
No main code merge, release/tag/version/dependency/settings/default/gesture/model/dictionary/ranking change. No gate bypass. No claim of real-device success from CI; exact ordinary-field phone app/editor and state trace still unavailable.

## 5. Implementation
At57c15c38, canUndoTypedAutocorrect verifies the exact editor/caret/token bookmark before seeding KeyEventHandler’s transient corrected/original/source pair. A prediction reset alone no longer blocks immediate undo. Typed/new-field/caret/selection/text/lifecycle invalidation remains. Four changed blobs: one production method,3 registered regressions, canonical spec follow-up and bounded memory/todo entry.

## 6. Verified results
Live38057510660 and CI38057513808 SUCCESS at exact head. Runtime and Android instrumentation sources compiled.2881 pure tests and mandatory original conformance2471 vectors/232 batches/532 candidates/five inputs passed in each. Live11 integration suites225 tests; standard18 suites305 tests (overlap; never sum). LearningFunnelBookkeepingTest34 cases includes the3 new ordinary-field production-BS restore after tracker reset/different length/preceding text/kept space/ExactAdd and stale typing/field/caret cases. Existing clipboard/search suites passed.
Debug lint0 Error/Fatal,235 Warning, unchanged from parent; release vital lint/assembly/security/code-quality/APK size and no-weights/no-fixtures gates passed. Logs read, report ZIP downloaded/hash checked, pure marker/count and lint XML read independently. No local Kotlin/Android SDK execution; Android View tests compiled, not executed on a device.

## 7. Branch/PR/runs
Trial/herbert-live-v1=57c15c38389418a01801502a9ae8b3b92eccf7e3; draftPR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with results.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38057510660 .
Standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38057513808 .
Producer diagnostic branch86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / draftPR13 unchanged. Rejected agreement-v4 remains excluded. No new trial commit/run after success.

## 8. Current artifact identity
Artifact11670958917 from live38057510660/currenthead:
https://github.com/jakamilek/CleverKeysPL/actions/runs/38057510660/artifacts/11670958917 .
ZIP35812330B,SHA-25610a52a61477f9c274d3effcfbf3d5c1f18113025365df83a4f38cfacae6bba10.
CleverKeys-v2.0.0-arm64-v8a.apk35810906B,SHA-256d886cf5f98b8b5cb956c67c82de34972e3776def7f4fed7695229575bf548bef.
Both downloaded/re-hashed locally; identity exact codeCommit57c15c38389418a01801502a9ae8b3b92eccf7e3,clipboardPasteSuggestion/spaceFreeTypedAutocorrectUndo/liveAI true,optInDefault false,compact-case-v4,context32/deadline350. Local ZIP/APK archive check matches identity and finds no weights/reference fixtures.
Report11671633471 ZIP22471B,SHA-25683472d8ff757b263a356ab5172f60cd88eba63f53e7fea20c707dd76502a7c2a verified.
Original imported HerBERT model SHA-256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged; no reimport needed. Parent11671965482/b047d3fc is historical and lacks this follow-up.

## 9. Limits/backlog
Phone retest on NubiaNX721J/Android15 remains essential. Found source-state dependency repaired; do not state it was the sole phone cause. Editor extraction/timing limits are not bypassed. Native View test execution pending. Other locale gaps, redundant SDK warning cleanup, dictionary nine missing swipe words/prior forms, usage priors and BS timing options remain deferred.

## 10. Next phone test
Install current APK. In ordinary field type a word triggering correction at space; immediate BS restores entire original and keeps exactly one space. ExactAdd stays and adds without changing editor text; next BS deletes normally. Repeat search without trailing space and clipboard checks. New typing/cursor/field changes must reject stale undo. If it still fails, obtain actual app and precise observed BS behavior/text-free diagnostics before changing editor compatibility.

## 11. Delta/stop
Previous ORDINARY_FIELD_AUTOCORRECT_UNDO_STARTED checkpoint remains. Fresh required CI gates pass; current APK/report bytes and identity independently verified. Both mains gain only this document; runtime source stays57c15c38389418a01801502a9ae8b3b92eccf7e3. Deliver test APK and await manual feedback, no continued monitoring or dictionary/SI implementation.
