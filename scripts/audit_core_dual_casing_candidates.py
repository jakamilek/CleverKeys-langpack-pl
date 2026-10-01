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
from collections import Counter
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
    # SGJP currently exposes the common-name classification in two NAME spellings
    # in this dictionary snapshot. Both mean common-name evidence for this audit.
    common_classes = {"nazwa_pospolita", "nazwa pospolita"}
    ignored = set(common_classes)
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

                if any(common_class in classes for common_class in common_classes):
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

    # Class distributions count each candidate key once per distinct class; combinations preserve the full per-key class signature.
    # A candidate is counted once per atomic NAME class present in its
    # competing proper-name analyses. We also retain exact candidate keys per
    # class so the next analysis stage can inspect categories independently.
    candidate_classes: dict[str, set[str]] = {}
    for row in rows:
        classes = {
            cls
            for item in row["proper_analyses"]
            for cls in item["classes"]
        }
        candidate_classes[row["surface_key"]] = classes

    proper_class_distribution = Counter(
        cls
        for classes in candidate_classes.values()
        for cls in sorted(classes)
    )
    proper_class_candidate_keys = {
        cls: sorted(
            key for key, classes in candidate_classes.items()
            if cls in classes
        )
        for cls in sorted({
            cls
            for classes in candidate_classes.values()
            for cls in classes
        })
    }
    proper_class_combination_distribution = Counter(
        " + ".join(sorted(classes))
        for classes in candidate_classes.values()
    )
    surname_only_candidate_count = sum(
        bool(classes) and classes == {"nazwisko"}
        for classes in candidate_classes.values()
    )
    non_surname_candidate_count = sum(
        any(cls != "nazwisko" for cls in classes)
        for classes in candidate_classes.values()
    )
    surname_plus_other_class_candidate_count = sum(
        "nazwisko" in classes and any(cls != "nazwisko" for cls in classes)
        for classes in candidate_classes.values()
    )

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
        "proper_class_distribution_by_candidate": dict(sorted(proper_class_distribution.items())),
        "proper_class_candidate_keys": proper_class_candidate_keys,
        "proper_class_combination_distribution": dict(sorted(proper_class_combination_distribution.items())),
        "surname_only_candidate_count": surname_only_candidate_count,
        "non_surname_candidate_count": non_surname_candidate_count,
        "surname_plus_other_class_candidate_count": surname_plus_other_class_candidate_count,
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
        "all_candidate_keys": [row["surface_key"] for row in rows],
        "proper_class_distribution_by_candidate": dict(sorted(proper_class_distribution.items())),
        "proper_class_combination_distribution": dict(sorted(proper_class_combination_distribution.items())),
        "surname_only_candidate_count": surname_only_candidate_count,
        "non_surname_candidate_count": non_surname_candidate_count,
        "surname_plus_other_class_candidate_count": surname_plus_other_class_candidate_count,
        "sample_checks": {
            key: next((row for row in rows if row["surface_key"] == key), None)
            for key in ("warszawa", "łódź", "malina", "bardo")
        },
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
