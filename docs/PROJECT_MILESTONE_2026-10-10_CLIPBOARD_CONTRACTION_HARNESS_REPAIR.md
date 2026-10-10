# Clipboard opening words — explicit contraction harness repair

## 1. Identity and bases
UTC2026-10-10. Runtime main before this docs-only checkpoint 29b4c6102a9188c94831c93d8b6b8f0c90e03092; producer main 0aacca6611593bd23341f8a9fdaf1a20f85f1401. Runtime trial parent3ce3b70707dc650727c4abf7d4e49ca2e469e109; new head 8375724e2527b48b0c7e048d98ff894bb37f46e8. Identical document on both mains; all preceding source and checkpoints retained.

## 2. Architecture
Geometric + original opt-in HerBERT FP32 compact-case-v4/context32/deadline350ms/privacy/editor single-publish unchanged. Clipboard icon/label/tap/hold separate from candidates; opening words use gated personal counts and dictionary fallback; structured ExactAdd writes the existing personal dictionary without editor rewrite.

## 3. Accepted task
User reports completion of runs. Verify exact-head failures, repair them and prepare installable feature APK only after required gates. Preserve requested clipboard panel/idle frequent words/complete email or hyphenated entry add and phone-accepted BS/autocorrect. Actions monitoring<=60s/run.

## 4. Exclusions
No production/model/langpack/source dictionary/ranking/geometry/gesture/settings/default/dependency/version change. No merge/release/tag; no regression or lint/security/conformance bypass. No subagents; no fabricated local build or device result.

## 5. Failure and narrow repair
First repair3ce3b70 fixed android.os.Trace Stub! by stubbing the unrelated dictionary predictor for g. It was incomplete: same aQueuedStartupResultCannotOverwriteFirstTypedWord now reaches assertion, expected grzeje but actual empty String. Relaxed MockK nullable getNonPairedMapping returns empty String; actual handler accepts that as a contraction replacement.
Second repair makes existing contraction mock a fixture property and explicitly returns null for getNonPairedMapping(g) and getNonPairedMapping(grzeje), emptyList for getPairedContractions(g) in this test only. Real typing/invalidation/queued publication still run. Exact grzeje, exactly one typed predictor call and editor g assertions unchanged. All44 test names retained.
Git compare confirms exactly2 files: LearningFunnelBookkeepingTest.kt and memory/todo.md (496 lines,497 split entries, <=500). No production change. Trial CAS3ce3b70->8375724e2527b48b0c7e048d98ff894bb37f46e8 succeeded.

## 6. Actual results and pending
Exact3ce3b70 live38069889084/job114264978997 and CI38069891533/job114264986934 COMPLETED/FAILURE independently verified in logs, same44-case suite1 failure. Runtime/instrumentation compilation,2896 pure tests, mandatory original conformance2471token vectors/232batches/532candidates/five inputs passed in both. Live9 completed integration suites193tests; CI16 completed suites288tests (overlapping, not additive). Clipboard controller11 passed. Standard security/code-quality passed; size skipped. Debug/vital lint and APK gates skipped. No verified feature APK.
Local second repair: static diff, unchanged44 names, exact assertions retained, bounded todo checked. No local Kotlin/Android test run: environment lacks complete toolchain. All new-head CI results pending.

## 7. Branches, PR and runs
Runtime draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated with both failures and narrow repair.
New live https://github.com/jakamilek/CleverKeysPL/actions/runs/38070883727 observed IN_PROGRESS; CI https://github.com/jakamilek/CleverKeysPL/actions/runs/38070886854 observed QUEUED, both exact8375724e2527b48b0c7e048d98ff894bb37f46e8. One observation about11s after push; no wait loop or cancellation of completed runs.
Producer experiment86ab57abecebcff3c290fc269fd78ab5e2a7cf60/draftPR13 unchanged. Main checkpoints docs only.

## 8. Artifacts and model identity
Failed live report11676368441,4954B, API digest sha256:580c417b1d5dd2adb1f3dc0934dd37da57c94aaafb54d75a9c81ba7627988e1e; not locally downloaded or rehashed. No APK on failed live run.
Original separately imported FP32 model SHA256 f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged. Earlier accepted baseline57c15c38/APK11670958917 does not contain new features and must not be supplied as their build. New artifact must match current head and flags clipboardLabelAndHoldPanel/startupFrequentWords/explicitStructuredDictionaryAdd.

## 9. Limits and backlog
Instrumented View tests compiled only; native icon/label/tap/hold/idle/structured-add tests pending. Global usage uses primary-language membership filtering, not per-language counters. No new mid-address completion.
Polish/base labels done; other locales deferred. Dictionary coverage including nine reported words, source usage priors, native SI RAM/quality and stationary BS timing controls remain backlog.

## 10. Next after user reports completion
Read exact8375724e runs/logs, check repaired44-case suite and every remaining gate. Fix real failures without weakening tests. If green, download/re-hash ZIP and APK, verify commit/feature identity and no separately imported FP32 model/fixture packaging, then supply APK and concise phone checklist. Monitoring<=60s/run.

## 11. Delta
Unrelated relaxed contraction fixture previously produced an impossible replacement; explicitly model no contraction while retaining stronger lifecycle assertions. Only test/todo changed. PR and both docs-only mains record failure and pending status. No new installable APK claimed.
