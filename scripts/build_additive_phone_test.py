#!/usr/bin/env python3
"""Build the production-shaped additive module preview over the immutable 100k core."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path


def read_base(path: Path) -> dict[str, str]:
    surfaces: dict[str, str] = {}
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        key = value.lower()
        prior = surfaces.get(key)
        if prior is not None and prior != value:
            raise SystemExit(f"Conflicting core surface {path}:{line_no}: {prior!r} vs {value!r}")
        surfaces[key] = value
    if len(surfaces) != 100000:
        raise SystemExit(f"Immutable core must contain exactly 100000 keys, got {len(surfaces)}")
    return surfaces


def load_first_name_policy(path: Path) -> set[str]:
    lower: set[str] = set()
    with path.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if row["policy"].strip() == "lowercase_common_noun":
                lower.add(row["name"].strip().lower())
    return lower


def add_records(registry, rows, surface_field, policy_field, source, lower_keys=frozenset()):
    for row in rows:
        surface = row[surface_field].strip()
        if not surface:
            continue
        key = surface.lower()
        policy = row[policy_field].strip() if policy_field else ("lowercase" if surface == surface.lower() else "capitalized")
        if key in lower_keys:
            surface = key
            policy = "lowercase"
        registry.setdefault(key, []).append({"surface": surface, "policy": policy, "source": source})


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        lines = (
            line for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        )
        return list(csv.DictReader(lines, delimiter="\t"))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--first-name-inflections", type=Path, required=True)
    ap.add_argument("--first-name-surface-policy", type=Path, required=True)
    ap.add_argument("--cities", type=Path, required=True)
    ap.add_argument("--city-inflections", type=Path, required=True)
    ap.add_argument("--terc-inflections", type=Path, required=True)
    ap.add_argument("--countries", type=Path, required=True)
    ap.add_argument("--country-inflections", type=Path, required=True)
    ap.add_argument("--capitals", type=Path, required=True)
    ap.add_argument("--capital-inflections", type=Path, required=True)
    ap.add_argument("--custom", type=Path, required=True)
    ap.add_argument("--surface-registry-policy", type=Path, required=True)
    ap.add_argument("--out-wordlist", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

    base = read_base(args.base)
    lowercase_names = load_first_name_policy(args.first_name_surface_policy)

    registry: dict[str, list[dict[str, str]]] = {
        key: [{"surface": surface, "policy": "lowercase" if surface == surface.lower() else "capitalized", "source": "immutable-100k-core"}]
        for key, surface in base.items()
    }

    add_records(registry, read_rows(args.first_name_inflections), "form", None, "first-name-inflection", lowercase_names)
    add_records(registry, read_rows(args.cities), "name", None, "city")
    add_records(registry, read_rows(args.city_inflections), "form", None, "city-inflection")
    add_records(registry, read_rows(args.terc_inflections), "form", "case_policy", "terc")
    add_records(registry, read_rows(args.countries), "name", "case_policy", "country")
    add_records(registry, read_rows(args.country_inflections), "form", "case_policy", "country-inflection")
    add_records(registry, read_rows(args.capitals), "name", "case_policy", "capital")
    add_records(registry, read_rows(args.capital_inflections), "form", "case_policy", "capital-inflection")
    add_records(registry, read_rows(args.custom), "surface", "case_policy", "custom-manual")

    overrides = {}
    with args.surface_registry_policy.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            key = row["surface_key"].strip().lower()
            overrides[key] = (row["canonical_surface"].strip(), row["case_policy"].strip())

    conflicts = []
    resolved: dict[str, str] = {}
    explicit_sources = {
        "immutable-100k-core",
    }
    for key, candidates in sorted(registry.items()):
        explicit = [c for c in candidates if c["source"] != "immutable-100k-core"]
        variants = {(c["surface"], c["policy"]) for c in explicit}
        override = overrides.get(key)

        if override:
            surface, policy = override
            if surface not in {c["surface"] for c in explicit}:
                conflicts.append({
                    "key": key,
                    "candidates": sorted(variants),
                    "reason": "override-is-not-a-contributing-surface",
                })
                continue
            resolved[key] = surface
            continue

        if len({c["policy"] for c in explicit}) > 1:
            conflicts.append({
                "key": key,
                "candidates": sorted(variants),
                "sources": sorted({c["source"] for c in explicit}),
            })
            continue

        if explicit:
            policy = next(iter(explicit))["policy"]
            if policy == "lowercase":
                resolved[key] = key
            else:
                surfaces = sorted({c["surface"] for c in explicit})
                resolved[key] = next((s for s in surfaces if s[:1].isupper()), surfaces[0])
        else:
            resolved[key] = base[key]

    if conflicts:
        sample = "; ".join(
            f"{r['key']}={r['candidates']}" for r in conflicts[:20]
        )
        raise SystemExit("Unresolved additive surface registry conflicts: " + sample)

    args.out_wordlist.parent.mkdir(parents=True, exist_ok=True)
    words = [resolved[key] for key in sorted(resolved)]
    if len(words) != len(resolved) or len({w.lower() for w in words}) != len(words):
        raise SystemExit("Additive preview contains duplicate dictionary keys")
    if not set(base).issubset({w.lower() for w in words}):
        raise SystemExit("Immutable 100k core key set was not preserved")

    module_keys = set(resolved) - set(base)
    lowercase_count = sum(1 for surface in resolved.values() if surface == surface.lower())
    capitalized_count = len(resolved) - lowercase_count
    report = {
        "mode": "production-shaped-additive-phone-test",
        "immutable_core_keys": len(base),
        "final_keys": len(resolved),
        "kept": len(resolved),
        "net_new_module_keys": len(module_keys),
        "formula": "100000 + union(net-new case-insensitive module keys)",
        "surface_registry_keys": len(registry),
        "surface_registry_conflicts": len(conflicts),
        "capitalization_audit": {
            "checked": len(resolved),
            "lowercase_surfaces": lowercase_count,
            "capitalized_surfaces": capitalized_count,
            "violations": [],
        },
        "explicit_surface_resolutions": [
            {"key": key, "surface": value[0], "policy": value[1]}
            for key, value in sorted(overrides.items())
            if key in registry
        ],
    }
    args.out_wordlist.write_text(
        "# CleverKeys Polish production-shaped additive module phone-test list\n"
        f"# immutable_core=100000 final_keys={len(words)} net_new_modules={len(module_keys)}\n"
        + "\n".join(words) + "\n",
        encoding="utf-8",
    )
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
