# Explicit personal entries — typed prefix recall implemented

## 1. Identity and bases
UTC2026-10-10 / Europe-Warsaw2026-10-10. Runtime trial parent8375724e2527b48b0c7e048d98ff894bb37f46e8; new head53767fdf57684aed459226b824a0885a3e031e6c. Runtime main before docs-only checkpoint4f866a53e0ee721edab49b9d92d4a167b75863a9; producer main38b7788e445a5298cadfed1dad977128ea2c83a3. Identical11-section file on both mains, all prior source/checkpoints retained.

## 2. Architecture
Geometric + original opt-in HerBERT FP32 compact-case-v4/context32/deadline350ms/privacy/single-publish unchanged. Existing clipboard/startup/explicit whole-add preserved. New small personal-entry prefix index belongs to DictionaryManager, derived from active explicit userWords; no new persisted store. Literal completions bypass model/contraction/capitalization paths.

## 3. Accepted task and feedback
Maintainer says prior build works but the main purpose of saving addresses was quick recall from first characters, which did not happen. Implement that missing lookup/display/full-token commit behavior. Continue to dictionary backlog after this app follow-up is verified; do not silently substitute global language-pack repair.

## 4. Exclusions
No model/export/SI corpus, langpack/source dictionary, geometry, BS gesture/settings/default, dependency/version/release/tag/main code merge. No gate weakening or tests removed. No subagents. Only one brief new-run observation; monitoring<=60s/run. No local Kotlin/Android build claim.

## 5. Cause and implementation
ExactAdd persisted complete structured entries but the ordinary frequency/length ranking could bury them, and the prose tracker split identifiers at punctuation/digits; ordinary suggestion taps could replace only the last fragment.
PersonalDictionaryCompletion indexes valid explicit structured entries by first1..3 characters, then filters the literal full prefix using Locale.ROOT. Stored case retained; shorter then spelling deterministic ordering. PersonalDictionaryToken's128UTF16 whole-entry bounds still apply. DictionaryManager invalidates the derived cache in existing mutateUserWords, including add/remove/clear/reload.
SuggestionHandler reads bounded whole before/after token independently of the prose tracker. Up to3 enabled explicit matches lead; letters-only prefixes retain queued ordinary results afterward with aligned scores/metas and dedup. Punctuated/digit prefixes own the literal strip and clear pending prose fragments before completion/learning. Full saved tokens remain literal through their final character. BS and cursor sync refresh this route.
Tap verifies editor/field/token/collapsed absolute caret/current entry/disabled state, selects both token halves and commitText replaces atomically. Failed commit restores caret without pre-deletion. Stored case preserved, trailing space follows existing field/preferences; surrounding text stays. Private/password/selection/Termux suppressed; no absolute caret => ordinary path. No text logging or implicit address learning.

## 6. Validation status
Static review/diff confirms9 files only, ten registered pure tests, eight new real-handler cases and all44 existing cases retained (52 total). Build changes only pure registration; workflow only structuredDictionaryPrefixCompletion identity flag. Todo497 actual lines/498 split entries<=500. Expected registered pure total2906, not executed locally.
Current-head Android compile, pure/mock/original conformance, debug/vital lint, security/quality/size/APK and phone checks PENDING. Environment lacks full Kotlin/Android toolchain; no fabricated test pass.
Prior8375724e2527b48b0c7e048d98ff894bb37f46e8: live38070883727 and CI38070886854 SUCCESS;2896 pure, original2471tokenvectors/232batches/532candidates/fiveinputs conformance; live238/standard315 overlapping integration;44/44 bookkeeping;debug0Error/Fatal235Warning,vital/security/quality/size/APK passed. Maintainer confirms clipboard/idle/full-add on phone; reports missing prefix recall. That old evidence is not validation of the extension.

## 7. Branches, PR and runs
Runtime trial ref advanced CAS8375724e2527b48b0c7e048d98ff894bb37f46e8->53767fdf57684aed459226b824a0885a3e031e6c; exact nine-file compare verified.
Draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with new behavior and pending checks.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38073753788 and CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38073754846 observed IN_PROGRESS at53767fdf57684aed459226b824a0885a3e031e6c, about17s after push. No long polling or cancellation.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60/draftPR13 unchanged. Both mains docs only.

## 8. Artifact/model identity
No verified new extension APK yet. Previous artifact11677595285/run38070883727 APK35823944B SHA256ff3571fc0509f8f35d3ff626d1ff4fd321e5b7efb6b871ac0e8e5ed4d6cee354 lacks prefix recall; do not relabel it as new build.
Future artifact must match53767fdf57684aed459226b824a0885a3e031e6c and structuredDictionaryPrefixCompletion=true plus clipboardLabelAndHoldPanel/startupFrequentWords/explicitStructuredDictionaryAdd.
Original separately imported FP32 model SHA256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged, no reimport needed.

## 9. Limits/backlog
New runtime and device validation pending. Explicit keyboard-managed active-language user entries are indexed; no new Android-provider or cross-language store. Case-insensitive literal matching does not invent diacritic forms. Same-prefix personal entries use deterministic ordering, no usage-frequency calibration. Absolute collapsed editor caret required for guarded atomic replacement.
Polish UI priority retained; no new strings. Other locales, global dictionary missing keys/source priors, native SI performance and stationary BS timing controls remain separate.

## 10. Next after completion
Read exact53767fdf57684aed459226b824a0885a3e031e6c run logs. Check52-case handler, expected2906 pure/original conformance and all remaining gates. Repair failures without reducing coverage. If green, download/re-hash ZIP+APK and verify new identity/no model fixtures. Phone: existing saved address from first letters, dots/@/digits in email/search fields, hyphenated entry, BS/cursor middle replacement, multiple matches with prose options, no text loss, deleted entry disappears. Then return to dictionary work after acceptance.

## 11. Delta
Saving a whole address was implemented and phone accepted, but quick prefix recall was incomplete. This adds derived explicit-entry lookup and guarded literal replacement while retaining ordinary candidates for letter prefixes. New tests/spec/todo/APK identity added; current-head verification pending. No installable new package is claimed.
