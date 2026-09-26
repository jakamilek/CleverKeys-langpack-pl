#!/usr/bin/env python3
"""Shared tokenization for multiword language-source surfaces."""

from __future__ import annotations

import re

# CKDT is word-oriented. Keep provenance at phrase level, but expose each
# letter-run component as a candidate/audit surface. Hyphens separate components;
# the original full surface remains in the source artifact.
WORD_COMPONENT_RE = re.compile(r"[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż]+")


def component_surfaces(surface: str) -> list[str]:
    return WORD_COMPONENT_RE.findall(surface)


def component_records(surface: str) -> list[tuple[int, str]]:
    return [(index, part) for index, part in enumerate(component_surfaces(surface), 1)]


def is_multi_component(surface: str) -> bool:
    return len(component_surfaces(surface)) > 1
