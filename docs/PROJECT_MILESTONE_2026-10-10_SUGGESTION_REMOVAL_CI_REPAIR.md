# Suggestion dictionary removal — CI repair checkpoint, 2026-10-10

## 1. Identity and bases

Runtime: jakamilek/CleverKeysPL, trial/herbert-live-v1, draft PR4. Repaired code 289b5a48ed3823ab098e729342c17b7006a4a1e9;
parent a3d4eef7640502fecf5fef1dad6ef8e41f79d1a0. Earlier verified53767fdf57684aed459226b824a0885a3e031e6c.
Runtime main documentation base8faa57dee0ada610833a5f9deca4af3a6ef16af0;
producer main documentation base27ccc4ddf698cc3bb8d333738d765dceff876761.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / PR13 remains unchanged.
Identical docs-only checkpoint on both mains; no main code merge.

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

Failed code a3d4eef7: live38076340590/android114283959348 and
CI38076343391/BuildAndTest114283967781 FAILED at compileDebugKotlin with identical
unresolved reloadDisabledWords. Full tests/lint/APK gates did not execute; no new APK.
CI security114283968024 and quality114283968003 SUCCESS; size114284257480 SKIPPED.
Current repair: bounded local interface/source review PASS, not Android execution.
Three new real WordPredictorDictionaryUpdateTest cases (16 total) invoke through Predictor:
custom removal/base exclusion/re-enable, personal-only serving/prefix retraction and
retained provider ownership override. Live workflow explicitly adds this registered suite.
All60 LearningFunnelBookkeepingTest cases and prior View/clipboard/prefix/BS/conformance
gates remain; only its concrete reload mock/verification is removed because the handler
no longer calls that method. Current-head compile/test/lint/APK and phone checks pending.
Earlier verified53767fdf live38073753788/CI38073754846 SUCCESS:2906 pure and original
2471tokenvectors/232batches/532candidates/fiveinputs conformance;246/323 overlapping
integration tests. Debug0error/fatal236warnings/vital/security/quality/size/APK passed.
Maintainer confirms earlier prefix recall works. Earlier success is not repair validation.

## 7. Branches, PRs and runs

Runtime PR https://github.com/jakamilek/CleverKeysPL/pull/4
CI: https://github.com/jakamilek/CleverKeysPL/actions/runs/38077320840 — in_progress, conclusion pending.
Polish SI HerBERT live trial v1: https://github.com/jakamilek/CleverKeysPL/actions/runs/38077317734 — in_progress, conclusion pending.
Failed prior live https://github.com/jakamilek/CleverKeysPL/actions/runs/38076340590
Failed prior CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38076343391
Producer PR13 unchanged. Both mains receive only this matching checkpoint.

## 8. Artifact and model identities
No current-head APK is verified yet. Previous verified ARM64 artifact11678128425,
35833244B APK SHA256752faacfa02d4dfb0aaa2db8713f4b4227585d0ec64753b7eaedda5b75e67cee.
Previous ZIP35834829B SHA256f1bc004b753c52b7b0dc19dd77df9fbf1d6be4c01759d7fe1b66602c98585d4b.
Its embedded prefix/clipboard/idle/full-add flags and ARM64/no-weight/no-fixture packaging
were locally checked. New workflow adds suggestionHoldDictionaryRemoval=true.
Original FP32 model SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2
is unchanged and separately imported; no model reimport.

## 9. Limits and backlog
Actual PopupWindow/IME/device execution remains pending. Android system personal entries
retain the preexisting override policy; this feature does not delete data shared with
other apps. Other21 locales need suggestion_remove_from_dictionary and correction of
obsolete advanced_provenance_markers_desc hold text; local MissingTranslation ignore
is confined to the new base resource file. Native SI RAM/quality/source priors, nine
missing swipe keys plus kapitalizacją/kapitalizacje, and BS timing options remain.
Actions monitoring <=60seconds TOTAL per run; user reports completion.

## 10. Next after completion
Read exact-head statuses/logs, verify all required compile/pure/conformance/mock/lint/
security/quality/size/assembly gates, then download and verify artifact SHA/embedded
code SHA and new identity flag before presenting APK. Phone: hold versus tap/cancel,
confirm without field edits, removed email prefix disappearance, subsequent typing/swipe,
base Disabled-tab restore and unchanged Clipboard hold. View execution is separate.
Repair actual failures without weakening gates. No automatic release/merge.

## 11. Delta from previous checkpoint

The maintainer reported run completion. Both runs actually failed the same interface
compilation, so no APK is delivered. This repair honors the existing refresh contract,
reuses real removal bookkeeping, adds three real lifecycle regressions and runs their
suite in live CI. Repaired-head automated and phone gates remain pending. No completed
new build/test success or native/device quality is inferred; monitor <=60seconds/run.

