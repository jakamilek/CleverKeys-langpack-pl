# Suggestion dictionary removal — verified build checkpoint, 2026-10-10

## 1. Identity and bases

Runtime jakamilek/CleverKeysPL, trial/herbert-live-v1 at289b5a48ed3823ab098e729342c17b7006a4a1e9,
draft PR4. Parent a3d4eef7 failed compile, recorded in prior repair checkpoint.
Runtime main documentation base3be962d7ca0168eac65eeb84a08a5d2444dc1321;
producer main documentation based7268ebc9bbd07eb0afc4db926a8b214e0d9885d.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / PR13 remains unchanged.
Both mains receive this identical docs-only checkpoint. No main code merge/release.

## 2. Architecture
SuggestionBar renders a themed IME PopupWindow without stealing editor focus.
SuggestionHandler validates the explicit removal callback and cancels queued predictions.
DictionaryManager owns fresh custom-store removal and existing active-language disabled
state. Prefix index invalidation and swipe lexicon content fingerprints already follow
those stores. No producer dictionary generation or alternate personal store is added.

## 3. Accepted task
Maintainer confirms prefix recall works and requests removal instead of statistics on
holding a word suggestion. Holding opens an action; tapping that action confirms.
Ordinary candidate tap and holding the Clipboard chip retain their existing behavior.

## 4. Scope and exclusions
Polish/base UI first. No editor text deletion/recommit, corpus/model/default/dependency,
langpack/SDK/version/tag/release or main code merge. Add/undo/preference prompt actions
are not dictionary words. Private/password fields do not offer this dictionary action.
No Android provider rows are deleted; inherited explicit custom/platform overrides of
disabled base words remain. No other-locale edits beyond recording the backlog.

## 5. Implementation and cause

The a3d4eef7 handler called reloadDisabledWords through Predictor, while that method
exists only on WordPredictor. Both runs reported the same unresolved reference at
SuggestionHandler.kt:958; this was an implementation type error, not a runner delay.
Handler now calls only existing coordinator.refreshCustomWords. The interface already
documents reloadCustomAndUserWords as custom/user/disabled refresh; its real implementation
now loads disabled state too. Lazy checkAndReload shares this path without an extra read.
A fresh lifecycle reload also retracts keys absent from the newly loaded custom/user set,
using the same handleIncrementalUpdate removal path as the existing observer: restore a
shadowed base frequency, or remove personal-only keys/prefixes. This closes a stale serving
map gap found while checking removal. Existing custom/platform override semantics remain.
No cast, no new Predictor method, no fake/no-op default and no weaker build gate.
Prior word popup action/editor/language/privacy guards, prefix invalidation, explicit
confirmation and Polish/base resources remain. No new editor text change.

## 6. Actual validation and pending work

Exact repaired code289b5a48: live38077317734 and CI38077320840 COMPLETED/SUCCESS.
Live android114286898055: runtime and instrumentation compile,2906 registered pure tests,
mandatory original2471tokenvectors/232batches/532candidates/fiveinputs conformance passed.
12 live integration suites270 tests passed, including LearningFunnelBookkeepingTest60/60
and WordPredictorDictionaryUpdateTest16/16. CI BuildAndTest114286906745:2906 pure and
18 integration suites331 tests passed. Suites overlap; never add counts across workflows.
Debug lint XML downloaded/rehashed/parsed:0 Error/Fatal,235 Warning (prior236; known
InlinedApi constant guard warning removed). Release vital lint passed in job logs; no
release lint XML included in live reports, so no invented release-warning count.
Security114286906564, quality114286906917 and size114289298022 SUCCESS.
Assembly, ARM64/no-model/no-fixture audit and upload passed. Local ZIP/APK hash,
embedded exact code SHA, feature flags and ABI/asset checks PASS.
Actual View tests compiled only; no instrumented/device execution or phone acceptance
of removal inferred. Earlier prefix recall was maintainer-confirmed working.

## 7. Branches, PRs and runs

Runtime PR https://github.com/jakamilek/CleverKeysPL/pull/4
Verified live https://github.com/jakamilek/CleverKeysPL/actions/runs/38077317734 — SUCCESS.
Verified CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38077320840 — SUCCESS.
Failed prior live38076340590/CI38076343391 remain historical compile evidence, not current.
Producer PR13 unchanged. No new build launched merely to record these results.

## 8. Artifact and model identities

Verified live ARM64 artifact11679618773, ZIP35836672B:
SHA256bd29b63203b36d6018d0d19a8d1b58d82b5658f3f94e9ab32e68efa467e35288.
APK35835044B:
SHA2561c9ff8fc2fbcc0dcffc9855f5151bbef2f0a83b67e0c9e133edcf0b0dce739a1.
Embedded codeCommit289b5a48ed3823ab098e729342c17b7006a4a1e9 and
suggestionHoldDictionaryRemoval=true, personal prefix and prior clipboard/idle/add flags
verified. ZIP checksum matches GitHub artifact digest; APK checksum matches manifest
and hash sidecar. Only ARM64 native libraries; no >50MiBONNX or tokenizer/score fixtures.
Verified reports11679324033,22470B:
SHA2562f5b42e128fed7ff749a331536753ed37595f75edd1ba5abf5edd115c09acc86;
debug lint and real pure-conformance report inspected. Standard artifact11679247068
exists but was not used to deliver the live trial.
Original separately imported FP32 model
SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2
unchanged; no reimport. Opt-in off, context32/default350ms, compact-case-v4 unchanged.

## 9. Limits and backlog
Actual PopupWindow/IME/device execution remains pending. Android system personal entries
retain the preexisting override policy; this feature does not delete data shared with
other apps. Other21 locales need suggestion_remove_from_dictionary and correction of
obsolete advanced_provenance_markers_desc hold text; local MissingTranslation ignore
is confined to the new base resource file. Native SI RAM/quality/source priors, nine
missing swipe keys plus kapitalizacją/kapitalizacje, and BS timing options remain.
Actions monitoring <=60seconds TOTAL per run; user reports completion.

## 10. Next after completion

Deliver the locally verified matching ARM64 APK. Phone: add a temporary email/hyphen
entry and recall by prefix; hold its suggestion to open the removal action; dismiss first,
then confirm removal and check the existing field text stays unchanged and later prefix
recall no longer offers it. Check ordinary tap still inserts and Clipboard hold still opens
its panel. Base exclusions can be restored from Dictionary Manager's Disabled tab.
Phone quality and actual View execution remain separate. After accepted behavior,
return to global Polish swipe dictionary coverage/source evidence; no new CI waiting.

## 11. Delta from previous checkpoint

Repaired code now passes both complete workflows. The interface compile failure is
resolved; all60 handler/store cases and16 real lifecycle cases pass. Matching APK and
reports were downloaded and verified. Debug warnings returned236→235 with no global
lint weakening. Only phone removal/View execution remains pending for this feature.
Prior runtime todo/spec pending-CI notes are superseded by this exact-head checkpoint;
no code/default/model merge or release is implied.

