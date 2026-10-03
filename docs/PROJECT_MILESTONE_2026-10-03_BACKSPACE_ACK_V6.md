# Backspace acknowledgement follow-up v6 — 2026-10-03

## 1. Phone evidence
V5 tap deletion works; sentence capitalization and Shift at word end work. Holding selects the preceding word, but drag does not extend selection and release does not delete it; another Backspace tap is required. Hold/drag/release acceptance has failed.

## 2. Revision
Runtime commit 10fbf4eef0054a6ac33132633d104010d89f65e1, parent 375608ffc34d9d9d3e8cfd8cce4c9a6eb9b33d5b, trial branch docs/source-variants-integration-v1, PR #1. Marker backspace-gesture-v6. Seven changed files verified after push. No merge, tag, release or version bump.

## 3. Identified code gap
V5 discarded the hold session on the first mismatching selection read. A lagging extraction could therefore block both later movement and deletion, even after the visible selection caught up. Synchronous fixture reads did not cover this sequence. This is a demonstrated code path; without a phone trace it is not proof of the sole device cause.

## 4. Session activation
The session is installed before setSelection so synchronous callbacks can be recorded. Failed composition finishing or selection setup still cannot arm a word deletion.

## 5. Editor acknowledgements
Full selection_updated callbacks carry absolute positions. They can supplement a missing extraction, the original caret or one of the last eight requested ranges. Unexpected live positions continue to block editing.

## 6. Gesture continuity
A temporary mismatch or read error no longer clears the physical hold. Pointer timers retry using the same session. Left extension, right shrinking, whole-keyboard capture, edge speeds and release behavior retain the v5 contract.

## 7. Deletion checks
Connection/editor identity, exact live selected text and confirmed positions still guard deletion. Callback-only evidence never skips the text check. Empty selection and cancellation remain non-destructive. No unchecked DEL fallback is added.

## 8. Regression coverage
Seven new BackspaceHoldTest cases model lag/recovery, acknowledged release, extension/reversal, unrelated positions, changed text, synchronous acknowledgement and real Pointers-to-handler routing. Existing tests remain. No local Android toolchain is available.

## 9. CI evidence
V6 compilation and test execution are PENDING. The preceding v5 code 4ed1706ef37c715170e2585abee9f5dbf7493dbc passed debug assembly and 2790 pure + 195 focused mock checks (2985) in run 37148132597. That run's artifact 11282318484 is v5, not v6. Existing SubkeyAssignActivity lint and four HIGH site devalue findings remain; gates stay enabled. No continuous Actions monitoring beyond 60 seconds.

## 10. Producer and pack
CleverKeys-langpack-pl code and pack are unchanged. Producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. No AI/CTC or lexical metadata changes.

## 11. Next acceptance
After the v6 build/tests finish, install its new debug artifact and retest hold-only release; left extension over other keys; right reversal in the left half; shrink to zero; release; cancellation; editor/caret switching. Capitalization and tap deletion are already accepted on v5. V6 phone verification, instrumented checks and performance remain pending. Ale/Lub diagnosis remains pending.
