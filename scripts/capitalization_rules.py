#!/usr/bin/env python3
"""Shared capitalization rules for all CleverKeys Polish source modules.

Modules provide evidence; this resolver decides the canonical surface for one
case-insensitive dictionary key.

Precedence:
1. Any adjective analysis -> lowercase (absolute project rule).
2. Explicit audited lexical surface policy, where independently documented.
3. Verified ordinary common-noun homonym -> lowercase.
4. Lowercase-only source evidence -> lowercase.
5. Mixed unresolved source policies -> unresolved.
6. Otherwise source-backed proper-name evidence -> capitalized.

There is deliberately no first-name-specific capitalization branch.
"""

from __future__ import annotations

from typing import Iterable

COMMON_NOUN_CLASS = "nazwa_pospolita"
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
        [str(x) for x in classes],
    )


def adjective_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    """Return every adjective analysis; adjective is an absolute lowercase rule."""
    out: list[dict[str, object]] = []
    for item in morfeusz.analyse(surface.lower()):
        payload = _payload(item)
        if payload is None:
            continue
        orth, lemma, tag, classes = payload
        if tag.startswith("adj:"):
            out.append(
                {"orth": orth, "lemma": lemma, "tag": tag, "classes": classes}
            )
    return out


def common_lexical_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for item in morfeusz.analyse(surface.lower()):
        payload = _payload(item)
        if payload is None:
            continue
        orth, lemma, tag, classes = payload
        pos = tag.split(":", 1)[0]
        proper_classes = [
            cls
            for cls in classes
            if cls.startswith("nazwa_") and cls != COMMON_NOUN_CLASS
        ]
        if pos in ORDINARY_POS and not proper_classes:
            out.append(
                {
                    "orth": orth,
                    "lemma": lemma,
                    "tag": tag,
                    "classes": classes,
                }
            )
    return out


def resolve_capitalization(
    *,
    key: str,
    policies: Iterable[str],
    morfeusz,
    explicit_policy: tuple[str, str] | None = None,
) -> dict[str, object]:
    """Resolve one key using the single project-wide precedence order."""
    normalized = key.lower()
    policy_set = {
        value for value in policies if value in {"lowercase", "capitalized"}
    }
    adjectives = adjective_matches(morfeusz, normalized)
    lexical = common_lexical_matches(morfeusz, normalized)
    common_noun = [
        item for item in lexical
        if COMMON_NOUN_CLASS in item.get("classes", [])
    ]

    # Absolute project rule: every adjective is lowercase, regardless of module.
    if adjectives:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "adjective-absolute-lowercase",
            "common_lexical_matches": lexical,
            "common_adjective_matches": adjectives,
            "common_noun_matches": common_noun,
            "common_lexical_homonym": bool(lexical),
            "common_noun_homonym": bool(common_noun),
            "explicit_policy_conflict": (
                explicit_policy is not None and explicit_policy[1] == "capitalized"
            ),
        }

    if explicit_policy is not None:
        surface, policy = explicit_policy
        return {
            "resolved": True,
            "surface": surface,
            "policy": policy,
            "reason": "explicit-surface-registry-policy",
            "common_lexical_matches": lexical,
            "common_adjective_matches": adjectives,
            "common_noun_matches": common_noun,
            "common_lexical_homonym": bool(lexical),
            "common_noun_homonym": bool(common_noun),
            "explicit_policy_conflict": False,
        }

    # General lexical rule shared by all modules.
    if common_noun:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "common-noun-homonym-default-lowercase",
            "common_lexical_matches": lexical,
            "common_adjective_matches": adjectives,
            "common_noun_matches": common_noun,
            "common_lexical_homonym": bool(lexical),
            "common_noun_homonym": True,
            "explicit_policy_conflict": False,
        }

    if policy_set == {"lowercase"}:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "lowercase-source-evidence",
            "common_lexical_matches": lexical,
            "common_adjective_matches": adjectives,
            "common_noun_matches": common_noun,
            "common_lexical_homonym": bool(lexical),
            "common_noun_homonym": False,
            "explicit_policy_conflict": False,
        }

    if len(policy_set) > 1:
        return {
            "resolved": False,
            "surface": normalized,
            "policy": "lowercase",
            "reason": "mixed-source-capitalization-policy-without-explicit-resolution",
            "common_lexical_matches": lexical,
            "common_adjective_matches": adjectives,
            "common_noun_matches": common_noun,
            "common_lexical_homonym": bool(lexical),
            "common_noun_homonym": False,
            "explicit_policy_conflict": False,
        }

    if policy_set == {"capitalized"}:
        return {
            "resolved": True,
            "surface": normalized[:1].upper() + normalized[1:],
            "policy": "capitalized",
            "reason": "capitalized-source-without-common-noun-homonym",
            "common_lexical_matches": lexical,
            "common_adjective_matches": adjectives,
            "common_noun_matches": common_noun,
            "common_lexical_homonym": bool(lexical),
            "common_noun_homonym": False,
            "explicit_policy_conflict": False,
        }

    return {
        "resolved": True,
        "surface": normalized,
        "policy": "lowercase",
        "reason": "no-capitalization-source-evidence",
        "common_lexical_matches": lexical,
        "common_adjective_matches": adjectives,
        "common_noun_matches": common_noun,
        "common_lexical_homonym": bool(lexical),
        "common_noun_homonym": False,
        "explicit_policy_conflict": False,
    }
