#!/usr/bin/env python3
"""Measure net dictionary cost of additive language modules.

The comparison key is case-insensitive: a module form already represented by the
100k frequency core does not consume a new dictionary slot. It may, however, replace
the core surface (for example "warszawa" -> "Warszawa") through the normal casing
layer.

Usage:
  python3 scripts/analyze_dictionary_modules.py \
      --base build/base100k.txt \
      --module first_names=build/pl-first-name-inflections.tsv:form \
      --module cities=build/pl-city-source.tsv:name \
      --module city_inflections=build/pl-city-inflections.tsv:form \
      --out build/module-study.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_lines(path: Path) -> set[str]:
    words: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        words.add(line)
    return words


def load_column(path: Path, column: str) -> set[str]:
    import csv

    # Some reviewed staging TSVs intentionally have their schema documented in
    # comments rather than a machine-readable header.  Their second/third
    # fields contain semicolon-separated dictionary surfaces.  Support those
    # files explicitly so the module-cost report measures words, not metadata.
    if column == "__family_forms__":
        values: set[str] = set()
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.split("\t")
            if len(fields) < 2:
                continue
            start = 2 if path.name == "reviewed_morphology.tsv" else 1
            if len(fields) <= start:
                continue
            for surface in fields[start].split(";"):
                surface = surface.strip()
                if surface:
                    values.add(surface)
        return values

    with path.open(encoding="utf-8", newline="") as handle:
        rows = (line for line in handle if line.strip() and not line.lstrip().startswith("#"))
        reader = csv.DictReader(rows, delimiter="\t")
        if column not in (reader.fieldnames or []):
            raise SystemExit(
                f"Module source {path} has no column {column!r}; "
                f"available={reader.fieldnames}"
            )
        values = set()
        for row in reader:
            value = row[column].strip()
            if value:
                values.add(value)
        return values


def parse_module(spec: str) -> tuple[str, Path, str]:
    try:
        name, rest = spec.split("=", 1)
        path_text, column = rest.rsplit(":", 1)
    except ValueError as exc:
        raise SystemExit(
            f"Malformed --module {spec!r}; expected NAME=PATH:COLUMN"
        ) from exc
    if not name or not path_text or not column:
        raise SystemExit(
            f"Malformed --module {spec!r}; expected NAME=PATH:COLUMN"
        )
    return name, Path(path_text), column


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument(
        "--module",
        action="append",
        default=[],
        help="NAME=PATH:COLUMN; repeat in the intended module order.",
    )
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    base_surface = load_lines(args.base)
    base_keys = {word.lower() for word in base_surface}
    if len(base_keys) != len(base_surface):
        raise SystemExit("Base dictionary contains case-insensitive duplicate keys")
    base_surface_by_key = {word.lower(): word for word in base_surface}

    cumulative_keys = set(base_keys)
    rows = []
    all_module_keys: set[str] = set()

    for index, spec in enumerate(args.module, 1):
        name, path, column = parse_module(spec)
        raw = load_lines(path) if column == "__lines__" else load_column(path, column)
        keys = {word.lower() for word in raw}
        duplicate_case_variants = len(raw) - len(keys)
        already_in_base = keys & base_keys
        new_vs_base = keys - base_keys
        cumulative_new = keys - cumulative_keys
        overlap_previous_modules = new_vs_base - cumulative_new
        replacement_keys = {
            key
            for key in already_in_base
            if any(surface != base_surface_by_key[key] for surface in raw if surface.lower() == key)
        }

        rows.append({
            "order": index,
            "module": name,
            "source": str(path),
            "column": column,
            "source_surfaces": len(raw),
            "unique_keys": len(keys),
            "case_variants_collapsed": duplicate_case_variants,
            "already_in_100k_base": len(already_in_base),
            "existing_keys_with_surface_replacement": len(replacement_keys),
            "surface_replacements": sorted(
                (
                    {
                        "key": key,
                        "base_surface": base_surface_by_key[key],
                        "module_surfaces": sorted(surface for surface in raw if surface.lower() == key),
                    }
                    for key in replacement_keys
                ),
                key=lambda item: item["key"],
            ),
            "new_unique_keys_vs_100k_base": len(new_vs_base),
            "new_unique_keys_after_previous_modules": len(cumulative_new),
            "overlap_with_previous_modules": len(overlap_previous_modules),
            "new_keys_after_previous_modules": sorted(cumulative_new),
        })

        cumulative_keys |= keys
        all_module_keys |= keys

    result = {
        "base": {
            "surface_entries": len(base_surface),
            "unique_case_insensitive_keys": len(base_keys),
        },
        "modules": rows,
        "union": {
            "module_unique_keys": len(all_module_keys),
            "module_keys_already_in_base": len(all_module_keys & base_keys),
            "module_keys_new_vs_base": len(all_module_keys - base_keys),
            "final_unique_keys": len(cumulative_keys),
            "net_additions_over_100k_base": len(cumulative_keys) - len(base_keys),
        },
        "rule": (
            "Case-insensitive key equality prevents duplicate slots. A module may "
            "replace the base surface/casing without increasing unique-key count."
        ),
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result["union"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
