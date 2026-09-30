#!/usr/bin/env python3
"""Shared capitalization oracle and resolver for CleverKeys Polish.

The capitalization decision for the immutable 100k core must come from
independent linguistic evidence, not from category-module membership.

Morfeusz 2 / SGJP exposes lexical "commonness" classifications such as
nazwa_pospolita, imię, nazwisko, geograficzna, marka and other proper-name
classes. This resolver treats those classifications as the primary lexical
evidence. Module source policies are accepted only as secondary evidence for
module-only keys; they are not used to decide capitalization of core keys.

Project precedence:
1. verified common-noun analysis -> lowercase, absolutely;
2. proper-name classification from either case probe -> capitalized;
3. adjective analysis without competing proper-name evidence -> lowercase;
4. other ordinary Polish lexical analysis -> lowercase;
5. explicit audited surface policy -> fallback only when linguistic evidence
   does not determine the surface;
6. module source policy -> fallback only for module-only keys;
7. no evidence -> unresolved.

There is deliberately no first-name-, city-, surname-, country- or
category-specific capitalization branch.
"""

from __future__ import annotations

from typing import Iterable

COMMON_NOUN_CLASS = "nazwa_pospolita"
CAPITALIZATION_POLICIES = {"lowercase", "capitalized"}
ORDINARY_POS = {
    "subst", "adj", "adv", "verb", "part", "prep", "conj",
    "num", "ger", "ppron", "pron",
}


def _payload(item):
    if len(item) < 3:
        return None
    payload = item[2]
    if not isinstance(payload, (tuple, list)) or len(payload) < 4:
        return None
    classes = payload[3] if isinstance(payload[3], (tuple, list)) else []
    return (
        str(payload[0]),
        str(payload[1]),
        str(payload[2]),
        [str(x) for x in classes if str(x)],
    )


def _analyses(morfeusz, surface: str) -> list[dict[str, object]]:
    """Return normalized single-token Morfeusz/SGJP analyses."""
    out: list[dict[str, object]] = []
    for item in morfeusz.analyse(surface):
        payload = _payload(item)
        if payload is None:
            continue
        orth, lemma, tag, classes = payload
        pos = tag.split(":", 1)[0]
        proper_classes = [
            cls for cls in classes
            if cls != COMMON_NOUN_CLASS
        ]
        out.append({
            "orth": orth,
            "lemma": lemma,
            "tag": tag,
            "classes": classes,
            "pos": pos,
            "proper_name_classes": proper_classes,
        })
    return out


def _surface_variants(surface: str) -> list[str]:
    normalized = surface.lower()
    capitalized = normalized[:1].upper() + normalized[1:] if normalized else normalized
    if capitalized == normalized:
        return [normalized]
    return [normalized, capitalized]


def _collect_analyses(morfeusz, surface: str) -> list[dict[str, object]]:
    """Probe lowercase and first-letter-capitalized forms."""
    out: list[dict[str, object]] = []
    seen: set[tuple[str, str, str, tuple[str, ...]]] = set()
    for variant in _surface_variants(surface):
        for item in _analyses(morfeusz, variant):
            identity = (
                str(item["orth"]),
                str(item["lemma"]),
                str(item["tag"]),
                tuple(str(x) for x in item["classes"]),
            )
            if identity in seen:
                continue
            seen.add(identity)
            out.append(item)
    return out

def adjective_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    """Return every adjective analysis from the lowercase/capitalized probes."""
    return [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
        }
        for item in _collect_analyses(morfeusz, surface)
        if item["pos"] == "adj"
    ]


def common_noun_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    """Return analyses explicitly classified as nazwa_pospolita."""
    return [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
        }
        for item in _collect_analyses(morfeusz, surface)
        if item["pos"] in ORDINARY_POS
        and COMMON_NOUN_CLASS in item["classes"]
    ]


def proper_name_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    """Return lexical analyses carrying a non-common proper-name class.

    The class vocabulary is intentionally open-ended. Morfeusz/SGJP documents
    multiple classes (e.g. imię, nazwisko, geograficzna, marka, firma,
    organizacja, osoba, własna). Any non-empty lexical classification other
    than nazwa_pospolita is therefore treated as proper-name evidence.
    """
    return [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
            "proper_name_classes": item["proper_name_classes"],
        }
        for item in _collect_analyses(morfeusz, surface)
        if item["pos"] in ORDINARY_POS
        and item["proper_name_classes"]
    ]


def ordinary_lexical_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    """Return any known lexical analysis without proper-name classification.

    Morfeusz uses a broad tagset (fin, impt, praet, inf, subst, adj, etc.).
    Restricting this gate to a short hand-written POS list falsely turns many
    perfectly known Polish forms into "unresolved". Unknown-word (ign) and
    punctuation (interp) analyses are excluded.
    """
    return [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
        }
        for item in _analyses(morfeusz, surface)
        if item["pos"] not in {"ign", "interp"}
        and not item["proper_name_classes"]
    ]


# Backwards-compatible diagnostic name used by existing reports.
def common_lexical_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    return ordinary_lexical_matches(morfeusz, surface)


