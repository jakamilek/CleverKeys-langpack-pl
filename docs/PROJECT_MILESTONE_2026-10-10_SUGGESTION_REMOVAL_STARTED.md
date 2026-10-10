# Suggestion dictionary removal — implementation checkpoint, 2026-10-10

## 1. Identity and bases
Runtime: jakamilek/CleverKeysPL, trial/herbert-live-v1, draft PR4. New code commit a3d4eef7640502fecf5fef1dad6ef8e41f79d1a0;
parent53767fdf57684aed459226b824a0885a3e031e6c. Runtime main documentation base
cfcfbffdb99febc4a48c1bb400cce093532555a4; producer main documentation base
fc7c78e8d8a1974da65dfd9599448684c6cfbd74. Producer experiment remains
86ab57abecebcff3c290fc269fd78ab5e2a7cf60 / experiment/herbert-form-diagnostic-v1 / PR13.
This identical checkpoint is docs-only on both mains; no runtime main code merge.

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
The strip's listener previously called inspectSuggestion and built a provenance sheet.
It now calls offerSuggestionRemoval. Statistics formatting and optional origin markers
remain internal. Popup action requires unchanged bar/generation/index/word,
editor identity/revision, language and privacy; dismissed/stale callbacks cannot mutate.
DictionaryManager reads the fresh custom map: exact-case removal, otherwise one unique
case-insensitive stored spelling; ambiguous cases are rejected. Separately owned case
entries and unrelated frequencies survive. With no owned casing left, lowercase
Locale.ROOT enters disabled_words_<language>, preventing immediate base resurrection.
Removal invalidates structured prefix cache, queued prose/SI/idle work and dynamic serving
state. A confirmation clears the strip. Marker help no longer promises hold-for-statistics.
The prior prefix privacy check now delegates to shared LearningGate, addressing its known
API26 constant lint warning without changing the guard or SDK.

## 6. Actual validation and pending work
Local new-resource XML and bounded source review PASS; no Android/Kotlin execution here.
Eight new real-handler/store mock cases bring LearningFunnelBookkeepingTest52→60:
explicit confirm/text preservation, stale callbacks/privacy/prompts, failed removal,
email cache invalidation, case/diacritics preservation and scoped base exclusion.
One real-View dispatch regression supplements two clipboard cases (compile-only until
device execution). Current-head CI compilation/pure/mock/conformance/lint/APK is pending.
Parent53767fdf live38073753788 and CI38073754846 SUCCESS:2906 pure, mandatory original
2471tokenvectors/232batches/532candidates/fiveinputs conformance;246/323 overlapping
integration tests, never additive. Debug0 Error/Fatal236 Warning; vital/security/quality/
size/assembly/upload passed. Maintainer now confirms personal prefix behavior on phone.
These results and that APK do not validate the new removal commit.

## 7. Branches, PRs and runs
Runtime PR: https://github.com/jakamilek/CleverKeysPL/pull/4
Current CI: https://github.com/jakamilek/CleverKeysPL/actions/runs/38076343391 — in_progress, conclusion pending.
Current Polish SI HerBERT live trial v1: https://github.com/jakamilek/CleverKeysPL/actions/runs/38076340590 — in_progress, conclusion pending.
Producer PR13 unchanged: https://github.com/jakamilek/CleverKeys-langpack-pl/pull/13
Runtime and producer mains receive only this matching documentation file.

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
Prefix recall has moved from pending phone validation to maintainer-confirmed working.
New task replaces strip statistics hold with dictionary action and regression coverage.
Known prefix API constant guard is consolidated. This checkpoint starts the new CI cycle;
no new build/test/device success is claimed before results exist.
