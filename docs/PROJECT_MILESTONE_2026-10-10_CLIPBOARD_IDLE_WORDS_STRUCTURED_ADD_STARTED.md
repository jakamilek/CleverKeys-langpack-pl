# Clipboard panel, idle words and structured dictionary entries — trial prepared

## 1. Identity and bases
UTC2026-10-10. Runtime main base7e63b7c38ffe3b03031bdb33694e8136956c836f; producer main baseec8f484a75f0d96a2870e68ba2a649dd6dc3fc42. Runtime trial parent57c15c38389418a01801502a9ae8b3b92eccf7e3; new head35c7ba283770e1f9101450287bcd91a918d415ae, tree2ffdf3c8fa735ed0707864f46dfeefdaefaf0799. This identical checkpoint is docs-only on both mains. Existing source/checkpoints remain preserved.

## 2. Architecture
Geometric decoder and original opt-in HerBERT FP32 live compact-case-v4 remain:32-word context,350ms deadline, separate imported model/tokenizer/scorer and single-publish editor/privacy guards. Clipboard is a separate strip action; opening words query the existing predictor/personal statistics off UI; explicit structured ExactAdd writes the existing DictionaryManager store.

## 3. Accepted task
Maintainer confirms prior ordinary-field typed BS/autocorrect repair works. Requested paste icon + “Schowek” label, tap to paste and hold to open keyboard clipboard panel; frequently used opening words; full explicit personal entries such as przykład.ten@gmail.com and czarno-biały. Current priority app behavior, not dictionary/SI investigation.

## 4. Excluded approaches
No hand-authored frequent-word list, email fragment add, implicit non-prose learning expansion, decoder/model clipboard input or delete/recommit on ExactAdd. No source-data/producer/langpack/model/geometry/case/form-ranking/BS-gesture/settings/default/dependency/version changes, main code merge, release/tag or gate bypass. Gemini/PAL requirement remains waived. No subagents used.

## 5. Implementation
22 selected blobs changed on runtime trial; recursive Git tree verified exactly that set before CAS ref update from57c15c38.
Clipboard chip uses vector paste icon, localized label/accessibility description, stale-view tap/hold guards; controller openPanel revalidates active editor/plain clip, disarms paste, opens existing receiver SWITCH_CLIPBOARD.
StartupWordPolicy bounds list to3(default), personal actual usage counts first, lexical frequency filling remaining slots. Primary/user lexicon membership, disabled-word/letters-only filters and personal read master/personal/field gates apply; user synthetic insertion frequencies excluded from fallback. Usage store is process-wide, not per-language. Handler main/background tickets and exact editor identity prevent late publishes; initial cursor park and dictionary-ready callback refresh only an idle session. First mutation/caret movement/settings/exit disarm it; selection uses existing NEXT_WORD append/capitalization.
PersonalDictionaryToken proves full whitespace-delimited token ends from bounded reads (maximum128UTF-16 units), supports middle caret and one trailing completion space. Internal punctuation/hyphen entries get whole ExactAdd; unfinished punctuation endings/controls/selection/truncation rejected. Ordinary words/apostrophe contractions keep current path. Structured offer revalidates exact token/editor and available absolute caret; add preserves all editor text/separator. Known/disabled entries suppressed. Typed/BS/cursor-sync decoration leaves existing learning and autocorrect dispatch intact.
Polish/base resources, canonical input-behavior spec, localization backlog and <=500-line todo updated. Three new APK identity flags distinguish this trial.

## 6. Actual checks and pending checks
Locally resource XML and workflow YAML parse; pure test registration and selected-file/source-diff checks pass. Added15 registered pure policy/token cases,3 controller hold cases and10 actual-handler/backend regressions: full email/hyphen add with retained space/text, cursor acknowledgement, stale editor/text, known word, initial idle/append, queued typing/new editor, private/password and master/personal read gates. Existing View cases now cover icon/label/tap/hold; they are not executed on a device here.
Local JDK17 exists but workspace is partial, without complete Android/Gradle/Kotlin toolchain; no local Kotlin compilation/test execution claimed. Current-head compile/pure/mock/original conformance/debug+vital lint/APK and phone behavior are pending CI.
Parent57c15c38: live38057510660 and standard38057513808 SUCCESS;2881 pure,2471token vectors/232batches/532candidates/five-input original conformance. Live225/standard305 overlapping integration, LearningFunnelBookkeeping34cases;debug0Error/Fatal235Warning, vital/assembly/security/quality/size/APK passed. Parent ordinary-field phone check now accepted. Counts do not transfer to new head.

## 7. Branches, PRs and runs
Runtime draft PR4 https://github.com/jakamilek/CleverKeysPL/pull/4 updated to final combined app scope and pending validation.
Live https://github.com/jakamilek/CleverKeysPL/actions/runs/38063878832 and standard https://github.com/jakamilek/CleverKeysPL/actions/runs/38063882258 observed IN_PROGRESS at exact35c7ba28. No cancellation/restart or blocking wait. Monitoring remains<=60s total/run; maintainer reports completion.
Producer diagnostic PR13/experiment-herbert-form-diagnostic-v1 at86ab57abecebcff3c290fc269fd78ab5e2a7cf60 unchanged; no experiment run dispatched.

## 8. Artifact and model identity
No new APK available/verified yet. Workflow will emit clipboardLabelAndHoldPanel=true, startupFrequentWords=true, explicitStructuredDictionaryAdd=true alongside existing liveAI/optInDefault=false/compact-case-v4/context32/deadline350 identity.
Prior accepted artifact11670958917/run38057510660 contains parent APK only, not this feature set. APK35810906B SHA-256d886cf5f98b8b5cb956c67c82de34972e3776def7f4fed7695229575bf548bef; ZIP35812330B SHA-25610a52a61477f9c274d3effcfbf3d5c1f18113025365df83a4f38cfacae6bba10 verified.
Original separately imported FP32 model SHA-256f851436ba9ca35d0c7313ff873cd869b744b295a8a16fc95b4571d5e11b299f2 unchanged.

## 9. Limits and backlog
Opening words require word prediction and an eligible word boundary; static fallback works with learning off/private flag but clipboard private/password/sensitive suppression remains. Usage counters are global with active-lexicon filtering. No new structured mid-address completion/swipe mechanism; this task fixes explicit whole add.
Instrumented UI execution, phone label/hold/spacing/selection/add behavior and opening-list latency remain unmeasured. Other locale labels/accessibility deferred; Polish/base complete.235 parent lint warnings incl redundant clipboard SDK guard remain.
Dictionary coverage still pending: dodam,grzeje,kasami,nawilżane,odpowiadam,patrzysz,poczekaj,podpowie,pozdrawiam and kapitalizacją/kapitalizacje. Source usage priors, native quality/RAM and BS timing controls remain separate.

## 10. Next after maintainer reports completed runs
Read exact-head statuses/logs/test totals/original conformance/lint; fix any genuine failures with all gates retained. If green, download/re-hash APK+ZIP and verify feature identity before giving artifact. Phone checks: tap vs hold Schowek, words at opening and first typing replacing them, email/hyphen full ExactAdd retaining text/space and saved entry, BS/clipboard/autocorrect regression. Do not monitor indefinitely or resume unrelated dictionary work.

## 11. Delta from prior checkpoint
Prior ordinary-field CI+APK evidence is now complemented by maintainer acceptance. Current22-blob runtime trial introduces the three requested app behaviors and registered regressions; prior SI/model/ranking, dictionary producer and accepted BS remain. Both mains receive only this progress document, leaving runtime code on trial for CI/manual verification.
