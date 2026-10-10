# Clipboard/search undo — compile failure repaired, fresh checks pending

## 1. Date and repository heads
UTC 2026-10-10. Runtime main before this docs-only checkpoint: 17d854fac3a76ec407d68349d681daf03e61db85; producer main: ade9cb889572b763b8005ba38af1dc95e2500e39. Runtime trial parent d1ccc7e61e95e0506cf85217e51a8d080bbe5395, new head b047d3fcd5e2b566b751fe91a12a757cead94962. Previous checkpoint PROJECT_MILESTONE_2026-10-10_CLIPBOARD_SEARCH_UNDO_STARTED.md and all older documents/source are retained.

## 2. Architecture and active implementation
Geometric decoding, optional original imported HerBERT FP32 with bounded forms/case and compact-case-v4 display remain unchanged. Default context32 and deadline350ms, privacy/editor/single-publish guards remain. ClipboardPasteSuggestions presents a separate localized current-clip paste action before editing. Verified typed-autocorrect bookmarks support actual trailing-space or no-space endings, including search/URI text fields, independently of automatic-spacing eligibility.

## 3. Accepted scope
User reported runs completed. Inspect their actual outcomes and fix the implementation within the already-authorized app scope. Clipboard paste must be exact and stay outside word ranking/learning; BS restores the whole original typed token and keeps ExactAdd. Preserve BS gestures, haptics, spacing rules and settings. Prioritize Polish translation. Do not wait for Actions completion; max60s monitoring/run.

## 4. Rejected/unapproved changes
No tests or compile/lint/conformance/security/APK gates removed or weakened. No model, dictionary, langpack, source metadata, SI ranking, gesture, dependency, defaults, release/version/tag or main code changes. Rejected agreement-v4 experiment stays excluded. No latest APK is claimed before success.

## 5. Failure and precise repair
Live38054047905 job114218767853 and CI38054050655 Build and Test job114218775741 both failed compileDebugKotlin on SuggestionHandler.kt:523 with unresolved InputType references. The new nonpassword text-field guard lacked import android.text.InputType. New trial b047d3fcd5e2b566b751fe91a12a757cead94962 adds that import only in production code and one memory/todo failure note; two changed blobs, all other blob hashes/modes preserved. Both changed blobs match local Git hashes. No runtime behavior was changed to bypass the failure.

## 6. Actual evidence and pending checks
Both old runs concluded failure; no APK or report artifacts were produced. Compile stopped before regression tests, lint and assembly. Standard Code Quality Checks and Security Scan jobs passed independently; this does not mean the build passed. Job logs were fetched/read, not inferred from badges. Local source comparison, Git blob hashes/tree preservation and memory/todo<=500 checks passed. No local Kotlin/JDK/Android SDK execution. Existing eight clipboard mock tests, two typed-undo/editor integration cases and two Android View tests remain registered. Instrumentation tests are compile-only in this workflow; native View execution remains pending.

## 7. Branch, PR and fresh runs
Runtime trial/herbert-live-v1=b047d3fcd5e2b566b751fe91a12a757cead94962; draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with failure/repair evidence.
Fresh live https://github.com/jakamilek/CleverKeysPL/actions/runs/38054606810 and standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38054609652 were observed in_progress for the exact repaired head. No completion wait or continued polling.
Producer experiment/herbert-form-diagnostic-v1 at86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / draft PR13 remains unchanged; producer changes in this task are checkpoint documentation only.

## 8. Artifact/model identity
No APK for failed d1ccc7e or repaired b047d3fcd5e2b566b751fe91a12a757cead94962 is verified yet. Previous baseline3f48e456f0d8f411e80be3857f1846e4b2cd139e, live38040432033/artifact11665712630 and CI APK SHA-256 b9c063b3f6bea4c7549f2574e8841f4f0751ea751b291fa920074fafaeeb481f remain historical and do not contain these clipboard/search changes. Original HerBERT model SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged. Existing workflow will stamp both clipboardPasteSuggestion and spaceFreeTypedAutocorrectUndo true in a successfully built artifact.

## 9. Limits and backlog
Phone clipboard and search/URI editors need real verification on Nubia NX721J/Android15. No native View execution or current phone result. EN/PL label supplied; other locales tracked. Dictionary audit and its nine missing swipe words, rare-place usage priors, and BS timing options remain deferred. No renewed AI experiment.

## 10. Next action after user reports completion
Read fresh run conclusions and required job reports; fix further failures before presenting an APK. On success verify exact code commit, identity flags, uploaded artifact association and CI digest. Then test clipboard exact paste/dismiss/session/password guards; search autocorrect followed by immediate BS restores full original without adding a separator, ExactAdd keeps text, subsequent BS deletes normally; normal text-field undo remains intact. Execute Android View tests only with a device.

## 11. Delta and stopping state
Previous milestone implemented the app behavior but CI exposed the omitted import. This checkpoint records confirmed compile failures, the narrow import repair and two new pending runs. Both mains receive only this new document; source/main and historical checkpoints preserved. No completed test result or new APK is asserted. Stop monitoring until the user reports the fresh runs finished.
