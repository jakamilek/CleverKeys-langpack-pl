#!/usr/bin/env python3
"""Count immutable-core keys that can reasonably carry both lowercase/capitalized forms.

This audit is deliberately module-independent. It inspects only the immutable 100k
core and Morfeusz 2 / SGJP analyses.

A dual-casing candidate is intentionally narrow:
- the key is a singular nominative common noun (subst:sg:nom), and
- the same case-folded surface also has a distinct singular nominative proper-name
  noun analysis (subst:sg:nom) with a non-common lexical class.

Inflected forms, adjectives, surnames used only as inflectional analyses, and other
non-nominative surfaces are excluded from the count. The result estimates the set
for which storing both lowercase and capitalized candidate surfaces could be useful.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def is_singular_nominative_noun(tag: str) -> bool:
    parts = tag.split(":")
    if not parts or parts[0] != "subst":
        return False
    return "sg" in parts[1:] and "nom" in parts[1:]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    args = ap.parse_args()

    base = {
        line.strip().lower()
        for line in args.base.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    if len(base) != 100000:
        raise SystemExit(f"Immutable core must contain exactly 100000 keys, got {len(base)}")

    import morfeusz2

    morfeusz = morfeusz2.Morfeusz()
    common_class = "nazwa_pospolita"
    ignored = {"nazwa_pospolita"}
    rows: list[dict[str, object]] = []

    for key in sorted(base):
        normalized = key.lower()
        variants = [normalized]
        cap = normalized[:1].upper() + normalized[1:] if normalized else normalized
        if cap != normalized:
            variants.append(cap)

        seen_common: set[tuple[str, str, tuple[str, ...]]] = set()
        seen_proper: set[tuple[str, str, tuple[str, ...]]] = set()

        for variant in variants:
            for item in morfeusz.analyse(variant):
                if len(item) < 3:
                    continue
                payload = item[2]
                if not isinstance(payload, (tuple, list)) or len(payload) < 4:
                    continue
                orth = str(payload[0])
                lemma = str(payload[1])
                tag = str(payload[2])
                classes = tuple(str(x) for x in payload[3] if str(x)) if isinstance(payload[3], (tuple, list)) else ()
                if not is_singular_nominative_noun(tag):
                    continue

                if common_class in classes:
                    seen_common.add((orth, lemma, classes))
                    continue

                proper_classes = tuple(sorted(cls for cls in classes if cls not in ignored))
                if proper_classes:
                    seen_proper.add((orth, lemma, proper_classes))

        if seen_common and seen_proper:
            rows.append({
                "surface_key": normalized,
                "common_analyses": [
                    {"orth": a, "lemma": b, "classes": list(c)}
                    for a, b, c in sorted(seen_common)
                ],
                "proper_analyses": [
                    {"orth": a, "lemma": b, "classes": list(c)}
                    for a, b, c in sorted(seen_proper)
                ],
            })

    summary = {
        "mode": "immutable-core-dual-casing-candidate-audit",
        "authority": "independent Morfeusz 2 / SGJP only",
        "modules_consulted": False,
        "core_keys": len(base),
        "candidate_count": len(rows),
        "definition": {
            "common_side": "subst + sg + nom + nazwa_pospolita",
            "proper_side": "subst + sg + nom + non-nazwa_pospolita lexical class",
            "casefolded_surface": True,
            "inflected_forms_excluded": True,
        },
        "candidate_keys": [row["surface_key"] for row in rows],
        "candidates": rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        handle.write("surface_key\tcommon_analyses\tproper_analyses\n")
        for row in rows:
            handle.write(
                row["surface_key"]
                + "\t"
                + json.dumps(row["common_analyses"], ensure_ascii=False, sort_keys=True)
                + "\t"
                + json.dumps(row["proper_analyses"], ensure_ascii=False, sort_keys=True)
                + "\n"
            )

    print(json.dumps({
        "candidate_count": len(rows),
        "sample_first_50": [row["surface_key"] for row in rows[:50]],
        "sample_checks": {
            key: next((row for row in rows if row["surface_key"] == key), None)
            for key in ("warszawa", "łódź", "malina", "bardo")
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
