# Clipboard opening words — CI harness repair

## 1. Identity and bases
UTC2026-10-10 (Europe/Warsaw2026-10-10). Runtime main before this docs-only checkpointca235035f76079fe302d4cdf0110554a99b550da; producer main3a6f582030147f40b4e979bfc94454c4c6365cf0. Runtime trial parent35c7ba283770e1f9101450287bcd91a918d415ae; repaired head3ce3b70707dc650727c4abf7d4e49ca2e469e109. All preceding source/checkpoints retained; identical document saved on both mains.

## 2. Architecture
Geometric + original opt-in HerBERT FP32 compact-case-v4/context32/deadline350ms/privacy/editor single-publish architecture unchanged. Clipboard icon/label/tap/hold action is separate from candidates. Opening frequent words use gated personal counts and dictionary fallback; full structured ExactAdd writes existing personal dictionary without editor rewrite.

## 3. Accepted task
User reports run completion. Verify exact-head CI/artifacts, repair actual failures and prepare APK only after all required gates. Maintain requested three app features and previously phone-accepted ordinary-field BS/autocorrect behavior. Actions monitoring<=60s/run; no automatic unrelated SI/dictionary work.

## 4. Exclusions
No production, language-pack/source dictionary, model/ranking/geometry, gesture, settings/default, dependency/version or release changes in repair. No main code merge, tag or test/lint/conformance bypass. No exception swallowing, removal/renaming of regression or fabricated device result. No subagents.

## 5. Failure and repair
Both runs fail only in LearningFunnelBookkeepingTest.aQueuedStartupResultCannotOverwriteFirstTypedWord: java.lang.RuntimeException Stub! at android.os.Trace.beginSection -> WordPredictor.predictInternal -> real typed predictWordsWithContext from the inline executor fixture. The test's startup seam also executes ordinary typing prediction, unintentionally invoking an uninitialized dictionary-backed Android implementation in the JVM mock environment.
Repair3ce3b70 changes exactly2 blobs: test fixture and bounded memory/todo. For prefix g only, provide PredictionResult([grzeje],[200]); keep real handler typing, startup invalidation, queued callback and prefix-result publication. Strengthen assertions from absence of tak to exactly grzeje, exactly one typed-predictor call and editor remaining g. Preserve all44 test cases and source behavior. Git compare verified only these2 files before CAS35c7ba28->3ce3b70.

## 6. Verified parent results
At exact35c7ba28, live38063878832 and standard38063882258 COMPLETED/FAILURE, same one fixture failure independently confirmed in both job logs. Runtime/instrumentation compilation succeeded;2896 registered pure tests and mandatory original conformance2471token vectors/232batches/532candidates/five inputs passed in both runs. Live9 completed integration suites193tests; standard16 completed suites288tests (overlap; never combine). Clipboard controller11 tests passed. LearningFunnelBookkeepingTest44 tests,1 failure; remaining43 ran successfully but the suite is FAILED.
Standard Security Scan and Code Quality Checks succeeded; size skipped. Debug/release vital lint and live APK assembly/audit/upload gates skipped after integration failure. No verified feature APK published. Parent235-warning baseline does not substitute for a new lint result.
Local repair has source assertion and <=500-line todo checks only; no local Kotlin/Android build or JVM test execution. New-head results remain pending.

## 7. Branches, PRs and new runs
Draft runtime PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with actual failed results, exact failure cause and narrow repair.
Fresh live https://github.com/jakamilek/CleverKeysPL/actions/runs/38069889084 and standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38069891533 observed IN_PROGRESS at3ce3b70. Triggered by authorized trial push, not cancelling old completed runs. No long wait/poll loop.
Producer diagnostic branch86ab57abecebcff3c290fc269fd78ab5e2a7cf60 and draftPR13 unchanged; no experimental run.

## 8. Artifact/model identities
Failed live report11675035613,4681B, GitHub ZIP digest sha256:760d3e78618496625739e52b223befd5b8227ca422f936796408f2a9270f6247. This metadata is API/log evidence, not a local download/hash claim. No APK artifact on failed live run.
Original separately imported model SHA-256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged.
Previous accepted APK artifact11670958917 at57c15c38 does not contain clipboard hold/opening words/structured add. Do not offer it as the requested feature build. New identity must match3ce3b70 and include clipboardLabelAndHoldPanel/startupFrequentWords/explicitStructuredDictionaryAdd.

## 9. Limits and backlog
Current-head full tests/lint/APK pending. Android View tests are compiled by live workflow, not executed on a device; actual icon/label/tap/hold/idle/add behavior and native performance remain manual checks. Global personal usage is filtered by active lexicon rather than per-language counts. No new mid-address completion mechanism.
Polish/base labels complete; other locales deferred. Dictionary coverage, source use priors, native RAM/quality and stationary BS timing options remain separate backlog. Prior ordinary-field BS repair is phone accepted.

## 10. Next after completion
Read exact3ce3b70 runs and logs, verify44-case repaired suite,2896 pure/original conformance and remaining gates. Fix any genuine new failure without weakening tests. If green, download/re-hash ZIP+APK, verify commit/feature identity and no FP32 fixture/model packaging, then supply artifact and concise phone tests. Continue respecting<=60s monitoring/run and user completion messages.

## 11. Delta
Three requested app behaviors compiled and pure tests passed, but one newly broadened inline test fixture blocked completion. Repair isolates the unrelated dictionary result while making the lifecycle assertion stronger. Main branches receive docs only; runtime production code and producer remain unchanged. No installable new package is claimed.
