# Animated GIF grid — dependency-lock repair checkpoint, 2026-10-10

## 1. Identity and bases
Runtime jakamilek/CleverKeysPL, trial/herbert-live-v1 at 04e683f35e9cd8fb9fe04eb8d11253c6257b492e, draft PR4.
GIF implementation parent b61afaabff25d269aa2981441530dfcf32cd2790 failed before compilation.
Earlier phone-accepted removal build289b5a48ed3823ab098e729342c17b7006a4a1e9 remains the last verified APK.
Runtime main documentation base 59d91309d6990b0dcab43f87e4d25fef9036b3ba.
Producer main documentation base f83ff00346cef7e35ee284c2e87686a634c9ec50.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / PR13 unchanged.
Both mains receive this identical eleven-section docs-only checkpoint; no main code merge.

## 2. Architecture
GifGridManager owns one pinned Coil image loader and tracks attached RecyclerView holders.
Each GifPreviewLoader owns its local file request, callback generation and drawable lifetime.
CoilGifPreviewRequestLoader is the platform boundary for bounded decode and caching policy.
KeyboardReceiver retains the current grid and destroys it on the shared pane-close path,
including back, selection, pane switching and onFinishInputView. Existing content-pane host,
search routing, pagination and media insertion interfaces remain.

## 3. Accepted task
Maintainer confirms the preceding suggestion-removal build works, then requests moving
GIF previews inside the keyboard. Implement automatic looping of available imported local
animations in visible grid tiles. A static-only pack still needs actual full animation data.

## 4. Scope and exclusions
Runtime trial only: add io.coil-kt:coil-gif:2.6.0 matching existing Coil2.6.0; this necessary
decoder module is part of the newly authorized GIF task. No whole-library/SDK upgrade,
INTERNET permission, remote media fetch, GIF pack/schema regeneration or UI preference.
No corpus/langpack/model/default/version/tag/release/main code merge or producer code.
Editor/prediction/removal/backspace behavior and imported FP32 identity remain untouched.
No new translated strings. Other-locale action/help backlog remains deferred.

## 5. Implementation and cause
Both jobs failed checkDebugAarMetadata: "Resolved 'io.coil-kt:coil-gif:2.6.0' which is not
part of the dependency lock state". The first implementation added a pinned dependency
but omitted gradle.lockfile. This was an implementation/build-configuration omission,
not a queued-run issue. No Kotlin compilation, tests/lint or APK assembly followed it.
The repair adds exactly io.coil-kt:coil-gif:2.6.0 in the five configurations already
used by coil-base/coil2.6.0. Other module versions/configurations stay byte-identical.
The real Coil2.6.0 module source depends on coil-base, core and vectordrawable-animated;
existing locked transitive entries already cover those. Final resolution remains a CI gate.
A live step uses actual assembleDebug/assembleDebugAndroidTest/compileReleaseKotlin
tasks with --update-locks io.coil-kt:coil-gif, retaining other lock constraints, then
requires the regenerated full file to equal committed state. Only the already documented
stdlib-common loss of debugAndroidTestRuntimeClasspath can be restored before exact diff.
Any other graph change fails delivery. Normal locks/security/compile/test/lint/audit remain.
Lockfile-only changes now trigger the live workflow. Pending repair does not imply PASS.
The original animated local-file/lifecycle implementation is unchanged by this repair.

## 6. Actual validation and pending work
Parent b61afaab live38079913286/android114294526261 and standard38079916540/
BuildAndTest114294535028 COMPLETED/FAILURE at checkDebugAarMetadata. The same missing
coil-gif lock coordinate appears in both full logs. Pure/mock/lint/assembly/audit/upload
were skipped; no APK or test success is inferred. Standard security114294535200 and
quality114294535254 succeeded, size job114294777104 skipped.
Local repair review: exactly one pinned lock row; same scopes as coil-base/coil.
Workflow YAML and Python verification snippet parse; memory/todo.md remains499 lines.
Native8x8 two-frame fixture and earlier nine preview/two receiver regressions remain.
Local staging has no Android/Kotlin build toolchain; new-head compile/pure/conformance/
mock/lint/regenerated graph/assembly/audit and phone/native playback results are pending.
Prior verified289b5a48 removal build/phone acceptance remains valid only for that APK.

## 7. Branches, PRs and runs
Runtime PR https://github.com/jakamilek/CleverKeysPL/pull/4
Repaired head 04e683f35e9cd8fb9fe04eb8d11253c6257b492e:
CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38080723467 — initially in_progress
Polish SI HerBERT live trial v1 https://github.com/jakamilek/CleverKeysPL/actions/runs/38080721242 — initially in_progress
Failed parent live https://github.com/jakamilek/CleverKeysPL/actions/runs/38079913286
and standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38079916540 remain historical.
Only an initial new-run lookup is performed; no completion waiting/poll loop.
Monitoring<=60seconds TOTAL/run; maintainer reports completion before result retrieval.
Producer PR https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 unchanged.

## 8. Artifact and model identities
No new GIF APK or artifact hash is verified yet. Manifest adds gifAnimatedLocalPreviews=true.
Prior delivered/phone-accepted artifact11679618773:
ZIP35836672B SHA256bd29b63203b36d6018d0d19a8d1b58d82b5658f3f94e9ab32e68efa467e35288.
APK35835044B SHA2561c9ff8fc2fbcc0dcffc9855f5151bbef2f0a83b67e0c9e133edcf0b0dce739a1.
Reports11679324033/22470B SHA2562f5b42e128fed7ff749a331536753ed37595f75edd1ba5abf5edd115c09acc86.
Original separately imported FP32 SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
No reimport; opt-in off, compact-case-v4/context32/default350ms unchanged.

## 9. Limits and backlog
Android24–27 retain static WebP previews; full files must exist in the imported pack.
Native animated preview behavior, scrolling smoothness, memory/battery impact and actual
instrumented execution remain pending, not inferred from mock lifecycle or decode bounds.
Other21 locales: suggestion_remove_from_dictionary/obsolete advanced_provenance_markers_desc
review; nine missing swipe keys plus kapitalizacją/kapitalizacje, corpus/source priors,
native SI RAM/quality and BS timing options remain. No text logging or network fallback.

## 10. Next after completion
After maintainer reports repaired-run completion, inspect exact-head jobs/logs/reports,
including the new exact dependency-lock regeneration PASS and existing mandatory gates.
Download/re-hash/audit a matching ARM64 live artifact only when required gates succeed.
No failed-parent APK exists and no earlier APK is substituted as the GIF build.
Phone full-animation pack: movement, scroll/search/pages, send/Recently Used, close/reopen/
pane-app switches. Static-only pack fallback and API24–27 static rendering remain valid.
Actual native test execution/performance is separate, then return to Polish swipe coverage.

## 11. Delta from previous checkpoint
Both first GIF runs failed because the new library was absent from gradle.lockfile.
Repair commits one exact module lock row, targeted real-task graph verification, a
lockfile workflow trigger and cause/status documentation. No GIF/editor/SI source change.
Tests/rendering/APK remain pending for the repaired head; both mains receive docs only.
