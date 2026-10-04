# Configurable keyboard editing v9 — 2026-10-04

## 1. Accepted baseline
The maintainer accepts the v8 hold/drag/release behavior but reports a narrow stationary pause band and requests slower ordinary selection, a faster long-travel rate and configurable controls. V8 debug assembly and 3006 pure/focused checks passed at 16cf108ba454441e05ea3877ffe7bf7103b00d9b, run 37154899155. Those results do not validate v9. Earlier v5/v6 failure causes remain unproven.

## 2. Revision
Runtime f25d41740fb2e68835ed20a1200c3c0536ca3040, parent c0442972047e1ef1fd691bc13d981577234e5bff, branch docs/source-variants-integration-v1, draft PR #1. Marker editing-settings-v9. All 66 changed files were read back at the pushed commit and matched the prepared contents. No merge, tag, release or version bump.

Follow-up 897edfa3e3e9ea28abaf75a32c99417233e6a6d2, parent f25d41740fb2e68835ed20a1200c3c0536ca3040: only the Filipino hold-selection title is shortened from 42 to 38 code points. The label retains the long-press meaning. The one changed file was read back exactly after push. Runtime behavior, test thresholds and the empty translation exception list are unchanged.

## 3. Unified Backspace action
One short-tap dropdown replaces the obsolete swipe/autocorrect checkboxes: character/space deletion (default), undo the preceding autocorrection, or remove the verified last swiped token. Undo requires a collapsed cursor and a complete matching token, is excluded from passwords/technical fields and does not apply to repeats. Autocorrect undo replaces one verified selection in a single commit. Invalid enum values and old true/true preferences do not enable destructive word deletion.

## 4. Motion and speed controls
Defaults are 6 dp braking and 24 dp resumption from the fixed pause reference, with pause enabled. The normal rate is 80% of the prior v8 edge-dependent rate. After travel strictly greater than 50% of screen width, the rate is 200% of that prior rate, including a 15 ms fastest default repeat. Fast and normal values are independently relative to v8. Same-direction resumption retains travel; reversing resets it. Bounds: brake 3–12 dp, resume 12–48 dp, normal 40–150%, fast 100–300%, threshold 30–80%.

## 5. Hold and release controls
Word preview on hold remains enabled independently of Key Repeat. Delete on release defaults on; turning it off leaves the verified selected range for another edit. Turning hold selection off permits ordinary character repeat when Key Repeat is enabled. Whole-keyboard pointer ownership, code-point steps, live connection/selection verification, empty release and cancellation guards remain. Paused gestures have no polling timer. Old vertical sliders are identified as the legacy two-axis fallback.

## 6. Formatting and Shift controls
Existing before/after auto-space settings apply to swipes and selected suggestions. New switches control punctuation attachment and following space independently under Smart Punctuation; search formatting is off by default. Passwords, URI/email and nontext fields remain literal regardless of search opt-in. Numeric-period sentence capitals, Shift editing a returned-to word's first letter and Shift at word end default on. Ordinary Shift after whitespace and explicit editor caps hints remain.

## 7. Suggestion controls and unconditional fixes
Source-backed case variants, add-word chip first and returning the suggestion strip to its start after Backspace default on. Show Exact Typed Word remains the chip's master. Disabling source variants does not alter the one-key dictionary. Dictionary-add remains storage-only; cursor/text revision guards after cut/paste/replacement stay unconditional. No setting permits the former text-deletion regression. Ale/Lub diagnosis remains open.

## 8. Settings infrastructure
Eighteen typed options use shared product defaults, safe bounded reads and backup validation. Immutable EditBehaviorOptions is captured in ConfigSnapshot at pointer-down. Compose reactive reload, preference notifications, generated search with actual parent mappings, 22 resource sets and scoped reset buttons are wired. The maintainer prioritizes Polish UI translation (2026-10-04). Record discovered non-Polish translation defects for later instead of routinely interrupting Polish work. Native-speaker review of the 21 non-Polish locales remains a deferred backlog item; automated resource tests do not establish translation quality. The already-fixed Filipino length assertion is closed, not an outstanding defect. Deprecated undo keys are omitted from exports and ignored on import; historical Config symbols/test names are retained for RELEASE_RECORD compatibility. Canonical guide, specs, handbook, TOC and todo are updated on the runtime branch.

