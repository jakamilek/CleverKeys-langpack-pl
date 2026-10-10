# Animated GIF grid — native-test lint repair checkpoint, 2026-10-10

## 1. Identity and bases
Runtime jakamilek/CleverKeysPL, trial/herbert-live-v1 at ab9ae4321627ba355bdf7b59786b8efe22e95ba2, draft PR4.
Parent04e683f35e9cd8fb9fe04eb8d11253c6257b492e passes compile/pure/mock, fails debug lint.
GIF implementation b61afaab and its earlier missing-lock failure remain historical.
Last delivered phone-accepted APK code289b5a48ed3823ab098e729342c17b7006a4a1e9.
Runtime main documentation base ccbee850e41b0e04f67a367b09de9fd964a43e86.
Producer main documentation base 2ea3718d37c48a4b945feaa295c48aeb6989693a.
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
Both parent04e683f3 runs reached debug lint and reported UseSdkSuppress at
GifAnimatedPreviewTest.kt:24: tests must use SdkSuppress rather than RequiresApi.
The new test redundantly had both annotations. Repair removes only the RequiresApi
import and annotation; SdkSuppress(minSdkVersion=28), the two-frame test fixture and
all native decode/start-stop/clear assertions remain. No suppress-lint/baseline/global
lint changes and no runtime/decoder/controller/editor/model/config/dependency changes.
The prior missing dependency lock is fixed sufficiently for ordinary compilation;
the separate real-task targeted regeneration/exact-graph gate remains pending, because
lint stopped the preceding live run before that step. Do not claim its PASS yet.

## 6. Actual validation and pending work
Parent04e683f3 live38080721242/android114296895488: runtime/instrumentation compiled;
2906 pure tests and original2471tokenvectors/232batches/532candidates/fiveinputs conformance
passed;14 mock suites294 tests passed, including GifPreviewLoaderTest9/9 and
KeyboardReceiverPaneHostTest15/15 (two new close cases included).
Standard38080723467/BuildAndTest114296901781: build,2906pure and20mock suites355 passed.
Workflows overlap, counts are not additive. Both debug lint runs failed1Error/235Warnings:
only the erroneous RequiresApi annotation in the new native test is reported as error.
Live release vital lint/assembly/targeted lock regeneration/APK audit/upload skipped.
Standard security114296901741 and quality114296901591 SUCCESS; size114299494677 skipped.
Standard artifact11680547029/apk-debug97571985B exists from its pre-lint build, but is
unverified and is not delivered as a passing GIF APK. Live reports11680402427/22694B
digest07e348e0f48765fa43f99267b07319cf8c4a319e3fb880687c5633d67d87be1e observed.
Local repair review retains API28 test eligibility and all assertions; todo499 lines.
Actual native rendering test compiled only, not executed; mock lifecycle PASS is separate.
New-head compile/pure/mock/lint/lock-regeneration/assembly/audit and phone remain pending.
The earlier "not yet executed" todo creation note is superseded for mocks by these results;
native execution remains pending. Prior phone-accepted APK identity remains unchanged.

## 7. Branches, PRs and runs
Runtime PR https://github.com/jakamilek/CleverKeysPL/pull/4
New head ab9ae4321627ba355bdf7b59786b8efe22e95ba2:
CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38081910272 — initially in_progress
Polish SI HerBERT live trial v1 https://github.com/jakamilek/CleverKeysPL/actions/runs/38081907615 — initially in_progress
Failed parent live https://github.com/jakamilek/CleverKeysPL/actions/runs/38080721242
and standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38080723467 remain
completed failure evidence; successful compile/mocks do not mean overall success.
Only initial new-run lookup, no completion waiting/poll loop;<=60seconds TOTAL/run.
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
After maintainer reports new-run completion, inspect exact-head lint and all required
gates, including targeted dependency lock regeneration. Verify matching live ARM64
artifact digest/manifest/code/flags/ABI/asset limits only if all required gates pass.
Do not substitute the failed-parent standard apk-debug artifact or previous phone APK.
Phone full-animation pack: movement/scroll/search/pages/send/Recently Used/close/reopen/
pane-app switches; static-only fallback and API24–27 static rendering remain valid.
Native rendering/performance is separate, then deferred global Polish swipe coverage.

## 11. Delta from previous checkpoint
Dependency resolution now permits runtime/instrumentation compilation. Nine tile and
fifteen receiver tests, prior editor/SI mocks and original conformance passed on04e683f3.
Both runs stopped at a test-annotation lint error; it is repaired without weakening lint.
New-head results/lock regeneration/audited GIF APK/native device acceptance remain pending.
Exactly one test file loses two lines; todo/spec document the cause. Both mains docs only.
