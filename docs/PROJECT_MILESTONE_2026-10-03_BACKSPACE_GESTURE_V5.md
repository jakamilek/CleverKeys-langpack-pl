# Backspace gesture v5 — 2026-10-03

## 1. Maintainer feedback
Editor-sync-v4 works OK on the phone. Sentence capitals are still occasionally missing after periods. The latest Backspace request supersedes tap undo and hold-first-word-then-character-repeat behavior.

## 2. Runtime revision
Trial branch docs/source-variants-integration-v1, PR #1; commit 4ed1706ef37c715170e2585abee9f5dbf7493dbc, parent 51a8e0204a64163fb965ec04de49ce244b1e0310. Marker backspace-gesture-v5. All 25 changed files were read back and verified. No merge, tag, release or version bump.

## 3. Short Backspace
A tap follows the ordinary DEL path for a single character/space, including after swipe/autocorrection. Legacy undo interceptors no longer consume it. Deletion clears stale undo state and returns the suggestion strip to its beginning.

## 4. Word hold
In a supported ordinary text editor, hold previews the preceding word, including trailing spaces. Release deletes the preview; the separator preceding the word remains. This release timing allows a hold to become a drag without earlier destructive deletion. Holding alone does not repeatedly delete more words.

## 5. Drag selection
After hold, leftward motion extends selection and rightward motion shrinks it, including a reversal in the left half. The original pointer consumes motion across the keyboard and suppresses new key presses. Full keyboard edge distance controls 30–200 ms repeat intervals. Selection never grows to the right of its initial caret; an empty selection on release deletes nothing.

## 6. Editor integrity
The session verifies connection, editor info, absolute selection and selected text before deletion. It reads at most 4096 UTF-16 units; truncated whole-word previews are skipped. A refused composition finish does not arm a replacement. Cancellation restores a still-valid caret. Passwords, terminals, inline panes and editors lacking usable selection APIs retain the existing fallback.

## 7. Capitalization
Tap and swipe share the live capitalization decision. If editor caps are zero or fail, prose punctuation can use Android TextUtils sentence rules; numeric boundary handling remains. Search/private formatting exclusions and abbreviation handling are retained. This addresses a possible cause; the occasional phone symptom has not yet been proven resolved.

## 8. Shift word end
Explicitly returning the caret immediately after a word now permits toggling its first letter, as at its start/interior. Ordinary typing acknowledgements still do not arm an edit. Updated pure/editor tests cover every position.

## 9. Validation state
Debug assembly PASS; **2790 pure + 195 focused mock tests PASS (2985 total)** for code 4ed1706ef37c715170e2585abee9f5dbf7493dbc, [CI 37148132597](https://github.com/jakamilek/CleverKeysPL/actions/runs/37148132597). Includes BackspaceHoldTest 12, PointersBackspaceHoldTest 6, SwipeAutocapCommitTest 16, AutocapitalisationTest 18 and all existing editor/import/casing/spacing suites. Code Quality PASS.

[Debug APK artifact 11282318484](https://github.com/jakamilek/CleverKeysPL/actions/runs/37148132597/artifacts/11282318484), marker backspace-gesture-v5, ZIP 96899904 bytes, expires 2026-10-10T19:41:56Z. GitHub artifact digest sha256:0893c511c01c6255961f188247a89853e60feaad07b939e6895ed30c7d41f08c is metadata for the ZIP, not an individual APK hash or local byte verification.

Whole CI remains failure: existing ProduceStateDoesNotAssignValue at popover/SubkeyAssignActivity.kt:148 (1 error, 210 warnings) and four HIGH devalue 5.8.1 findings in site/bun.lock (fixed upstream in 5.9.3). Release lint and APK Size Analysis skipped. Gates remain enabled. Instrumented, minified release, performance and phone acceptance of v5 remain pending. Local Android toolchain is unavailable; these executed results come from Actions. No continuous monitoring.

Previous v4 evidence remains 2951 passed checks in run 37143960348; it is distinct from the v5 result above.

## 10. Producer and pack
CleverKeys-langpack-pl producer code and pack are unchanged (producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb). Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. Geometric decoder retained; no AI/CTC, duplicated dictionary keys or manual definitions added.

## 11. Next acceptance checks
With debug assembly and test suites passing, install the v5 debug artifact and test tap after swipe/autocorrection; hold deletion from “olej mleko ” to “olej ”; left/right reversal across other keys and at edges; shrink to zero; touch cancel and field/caret changes; Shift at all positions including word end; punctuation after ordinary words and numbers; cut/paste and dictionary-add integrity. Ale/Lub casing diagnosis remains pending. Phone verification does not follow from mocks.
