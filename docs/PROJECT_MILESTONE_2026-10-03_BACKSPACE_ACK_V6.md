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
V6 debug assembly PASS; **2790 pure + 202 focused mock checks PASS (2992 total)** for code 10fbf4eef0054a6ac33132633d104010d89f65e1, [run 37150909557](https://github.com/jakamilek/CleverKeysPL/actions/runs/37150909557). BackspaceHoldTest passed all 19 checks, including seven new editor-lag regressions; PointersBackspaceHoldTest passed 6. Existing editor/import/casing/spacing suites and Code Quality passed.

[Debug APK artifact 11284341482](https://github.com/jakamilek/CleverKeysPL/actions/runs/37150909557/artifacts/11284341482), marker backspace-gesture-v6, ZIP 96906096 bytes, expires 2026-10-10T20:26:20Z. GitHub ZIP digest sha256:4ec0ccaccd474e208567192f0d7f91d87f6524a2643268af59bfc364dc66f547 is artifact metadata, not an individual APK hash or local byte verification.

Full CI remains failure: existing ProduceStateDoesNotAssignValue at popover/SubkeyAssignActivity.kt:148 (1 error, 210 warnings) and four HIGH devalue 5.8.1 findings in site/bun.lock (upstream fix 5.9.3). Release lint and APK Size Analysis skipped. Gates remain enabled. V6 phone acceptance, instrumented/minified/performance checks remain pending; mock success does not establish that the phone issue is fixed.

Previous v5: 2985 passing checks in run 37148132597; v5 phone hold/drag/release failed. That artifact is superseded for this test by the v6 artifact above.

## 10. Producer and pack
CleverKeys-langpack-pl code and pack are unchanged. Producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. No AI/CTC or lexical metadata changes.

## 11. Next acceptance
With v6 debug assembly/tests passed, install artifact 11284341482 and retest hold-only release; left extension over other keys; right reversal in the left half; shrink to zero; release; cancellation; editor/caret switching. Capitalization and tap deletion are already accepted on v5. V6 phone verification, instrumented checks and performance remain pending. Ale/Lub diagnosis remains pending.
