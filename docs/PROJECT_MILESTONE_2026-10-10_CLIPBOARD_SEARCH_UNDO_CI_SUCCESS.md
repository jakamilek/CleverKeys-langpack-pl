# Clipboard and search autocorrect undo — CI success, phone tests next

## 1. Date and checkpoint bases
UTC2026-10-10. Runtime main before this docs-only checkpoint: fed123eb3fc540b3e24b26a11053411b213b87fd; producer main: c9d7f5ebfe9fd33c1781e6c9de4a24c21667a318. Runtime trial/herbert-live-v1 stays at b047d3fcd5e2b566b751fe91a12a757cead94962; no new trial source commit. All earlier source/docs/checkpoints are preserved.

## 2. Current architecture
Geometric decoding and original opt-in HerBERT FP32 remain unchanged, with bounded decoded forms/case, compact-case-v4 presentation, context32/default deadline350ms and existing privacy/editor/single-publish guards. Clipboard paste is a separate pre-edit action; exact typed-autocorrect undo supports verified space-free search/URI endings independently of automatic-spacing rules.

## 3. Accepted scope
User reported the fresh runs completed. Read actual outcomes, verify the present APK identity and integrity, offer it for phone tests and save the milestone on both mains. App scope remains clipboard suggestion and BS restore after search autocorrection. Polish translation priority, deferred dictionary work and max60s run monitoring remain.

## 4. Rejected/unapproved scope
No tests/gates removed, no source/model/dictionary/ranking/BS gesture/settings/dependency/default change after success, no merge/release/tag/version bump. Agreement-v4 remains rejected; usage priors are unimplemented. No current native phone or linguistic-accuracy success is claimed.

## 5. Implemented behavior and repaired failure
Current clipboard chip reads one plain current clip (1–65536 characters), previews up to64 Unicode code points, pastes the full text directly, avoids word candidate/learning/history/persistence/logging, and dismisses on first edit/cursor change/hidden keyboard/stale editor or tap. Password/private/sensitive guards apply. Search/URI typed-autocorrect bookmarks verify actual corrected word with/without a separator and exact editor/caret/word boundaries; immediate short BS restores whole original and keeps ExactAdd. The previous d1ccc7e compile failure was an omitted InputType import; b047d3fcd5e2b566b751fe91a12a757cead94962 adds it plus a memory failure note, preserving behavior and gates.

## 6. Verified checks and limits
Live38054606810 and standardCI38054609652 both SUCCESS at exact trial head. Android runtime and instrumentation test sources compiled. Each run passed2881 pure tests and mandatory original conformance:2471 tokenizer vectors,232 batches/532 candidates/five inputs. Live11 integration suites passed222 tests, including8 clipboard mocks and31 learning/editor cases with the2 new space-free-undo regressions. Standard18 integration suites passed302 tests; overlapping totals must not be combined. The2 Android SuggestionBar View tests compiled but were not executed on a device.

Debug lint:0 Error/Fatal,235 Warning;234 inherited plus1 new ObsoleteSdkInt for redundant SDK>=24 in clipboard sensitivity handling when minSdk24. This harmless cleanup remains for later; no broad lint suppression or extra rebuild. Release vital lint, assembly, APK no-weights/no-fixtures audit, standard security/code-quality and size jobs passed. Logs were fetched/read. Downloaded report ZIP hash verified; pure count/conformance marker and lint XML severities independently read. No local Kotlin/Android SDK execution claimed; results are CI/JVM evidence.

## 7. Branches, PRs and run links
Runtime trialb047d3fcd5e2b566b751fe91a12a757cead94962 unchanged; draftPR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with successful evidence.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38054606810 ; standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38054609652 .
Previous failed38054047905/38054050655 remains documented. Producer experiment/herbert-form-diagnostic-v1 at86ab57abecebcff3c290fc269fd78ab5e2a7cf60 and draftPR13 unchanged. No completed-run waiting.

## 8. Current artifact and model identities
ARM64 trial artifact11671965482, run38054606810, headb047d3fcd5e2b566b751fe91a12a757cead94962:
https://github.com/jakamilek/CleverKeysPL/actions/runs/38054606810/artifacts/11671965482 .
ZIP35812222B,SHA-256 d161d1bdf39a016b1c331597c8edf6d273f9b9495e249aaf753da7911484f3a8.
Extracted CleverKeys-v2.0.0-arm64-v8a.apk35810798B,SHA-256 bff4b23b05dd26886b04620941daea90deeaf6aa63d8b4358de61b3600f16f50. Both ZIP and APK bytes downloaded/re-hashed locally, matching GitHub digest and CI identity; identity codeCommit equals exact head, clipboardPasteSuggestion=true,spaceFreeTypedAutocorrectUndo=true,liveAI=true,optInDefault=false,liveRevision=compact-case-v4,context32/deadline350. Local APK archive audit finds no model weights/reference fixtures and only arm64 native libs.

Report artifact11672025369: ZIP22473B,SHA-2566dc395adb6b77f69ce86dcab002ee97357002589579c22be6d7b60545bd0016e verified. Older11665712630/3f48e456 is historical. Original separately imported model SHA-256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged; no new import needed.

## 9. Backlog and risk limits
Real phone behavior on NubiaNX721J/Android15 and native Android View execution pending. Clipboard OS permissions and actual search/URI editor space behavior require manual confirmation. Other locales for new clipboard label deferred (EN/PL supplied). Record redundant SDK warning for later cleanup. Dictionary audit still deferred: dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam and prior missing forms. Usage priors and BS timing options deferred.

## 10. Next user tests
Install APK from the current artifact ZIP. Copy multiline/punctuation text, open keyboard before typing, verify Wklej offers and pastes exact full text; typing dismisses it, and password fields do not show it. In search field type a token that triggers autocorrection, tap space and immediately BS: full original returns without adding a space, ExactAdd remains and does not remove editor text, next BS deletes normally. Repeat normal text-field undo with its space and confirm existing BS gestures. Native View tests need a separate device run. Await phone feedback; do not autonomously resume SI/dictionary changes.

## 11. Delta and stopping state
Both fresh builds now pass after the narrow import repair; present APK/report bytes and identities verified. Current runtime source remains b047d3fcd5e2b566b751fe91a12a757cead94962. PR4 and this docs-only checkpoint on both mains record success with phone/Android runtime limits. No source edits or new CI launch after success. Stop at the concrete test APK and manual test guidance.
