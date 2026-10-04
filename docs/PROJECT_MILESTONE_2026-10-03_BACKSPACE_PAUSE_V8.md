# Backspace brake and resume v8 — 2026-10-03

## 1. Device evidence
The maintainer says v7 works well. Supplied playground trace identifies the actual backspace-diagnostic-v7 runtime, acknowledged preview, accepted left/right steps, six-unit selected replacement on release and collapsed empty release without deletion. These tested paths are accepted. The cause of earlier v5/v6 failures remains unproven.

## 2. Revision
Runtime 16cf108ba454441e05ea3877ffe7bf7103b00d9b, parent e787f19d3dac2fc9a6253f6bbc06386579d64f33, branch docs/source-variants-integration-v1, draft PR #1. Marker backspace-pause-v8. Twelve changed files verified after push. No release, tag, merge or version bump.

## 3. Requested behavior
After hold previews a word, dragging left extends selection. A small rightward movement pauses without shrinking it. Further left movement resumes extension; further right movement starts shrinking. Reversal during shrinking also pauses first.

## 4. Motion policy
BackspaceGesture.Drag brakes after 3 physical pixels against the latest directional extreme. Resumption requires 15 pixels from the pause point and a later motion event. Initial activation still requires 15 pixels left. Subthreshold jitter cannot move the pause point. These starting thresholds need phone feel testing.

## 5. Timers
On pause, Pointers cancels the pending repeat. A zero-direction modern tick returns without scheduling another timer or changing selection. A later resume transition makes one immediate step and restarts the existing edge-dependent repeat. The initial word preview remains unchanged.

## 6. Release and guards
Release while paused deletes the current verified selection. Empty release remains non-destructive, cancellation retains its existing checks, and keyboard-wide pointer capture suppresses other keys. Editor guards, character taps, Shift, spacing and unsupported-editor behavior are unchanged.

## 7. Diagnostic scope
Existing bounded, metadata-only playground diagnostics remain; direction zero identifies the pause. Runtime and activity markers use backspace-pause-v8. The uploaded phone log is not copied into repository files.

## 8. Regression coverage
Five new pure tests cover reversal braking, both resume directions, jitter/latest extreme and nonfinite coordinates. Two new pointer/timer tests exercise pending cancellation, delivered paused ticks, resumption and paused release. Existing test names are preserved; lagging-editor integration now verifies unchanged selected text during braking before resumption.

## 9. Build status
V8 debug assembly PASS; **2795 pure + 211 focused mock checks PASS (3006 total)** for code 16cf108ba454441e05ea3877ffe7bf7103b00d9b, [run 37154899155](https://github.com/jakamilek/CleverKeysPL/actions/runs/37154899155). BackspaceHoldTest passed 23 and PointersBackspaceHoldTest passed 11; all seven new brake/resume cases passed. Code Quality PASS.

[Debug APK artifact 11285860899](https://github.com/jakamilek/CleverKeysPL/actions/runs/37154899155/artifacts/11285860899), marker backspace-pause-v8, ZIP 96917932 bytes, expires 2026-10-10T21:29:55Z. GitHub ZIP digest sha256:1528357c38ed936bfcb2eb6f694ff257afa29836ce4001287a612e296f8c4c6f is artifact metadata, not an individual APK hash or a local byte verification.

Full CI remains failure: existing ProduceStateDoesNotAssignValue at popover/SubkeyAssignActivity.kt:148 (1 error, 210 warnings) and four HIGH devalue 5.8.1 findings in site/bun.lock (upstream fix 5.9.3). Release lint and APK Size Analysis skipped; gates remain enabled. V8 phone acceptance and instrumented/minified/performance checks remain pending.

Maximum 60 seconds TOTAL monitoring per build. No local Android toolchain. V7 passed 2999 checks and received maintainer phone acceptance; v8 phone feel testing remains distinct.

## 10. Producer and pack
Producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb unchanged. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. No AI/CTC, dictionary duplicates, manual descriptions or lexical changes.

## 11. Next acceptance
V8 debug assembly/tests passed; install artifact 11285860899 and test left extension, small rightward brake with a stable finger, left resumption, right resumption, another brake while shrinking and release during pause. Confirm the stationary pause keeps exactly the selected range. Instrumented/minified/performance checks and Ale/Lub diagnosis remain open.
