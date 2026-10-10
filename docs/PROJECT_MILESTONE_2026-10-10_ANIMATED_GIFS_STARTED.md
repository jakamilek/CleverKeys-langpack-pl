# Animated GIF grid — implementation checkpoint, 2026-10-10

## 1. Identity and bases
Runtime jakamilek/CleverKeysPL, trial/herbert-live-v1 at b61afaabff25d269aa2981441530dfcf32cd2790, draft PR4.
Parent 289b5a48ed3823ab098e729342c17b7006a4a1e9 is the verified suggestion-removal build.
Runtime main documentation base ad0bce482c04e8261f14911b770c40bc2fa2a5fb.
Producer main documentation base a577a31abc55ca8b9c360c82d57d798ff795678c.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / draft PR13 unchanged.
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
The old grid requested only gifs/thumbs/{partition}/{id}.webp (a static first frame), while
packs can separately carry animated gifs/full/... and the image loader had no GIF module.
On API28+, ImageDecoderDecoder.Factory now decodes that full local WebP. Older devices,
missing/empty full files or full-decode failure use an existing static thumbnail.
Requests begin only for attached tiles, use a 200px FIT decode bound and disable animated
memory caching; static caching retains the existing32MiB cap. No page-wide animation prefetch.
Detach/recycle/close disposes requests, stops Animatable and clears ImageView. Generations
reject stale success/error after rebind or close. Destroy is idempotent, drops the adapter
and callbacks, cancels grid work and closes Coil. The existing finite selected-GIF usage
write survives immediate pane close so Recently Used does not regress.
No animated playback can be manufactured from a thumbnail-only pack.

## 6. Actual validation and pending work
Local source/API review against official Coil2.6.0 tag completed. Both workflow YAMLs parse;
the test-only8x8 WebP fixture contains two frames; memory/todo.md remains498 lines.
Nine actual preview lifecycle regressions and two receiver close regressions added and
registered in live/standard mock gates. GifAnimatedPreviewTest exercises actual pinned
WebP decode, Animatable start/stop and clearing the ImageView on API28+.
Local staging has no Android/Kotlin build toolchain; these tests are not yet executed here.
New-head runtime/instrumentation compile, pure/tokenizer conformance, mock/lint/assembly/
APK audit and device/native rendering/performance results remain pending.
Prior parent289b5a48: live38077317734/CI38077320840 SUCCESS;2906pure, original2471tokenvectors/
232batches/532candidates/fiveinputs conformance,270/331 overlapping integration tests,
debug0Error/Fatal235Warning. Maintainer now confirms phone behavior works.
Do not apply those prior counts/results to the new GIF commit.

## 7. Branches, PRs and runs
Runtime PR https://github.com/jakamilek/CleverKeysPL/pull/4
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38079913286 — initially in_progress.
Standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38079916540 — initially in_progress.
Both report exact b61afaabff25d269aa2981441530dfcf32cd2790. Monitoring stops after initial lookup,
well below60seconds total per run; maintainer reports completion before results retrieval.
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
After maintainer reports run completion, inspect exact-head job results and reports.
Only if all required gates pass, download/re-hash/audit the matching live ARM64 artifact.
Phone: open a pack containing full animations, check visible movement, scroll/search/change
page, select/send and check Recently Used, close/reopen and switch apps/panes. Static-only
pack fallback remains valid. Actual native test execution/performance is separate.
Then return to the deferred global Polish swipe dictionary coverage task.

## 11. Delta from previous checkpoint
Suggestion-removal phone acceptance is now confirmed. New request changes static thumbnail
rendering into visible local animation with lifecycle cleanup and a matching pinned decoder.
Eleven scoped runtime files changed in one trial commit; native/source/mock tests and specs
are prepared, build/device results pending. Both mains receive only this checkpoint.
