# Animated GIF grid — verified build checkpoint, 2026-10-10

## 1. Identity and bases
Runtime jakamilek/CleverKeysPL, trial/herbert-live-v1 at
ab9ae4321627ba355bdf7b59786b8efe22e95ba2, draft PR4.
Earlier b61afaab dependency-lock and04e683f3 native-test lint failures are repaired.
Runtime main documentation base 0edf096eb6ac2596210509d093758bbf90795010.
Producer main documentation base a94641c8eb8ea63168530dbecf5abe65822cf0db.
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
The integrated panel formerly requested only static first-frame thumbs, although packs
can carry local animated full WebP. Visible tiles now decode/start full files on API28+
with pinned coil-gif2.6.0/ImageDecoderDecoder; missing/empty/unreadable full files and
older Android use the existing static thumbnail. Native full data cannot be manufactured
from static-only packs. Request generations guard late callbacks; detach/recycle/close
cancel requests, stop animation and clear the view.200px FIT bounds both decode dimensions;
animated caching is disabled, existing static32MiB cap remains. Receiver destroys the
grid on back/selection/pane-switch/finish; finite usage write preserves Recently Used.
The initial missing lock row is now pinned and exact real-task graph regeneration passes.
The redundant RequiresApi annotation in the native test is removed; API28 SdkSuppress
and all assertions remain. No global lint suppression/baseline or other dependency bump.

## 6. Actual validation and pending work
Exact ab9ae432: live38081907615/android114300397942 and standard38081910272/
BuildAndTest114300406445 COMPLETED/SUCCESS. Runtime and instrumentation compile passed.
2906 registered pure tests and original2471tokenvectors/232batches/532candidates/fiveinputs
conformance PASS. Live14 mock suites294 tests and standard20 suites355 tests passed
(overlap, not additive); preview9/9 and receiver15/15 including two new close regressions.
Downloaded/rehashed debug lint XML:0Error/Fatal235Warning. Release vital lint passed in
both logs, no invented release-warning count. Real assembleDebug/assembleDebugAndroidTest/
compileReleaseKotlin selective lock regeneration printed exact committed graph PASS and
git diff --exit-code passed. Only pinned new module is added; normal locks retained.
Assembly, ARM64/no-model/no-fixture audit and upload PASS. Standard security114300406374,
quality114300406233 and size114304084775 SUCCESS.
Local artifact/reports hashes, APK sidecar/manifest/code SHA/feature flags and ABI/assets
PASS. Dex contains the Coil animated decoder and production preview controller, not
GifAnimatedPreviewTest. Native test compiled/assembled only, not run. No measured
animation smoothness, native playback/frame changes, memory/battery or phone acceptance.
Prior removal/prefix/clipboard/editor phone acceptance remains; GIF phone test pending.

## 7. Branches, PRs and runs
Runtime PR https://github.com/jakamilek/CleverKeysPL/pull/4
Verified live https://github.com/jakamilek/CleverKeysPL/actions/runs/38081907615 — SUCCESS.
Verified standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38081910272 — SUCCESS.
Failed first live38079913286/standard38079916540 and subsequent live38080721242/
standard38080723467 remain historical cause evidence, not current status.
No new build is launched merely to record these completed results. No waiting loop.
Monitoring<=60seconds TOTAL/run; maintainer reported completion before retrieval.
Producer PR https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13 unchanged.

## 8. Artifact and model identities
Verified live ARM64 artifact11681521627; ZIP35856676B:
SHA256db4b3730e26ec72247dfd420420378e47ffc4019dd0a30746607c3f815529875.
APK35855012B:
SHA2565b2aa1d7526b42272dcf84ea1070e5bfef9ceae74c33ae544308f9521924bcd4.
codeCommitab9ae4321627ba355bdf7b59786b8efe22e95ba2, gifAnimatedLocalPreviews=true,
prior removal/prefix/clipboard/idle/structured-add/BS-undo flags verified.
ZIP checksum matches GitHub digest, APK matches sidecar/manifest bytes/hash. ARM64-only
libraries, no >50MiBONNX/giant asset or tokenizer/score fixture in delivered APK.
Verified reports11681032371/22466B:
SHA256fff0f809c3079caa13289854ea2543c25f4d7e3af39c68d1c85691e5e3feff5f.
Standard apk-debug11681206543 exists but is not used for the live ARM64 delivery.
Original separately imported FP32
SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2.
No reimport; opt-in off/compact-case-v4/context32/default350ms unchanged.

## 9. Limits and backlog
Native GIF playback/scrolling/rendering test execution and process memory/battery impact
remain pending. Decode bound/lifecycle mocks are not performance or frame-output proof.
API24–27 remain static; imported packs need local full animation files. No Internet fallback.
Nine missing Polish swipe keys plus kapitalizacją/kapitalizacje, corpus/source priors,
native SI RAM/quality and BS timing options remain. Other-locale action/help review remains
deferred; no new strings in GIF change. No model/editor-text logging or persistence.

## 10. Next after completion
Deliver the verified matching ARM64 APK as the next phone test build.
Phone: open a full-animation pack and confirm movement; scroll/search/change page,
select/send/check Recently Used; close/reopen the panel and switch apps/panes.
A thumbnail-only pack validly remains static. Native test execution and phone performance
are separate. If phone accepts this behavior, return to deferred global Polish swipe
dictionary coverage/source investigation, without merging code or triggering releases.

## 11. Delta from previous checkpoint
Both complete workflows now succeed on exactab9ae432. Prior missing lock and erroneous
test annotation are resolved without weaker guards; real graph regeneration also PASS.
Matching live APK/reports downloaded/rehashed/audited, decoder/controller present.
Only GIF phone/native rendering/performance acceptance remains for this feature.
Prior trial todo pending-CI notes are superseded by this exact-head verified checkpoint;
no model/default/corpus/version/main code merge or release is implied.
