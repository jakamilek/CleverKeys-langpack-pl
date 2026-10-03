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
New BackspaceGestureTest, BackspaceHoldTest, PointersBackspaceHoldTest and capitalization regressions are registered through scripts/gradle-guard.sh. Static review/readback complete. Local Android toolchain is unavailable; v5 compilation, pure/mock execution and device acceptance are PENDING. Actions: https://github.com/jakamilek/CleverKeysPL/actions?query=branch%3Adocs%2Fsource-variants-integration-v1 . No continuous monitoring; stop within 60 seconds and let the maintainer report completion.
Previous code 383137f8a60f372215cb887c57a4c115b46a488f passed debug assembly and 2779 pure + 172 focused mock checks (2951), run 37143960348. This evidence belongs to v4, not v5. Existing SubkeyAssignActivity lint and site/bun.lock devalue HIGH findings remain unmodified; gates stay enabled.

## 10. Producer and pack
CleverKeys-langpack-pl producer code and pack are unchanged (producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb). Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. Geometric decoder retained; no AI/CTC, duplicated dictionary keys or manual definitions added.

## 11. Next acceptance checks
After successful CI, install v5 and test tap after swipe/autocorrection; hold deletion from “olej mleko ” to “olej ”; left/right reversal across other keys and at edges; shrink to zero; touch cancel and field/caret changes; Shift at all positions including word end; punctuation after ordinary words and numbers; cut/paste and dictionary-add integrity. Ale/Lub casing diagnosis remains pending. Phone verification does not follow from mocks.