def resolve_capitalization(
    *,
    key: str,
    policies: Iterable[str] = (),
    morfeusz,
    explicit_policy: tuple[str, str] | None = None,
    proper_lemma_keys: Iterable[str] | None = None,
) -> dict[str, object]:
    """Resolve one key from the independent linguistic capitalization oracle.

    policies and proper_lemma_keys are retained for diagnostics and for the
    module-only fallback path. They never override primary linguistic evidence
    for an immutable-core key.
    """
    normalized = key.lower()
    policy_set = {
        value for value in policies if value in CAPITALIZATION_POLICIES
    }
    proper_lemma_set = {
        str(value).strip().lower()
        for value in (proper_lemma_keys or ())
        if str(value).strip()
    }

    analyses = _collect_analyses(morfeusz, normalized)
    adjectives = [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
        }
        for item in analyses
        if item["pos"] == "adj"
    ]
    common_noun = [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
        }
        for item in analyses
        if item["pos"] in ORDINARY_POS
        and COMMON_NOUN_CLASS in item["classes"]
    ]
    proper_names = [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
            "proper_name_classes": item["proper_name_classes"],
        }
        for item in analyses
        if item["pos"] in ORDINARY_POS
        and item["proper_name_classes"]
    ]
    lexical = [
        {
            "orth": item["orth"],
            "lemma": item["lemma"],
            "tag": item["tag"],
            "classes": item["classes"],
        }
        for item in analyses
        if item["pos"] not in {"ign", "interp"}
        and not item["proper_name_classes"]
    ]

    base = {
        "common_lexical_matches": lexical,
        "common_adjective_matches": adjectives,
        "common_noun_matches": common_noun,
        "common_noun_homonym": bool(common_noun),
        "proper_name_matches": proper_names,
        "proper_name_classes": sorted({
            cls
            for item in proper_names
            for cls in item.get("proper_name_classes", [])
        }),
        "linguistic_analysis_count": len(analyses),
        "module_policy_evidence": sorted(policy_set),
        "proper_lemma_keys": sorted(proper_lemma_set),
    }

    # Absolute project rule: verified common noun always wins.
    if common_noun:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "common-noun-homonym-absolute-lowercase",
            "linguistic_basis": "common-noun",
            "explicit_policy_conflict": bool(
                explicit_policy is not None
                and explicit_policy[1] != "lowercase"
            ),
            **base,
        }

    # Proper-name evidence from the correctly-capitalized probe outranks an
    # adjective reading of the lowercase surface (for example, a surname vs.
    # an adjective). The absolute common-noun rule was handled above.
    if proper_names:
        return {
            "resolved": True,
            "surface": normalized[:1].upper() + normalized[1:],
            "policy": "capitalized",
            "reason": "proper-name-classification-from-linguistic-oracle",
            "linguistic_basis": "proper-name",
            "explicit_policy_conflict": bool(
                explicit_policy is not None
                and explicit_policy[1] != "capitalized"
            ),
            **base,
        }

    # Ordinary adjective forms are lowercase when no competing proper-name
    # interpretation exists in the case-sensitive oracle.
    if adjectives:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "adjective-absolute-lowercase",
            "linguistic_basis": "adjective",
            "explicit_policy_conflict": bool(
                explicit_policy is not None
                and explicit_policy[1] != "lowercase"
            ),
            **base,
        }
    # Ordinary Polish lexical evidence independently establishes lowercase.
    if lexical:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "ordinary-lexical-evidence-from-linguistic-oracle",
            "linguistic_basis": "ordinary-lexical",
            "explicit_policy_conflict": bool(
                explicit_policy is not None
                and explicit_policy[1] != "lowercase"
            ),
            **base,
        }

    # A human-audited global surface policy is a fallback for lexical gaps. It
    # does not override contradictory linguistic evidence above.
    if explicit_policy is not None:
        surface, policy = explicit_policy
        return {
            "resolved": True,
            "surface": surface,
            "policy": policy,
            "reason": "explicit-surface-registry-policy-fallback",
            "linguistic_basis": "explicit-fallback",
            "explicit_policy_conflict": False,
            **base,
        }

    # Module policy is deliberately last and only useful for additive
    # module-only keys that the linguistic dictionary does not classify.
    if policy_set == {"lowercase"}:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "module-source-policy-fallback",
            "linguistic_basis": "module-fallback",
            "explicit_policy_conflict": False,
            **base,
        }

    if policy_set == {"capitalized"}:
        return {
            "resolved": True,
            "surface": normalized[:1].upper() + normalized[1:],
            "policy": "capitalized",
            "reason": "module-source-policy-fallback",
            "linguistic_basis": "module-fallback",
            "explicit_policy_conflict": False,
            **base,
        }

    if len(policy_set) > 1:
        return {
            "resolved": False,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "mixed-module-source-policy-without-linguistic-resolution",
            "linguistic_basis": "unresolved",
            "explicit_policy_conflict": False,
            **base,
        }

    return {
        "resolved": False,
        "surface": normalized,
        "policy": "lowercase",
        "reason": "no-capitalization-or-linguistic-evidence",
        "linguistic_basis": "unresolved",
        "explicit_policy_conflict": False,
        **base,
    }
