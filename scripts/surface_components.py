#!/usr/bin/env python3
"""Shared tokenization for multiword language-source surfaces."""

from __future__ import annotations

import re

# CKDT is word-oriented. Keep provenance at phrase level, but expose each
# lexical component as a candidate/audit surface. Hyphens separate components;
# the original full surface remains in the source artifact.
#
# Some international proper names contain an English possessive suffix, e.g.
# `John's` or `John’s`. That suffix is not an independent dictionary word,
# so it must not become a spurious one-letter component (`s`) in the Polish
# word surface registry. The same rule applies to an uppercase possessive `'S`
# / `’S`. Internal apostrophes such as `D'...` or `D’...` are preserved as
# separators for component-level audit.
WORD_COMPONENT_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+")
# Only these characters are treated as lexical hyphens for the dedicated
# hyphenated-name processing path. En/em dashes and punctuation are not.
LEXICAL_HYPHENS = ("-", "‐", "‑")
HYPHEN_SPLIT_RE = re.compile(r"[-‐‑]")
ENGLISH_POSSESSIVE_RE = re.compile(r"(?i)(?:'|’|＇)s\b")


def component_surfaces(surface: str) -> list[str]:
    normalized = ENGLISH_POSSESSIVE_RE.sub("", surface)
    return WORD_COMPONENT_RE.findall(normalized)


def component_records(surface: str) -> list[tuple[int, str]]:
    return [(index, part) for index, part in enumerate(component_surfaces(surface), 1)]


def is_multi_component(surface: str) -> bool:
    return len(component_surfaces(surface)) > 1


def is_hyphenated(surface: str) -> bool:
    """Return whether a surface contains a project-recognized lexical hyphen."""
    return bool(HYPHEN_SPLIT_RE.search(surface)) and len(hyphen_components(surface)) > 1


def hyphen_components(surface: str) -> list[str]:
    """Return lexical components of a hyphenated surface without changing text."""
    return [part.strip() for part in HYPHEN_SPLIT_RE.split(surface) if part.strip()]
