# Configurable keyboard editing v9 — 2026-10-04

## 1. Accepted baseline
The maintainer accepts the v8 hold/drag/release behavior but reports a narrow stationary pause band and requests slower ordinary selection, a faster long-travel rate and configurable controls. V8 debug assembly and 3006 pure/focused checks passed at 16cf108ba454441e05ea3877ffe7bf7103b00d9b, run 37154899155. Those results do not validate v9. Earlier v5/v6 failure causes remain unproven.

## 2. Revision
Runtime f25d41740fb2e68835ed20a1200c3c0536ca3040, parent c0442972047e1ef1fd691bc13d981577234e5bff, branch docs/source-variants-integration-v1, draft PR #1. Marker editing-settings-v9. All 66 changed files were read back at the pushed commit and matched the prepared contents. No merge, tag, release or version bump.

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
Eighteen typed options use shared product defaults, safe bounded reads and backup validation. Immutable EditBehaviorOptions is captured in ConfigSnapshot at pointer-down. Compose reactive reload, preference notifications, generated search with actual parent mappings, 22 resource sets and scoped reset buttons are wired. Deprecated undo keys are omitted from exports and ignored on import; historical Config symbols/test names are retained for RELEASE_RECORD compatibility. Canonical guide, specs, handbook, TOC and todo are updated on the runtime branch.

## 9. Validation status
Local static checks PASS: XML parse/unique resource names, 22-locale copy coverage and distinctness, literal-percent formatting, 18 runtime-reader/UI-writer links, generated search entries and correct parent sections; obsolete UI state/readers are absent. Twenty-five regression cases were added: nine pure and sixteen focused mock cases. Existing suites remain enabled.

V9 compilation and Kotlin/JVM execution are PENDING in [CI run 37182681723](https://github.com/jakamilek/CleverKeysPL/actions/runs/37182681723); the observed status was in_progress, not a pass. No Android SDK/Gradle/Kotlin compiler is installed locally. CI uses scripts/gradle-guard.sh with the existing memory cap. There is no validated v9 APK yet. A single status check was made within 24 seconds of push; monitoring stopped without waiting for completion.

## 10. Existing blockers and producer
V8 full CI reported the unchanged ProduceStateDoesNotAssignValue lint error at popover/SubkeyAssignActivity.kt:148 and four HIGH devalue 5.8.1 findings in site/bun.lock; upstream fixed version 5.9.3. These are historical baseline observations, not a new v9 result. Gates remain enabled. Instrumented, minified and performance checks remain pending.

Producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb unchanged. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. No AI/CTC, dictionary duplicates, manual descriptions or lexical changes.

## 11. Next acceptance
After the maintainer reports run completion, inspect compilation/tests and the actual APK artifact. Phone-check: the wider pause band, both resume directions, normal versus beyond-half-screen speed, release deletion versus retained selection, short-tap modes and ordinary repeat, independent punctuation/search guards, Shift in/at word end, source case pairs, add-word chip placement and strip reset. Change values, restart and verify persistence; scoped reset must preserve unrelated settings and dictionaries. Do not reuse the old APK as a v9 test.
