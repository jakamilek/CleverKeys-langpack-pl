# Backspace phone diagnostics v7 — 2026-10-03

## 1. Phone evidence
The maintainer reports the same failure after v6: holding Backspace previews the preceding word, motion left/right does not extend/shrink it, and release leaves it selected until another Backspace tap. V5/v6 hold acceptance FAILED. Accepted tap deletion, sentence capitals, Shift at word end and earlier editor integrity are preserved.

## 2. Revision
Runtime commit 79021046324d8e5eb32023b9fd6fcd710e65b663, parent ea583e1cdb3f8f9f53c854365917a4e2092fb830, branch docs/source-variants-integration-v1, draft PR #1. Marker backspace-diagnostic-v7. Eleven changed files read back against the pushed commit. No merge, tag, release or version bump.

## 3. Cause status
The phone cause is not established. V6 modeled lagging editor reads and passed host checks but did not solve the device symptom. V7 does not assume missing touch events, lifecycle cancellation or a specific validation mismatch; it captures evidence to distinguish them.

## 4. Pointer diagnostics
Trace hold entry and ownership, first captured move, direction reversal, timer step acceptance, release, missing pointer and cancellation/clear. Moves still use the existing keyboard-wide capture and edge-speed policy. No deletion behavior is changed.

## 5. Editor diagnostics
Trace session setup, acknowledgement ranges, editor/connection identity rejection, extracted-selection rejection, selected-text length mismatch, release validation and commitText's boolean return. A successful return is an API acknowledgement, not proof of the on-phone result. All live-text safety checks remain.

## 6. Runtime and lifecycle
The active service reports the runtime/package marker when playground debug is enabled, also after log clearing. Service start/finish and view reset/touch cancel are visible, enabling detection of sessions abandoned before release.

## 7. Logging scope
New diagnostics contain offsets, counts, flags, enum/integer key kind, handler identity and exception class; never editor text or exception messages. They use existing package-bound playground broadcasts, not persistent logs or network. Repeated pointer/editor progress is capped at 24 entries per session; terminal outcomes are retained. Sink exceptions are isolated.

## 8. Regression coverage
Seven new focused cases cover release rejection reasons, position versus text mismatch, text exclusion, bounded output retaining the release result, hold/move/reversal/release stages, cancellation and sink failures. Existing test methods are preserved. No local Android SDK/Gradle/Kotlinc is available; scripts/gradle-guard.sh CI remains the build/test environment.

## 9. CI status
V7 debug assembly PASS; **2790 pure + 209 focused mock checks PASS (2999 total)** for code 79021046324d8e5eb32023b9fd6fcd710e65b663, [run 37153176431](https://github.com/jakamilek/CleverKeysPL/actions/runs/37153176431). BackspaceHoldTest passed 23 and PointersBackspaceHoldTest passed 9, including the seven diagnostic regressions. Code Quality PASS.

[Debug APK artifact 11284274382](https://github.com/jakamilek/CleverKeysPL/actions/runs/37153176431/artifacts/11284274382), marker backspace-diagnostic-v7, ZIP 96918725 bytes, expires 2026-10-10T21:04:44Z. GitHub ZIP digest sha256:c21284003fefae13b05ca1c64e164ea1917d1636c53be159d73bbe75af14cd4f is artifact metadata, not an individual APK hash or a local byte verification.

Full CI remains failure: existing ProduceStateDoesNotAssignValue at popover/SubkeyAssignActivity.kt:148 (1 error, 210 warnings) and four HIGH devalue 5.8.1 findings in site/bun.lock (upstream fix 5.9.3). Release lint and APK Size Analysis skipped. Gates remain enabled. V7 phone trace/acceptance, instrumented/minified/performance checks remain pending; diagnostics are not a phone fix.

Prior v6 passed 2992 checks but failed phone hold acceptance. Actions monitoring is limited to 60 seconds TOTAL per build, then the maintainer reports completion.

## 10. Producer and pack
Producer code 75a06570cc9eaac72f1e7c4376a4efd068be73fb and language pack are unchanged. Pack SHA-256 4c5c82c2ede9e9085bc8773ce3f3b8be53ba210a6f9e9b19b297127e90c7eec7; CKDT 087f99e39ccc9108d7bf5315c902ec5f6899620925e481cfb872d95e8df68e20. No AI/CTC, dictionary duplicates, manual descriptions or lexical changes.

## 11. Next evidence
V7 debug build/tests passed; install artifact 11284274382, enable playground debug and clear the log. Type olej mleko; hold Backspace then release. Repeat with a leftward drag, rightward reversal and release. Copy the complete log including BACKSPACE RUNTIME. Use that trace to choose the behavior fix. Device acceptance, instrumented/minified/performance checks and Ale/Lub source diagnosis remain open. Upstream issues checked read-only: #189 concerns center-less subkeys; #188 concerns Compose, neither establishes this phone cause.
