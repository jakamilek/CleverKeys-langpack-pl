#!/usr/bin/env python3
"""Shared tokenization for multiword language-source surfaces."""

from __future__ import annotations

import re

# CKDT is word-oriented. Keep provenance at phrase level, but expose each
# lexical component as a candidate/audit surface. Hyphens separate components;
# the original full surface remains in the source artifact.
#
# Some international proper names contain an English possessive suffix, e.g.
# `John's`. The trailing `'s` is not an independent dictionary word, so it must
# not become a spurious one-letter component (`s`) in the Polish word surface
# registry. Internal apostrophes such as `D'...` are preserved as separators.
WORD_COMPONENT_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+")
TRAILING_ENGLISH_POSSESSIVE_RE = re.compile(r"(?i)'s\b")


def component_surfaces(surface: str) -> list[str]:
    normalized = TRAILING_ENGLISH_POSSESSIVE_RE.sub("", surface)
    return WORD_COMPONENT_RE.findall(normalized)


def component_records(surface: str) -> list[tuple[int, str]]:
    return [(index, part) for index, part in enumerate(component_surfaces(surface), 1)]


def is_multi_component(surface: str) -> bool:
    return len(component_surfaces(surface)) > 1
