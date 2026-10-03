# Android integration proposal — source casing variants v1

Status: concrete review proposal, not executable runtime implementation.
Baseline: CleverKeysPL `0da41d8951f96b9dab4e9fb219da5e4924aa66b6`.
Contract: LANGUAGE_INTELLIGENCE_API_V1_FINAL_2026-10-02.md.

## Required review before implementation

`memory/REPO_INSTRUCTIONS.md` requires Gemini 3 Pro via PAL for architectural
decisions and security-sensitive changes. PAL/Gemini is unavailable in this
session. The archive-import/parser work touches that rule. The producer in
the separate langpack repository is complete; this proposal is prepared for
the required consultation or an explicit user override of that requirement.

## Concrete integration scope

1. `langpack/LanguagePackManager.kt`: parse the API/capability/member declaration,
   bound extraction of the intelligence member, check filename/schema/SHA,
   validate before installation and copy it to the staged pack. Preserve legacy
   packages and reject unsupported API majors explicitly. Do not change model
   import or CTC routing. Preserve existing import errors/localization behavior.
2. New pure parser and immutable data model under `langpack/`: unique
   lowercase keys preserving diacritics, one/two capitalization forms for this
   trial, matching defaults/case policies, language agreement and bounded input.
   Read the capitalization fields; tolerate optional metadata/provenance, retaining
   its installed source file. Future wider inventories must not silently fail a
   trial-specific parser: define supported case policies and limits explicitly.
3. New provider: load installed pack metadata away from the UI thread, publish an
   immutable snapshot keyed by language/pack generation, clear it on deletion or
   replacement, return no variants for absent metadata/legacy packages. Do not
   insert variants into the dictionary, prefix index or geometric ranker.
4. `SuggestionHandler.handleSwipePredictionResults`: expand only the top ranked
   lexical key after lexical rescoring, while constructing bar words/scores/metas.
   Use the candidate's language if available. Two display forms share the original
   lexical score; no artificial second decoder membership or score boost. The next
   distinct decoder key follows the pair. Preserve aligned language/score/meta lists,
   possessive gating, swipe provenance, correction tracking and next-word append.
5. `SuggestionMeta` and `wiring/SuggestionBridge`: mark explicit surface choices
   so the commit path can preserve the exact selected spelling. The alternate is a
   replacement of the swipe token, never a NEXT_WORD append. Do not change all manual
   selections globally; constrain exact-case handling to these marked suggestions.
   Auto-insert and bar must agree on the selected primary surface.

## Proposed case behavior for review

Without Shift/autocap, prefer the pack's default, retain its alternate.
Existing user case preference may change ordering only if it matches a confirmed
variant. At sentence start or with Shift, put the capitalized form first and keep
the lowercase choice available. A manual variant tap preserves exactly that form.
Caps Lock remains explicit uppercase input; define and test its interaction with
the pair before coding rather than applying an unconditional uppercase map to both
forms and accidentally creating two identical suggestions. These case details are
proposed, not yet accepted or tested on Android.

## Acceptance scenarios

- Middle of sentence: top key łódź produces łódź/Łódź and the next distinct word;
  selecting Łódź replaces only the auto-inserted word, including correct space repair.
- Sentence start: primary Łódź, explicit lower-form tap commits łódź exactly.
- malina/Malina, warszawska/Warszawska; łódzki stays single; no metadata stays unchanged.
- Shift/Caps Lock and stored user casing do not collapse or override explicit choices.
- Pack replacement/deletion/language switch cannot expose stale or wrong-language forms.
- Legacy import succeeds; changed hashes, unsupported versions, duplicate keys/members,
  path traversal, excessive size and mismatched language are rejected before installation.
- Real InputConnection replacement handles terminal and ordinary editor paths; no
  stale asynchronous bar update restores an earlier slate.

Producer tests are not Android tests. A runtime commit must run the appropriate
pure/mock import and swipe-selection tests plus real IME checks. Existing Gradle
guard and device instructions remain mandatory.

Out of scope here: Łódźi→Łodzi morphology editing, full-pack source generation,
contextual AI, CTC changes, punctuation and learned case counts. The fixture already
includes the łodzi/Łodzi key, so later editing can reuse the variant provider.
