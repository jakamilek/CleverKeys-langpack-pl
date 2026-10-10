# Ordinary text-field typed-autocorrect undo — follow-up pending CI

## 1. Date and heads
UTC2026-10-10. Runtime main before checkpoint2ef631c8d04e84cc0b4ca6b90ce1e1daf92d9e00; producer main6c1193b05d2a1fe9ab8ba2079048d80a0dd7c2c3. Runtime trial moves from b047d3fcd5e2b566b751fe91a12a757cead94962 to 57c15c38389418a01801502a9ae8b3b92eccf7e3. All previous docs/source/checkpoints retained; both mains receive only this new document.

## 2. Current architecture
Geometric + original opt-in HerBERT FP32 remain unchanged, with compact-case-v4, context32/deadline350ms, existing metadata/form/editor/privacy guards. Clipboard paste action stays separate from predictions. Typed autocorrect is an editor/caret/token-specific transaction supporting a preserved trailing space or no separator.

## 3. Accepted request
User reports a similar typed-word/autocorrect problem in an ordinary text field after delivery of the clipboard/search APK. Repair immediate BS restore in ordinary fields and retain ExactAdd without field mutation. No long Actions wait; max60s/run. Polish/localization priorities, deferred dictionary and BS timing remain.

## 4. Rejected/unapproved changes
No weakened editor/caret/password/token/field checks, suffix-only undo, altered automatic spacing or user settings, SI/dictionary/model/data/gesture/dependency/default change. No release/version/tag/main code merge. Exact phone app/editor trace unavailable: do not claim that the found state dependency is the only phone cause or that the phone fix is verified.

## 5. Found dependency and change
Old canUndoTypedAutocorrect required both a valid editor bookmark and transient tracker corrected/original/source values. Reset transient state could reject a valid correction before the park callback repopulated it. Current canUndo validates the bookmark first, then seeds the corrected/original AUTOCORRECT pair used by KeyEventHandler from that same transaction. New typing clears bookmarks; editor/caret/token/selection/lifecycle guards remain. Only production method changed. Three registered integration regressions, spec follow-up and memory/todo entry added; four selected blobs with all other hashes/modes preserved.

## 6. Checks and limits
Local production-diff isolation, immutable fetched-base hashes, edited blob hashes/new-tree preservation, valid unchanged spec frontmatter and memory/todo494 lines passed. No local JDK/Kotlin/Android SDK execution. LearningFunnelBookkeepingTest now34 cases: new normal-field real-BS restore after tracker reset, kept space/preceding text/different correction length/ExactAdd without mutation; rejection after typing, another field and moved caret. These new tests are pending CI. Existing search/clipboard suites and all build/conformance/lint/APK gates preserved. Android View tests are compile-only in the live workflow; native execution remains pending.

## 7. PR and runs
DraftPR4 https://github.com/jakamilek/CleverKeysPL/pull/4 ; trial/herbert-live-v1=57c15c38389418a01801502a9ae8b3b92eccf7e3.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38057510660 observed in_progress; standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38057513808 observed queued. Both exact head; no completion wait.
Producer diagnostic branch/PR13 remains unchanged; agreement-v4 stays rejected and archived.

## 8. Artifact identity
No current-head APK verified yet. Successful parent b047d3fcd5e2b566b751fe91a12a757cead94962: live38054606810/CI38054609652;2881 pure/conformance per run,222 live/302 standard integration tests (overlap), required compile/lint/security/size/APK gates PASS. Parent artifact11671965482 ZIP35812222B,SHA-256 d161d1bdf39a016b1c331597c8edf6d273f9b9495e249aaf753da7911484f3a8; APK35810798B,SHA-256 bff4b23b05dd26886b04620941daea90deeaf6aa63d8b4358de61b3600f16f50 verified locally. Parent contains clipboard/search fixes, not the current ordinary-field follow-up. Original imported HerBERT model SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged.

## 9. Backlog and unresolved limits
Phone ordinary-field reproduction/retest on NubiaNX721J/Android15 needed; app/input editor unspecified. ExtractedText availability/editor-specific timing remains a compatibility limit, not solved by bypassing verification. Parent debug lint235 warnings includes one redundant SDK check, recorded for later cleanup. Dictionary nine missing swipe forms and other prior missing forms, usage priors, other locale gaps and BS timing settings deferred. No new instrumentation/device/model quality claim.

## 10. Next after completion report
Read exact new run conclusions, required tests/lint, identity and artifact digest; fix failures before delivering APK. On success test ordinary field: typed token corrected at space, first BS restores whole original keeping exactly one space; ExactAdd leaves text, second BS deletes normally. Repeat search no-space case and reject undo after typing/new field/cursor move. If phone still fails, obtain actual app and observed BS/text behavior and a text-free state trace before broadening editor handling.

## 11. Delta and stop
Previous CLIPBOARD_SEARCH_UNDO_CI_SUCCESS checkpoint remains preserved. This follow-up removes the extra transient-prediction eligibility dependency, adds3 regressions and publishes one new runtime trial commit. PR updated and docs-only checkpoints saved on both mains. CI/phone outcome pending; do not keep monitoring or resume SI/dictionary work.