## 9. Validation status
Initial v9 [run 37182681723](https://github.com/jakamilek/CleverKeysPL/actions/runs/37182681723) on f25d41740fb2e68835ed20a1200c3c0536ca3040: debug assembly PASS; pure suite executed 2804 checks, with 2803 passing and one failure. TranslationLengthTest.constrainedStringsDoNotExpandPastTheThresholds rejected fil/edit_backspace_hold_select_title (42 code points versus English 19, limit 2.0 times). Focused mock suites, APK artifact upload and lint were skipped after this failure. Code Quality PASS. The interruption was a translation-length assertion, not a compilation or demonstrated gesture failure.

Follow-up 897edfa3e3e9ea28abaf75a32c99417233e6a6d2 shortens that title to 38 code points. A local Python check of the existing length policy across all 21 translated locales and XML parsing PASS. This does not substitute for the Kotlin/JUnit rerun; no test limit was relaxed and no exception was added.

Follow-up [CI run 37183355586](https://github.com/jakamilek/CleverKeysPL/actions/runs/37183355586) completed on 897edfa3e3e9ea28abaf75a32c99417233e6a6d2: debug assembly PASS, all 2804 pure checks PASS and all 227 focused mock checks PASS (3031 total). Code Quality PASS. The actual apk-debug artifact was uploaded and is not expired: ID 11295888906, ZIP size 97039723 bytes, expires 2026-10-11T06:46:09Z, GitHub metadata ZIP digest sha256:ad6d4aa8522bec864e3c78215e75cacd7ae57e3918f0c4bd2e8e7b2b59874784. This is archive metadata, not a locally verified APK hash or phone acceptance. Download: https://github.com/jakamilek/CleverKeysPL/actions/runs/37183355586/artifacts/11295888906. The standard build/reports/tests upload found no files; test counts are obtained from the JUnit console logs. No new build or monitoring loop was started during completion inspection. No local Android SDK/Gradle/Kotlin compiler; CI keeps scripts/gradle-guard.sh and the existing memory cap.

Initial local checks also passed XML/resource uniqueness, 22-resource-set coverage/distinctness, literal-percent formatting, 18 runtime-reader/UI-writer links and generated search parent sections. Twenty-five regression cases were added (nine pure, sixteen focused mock); all sixteen added focused cases now pass in CI.

## 10. Existing blockers and producer
The first v9 security job reported four HIGH devalue 5.8.1 findings (zero CRITICAL), with fixed version 5.9.3. Follow-up run 37183355586 confirms the same four findings in site/bun.lock. Its debug lint reports one error and 215 warnings; the error is the previously observed ProduceStateDoesNotAssignValue at popover/SubkeyAssignActivity.kt:148. Release lint and APK size analysis were skipped. The full workflow therefore remains FAILED despite passing assembly, pure/focused tests and APK upload. Gates remain enabled. Instrumented, minified and performance checks remain pending.

Producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb unchanged. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. No AI/CTC, dictionary duplicates, manual descriptions or lexical changes.

## 11. Next acceptance
Completion, compilation/tests and APK artifact inspection are done. V9 phone acceptance remains pending. Install the v9 APK from artifact 11295888906, then phone-check: the wider pause band, both resume directions, normal versus beyond-half-screen speed, release deletion versus retained selection, short-tap modes and ordinary repeat, independent punctuation/search guards, Shift in/at word end, source case pairs, add-word chip placement and strip reset. Change values, restart and verify persistence; scoped reset must preserve unrelated settings and dictionaries. Do not reuse the old APK as a v9 test.
