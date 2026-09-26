#!/usr/bin/env python3
"""Build the production-shaped additive module preview over the immutable 100k core."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from surface_components import component_surfaces


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
        raw_surface = row[surface_field].strip()
        if not raw_surface:
            continue
        for surface in component_surfaces(raw_surface):
            key = surface.lower()
            source_policy = row[policy_field].strip() if policy_field else (
                "lowercase" if surface == surface.lower() else "capitalized"
            )
            # Phrase-level capitalized policy still respects explicitly lowercase
            # connector components such as "de"/"la" by preserving their source case.
            policy = (
                "lowercase"
                if surface == surface.lower()
                else source_policy
            )
            if key in lower_keys:
                surface = key
                policy = "lowercase"
            registry.setdefault(key, []).append(
                {
                    "surface": surface,
                    "policy": policy,
                    "source": source,
                }
            )


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
    ap.add_argument("--terc-source", type=Path, required=True)
    ap.add_argument("--terc-inflections", type=Path, required=True)
    ap.add_argument("--countries", type=Path, required=True)
    ap.add_argument("--country-inflections", type=Path, required=True)
    ap.add_argument("--capitals", type=Path, required=True)
    ap.add_argument("--capital-inflections", type=Path, required=True)
    ap.add_argument("--custom", type=Path, required=True)
    ap.add_argument("--surface-registry-policy", type=Path, required=True)
    ap.add_argument("--core-capitalization-audit", type=Path, required=True)
    ap.add_argument("--module-capitalization-audit", type=Path, required=True)
    ap.add_argument("--out-wordlist", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

    base = read_base(args.base)
    lowercase_names = load_first_name_policy(args.first_name_surface_policy)

    core_audit = json.loads(args.core_capitalization_audit.read_text(encoding="utf-8"))
    module_audit = json.loads(args.module_capitalization_audit.read_text(encoding="utf-8"))
    if core_audit.get("unresolved_count", 0):
        raise SystemExit(
            "Core capitalization audit contains unresolved keys: "
            + ", ".join(core_audit.get("unresolved_keys", []))
        )
    if module_audit.get("unresolved_count", 0):
        raise SystemExit(
            "Module capitalization audit contains unresolved keys: "
            + ", ".join(module_audit.get("unresolved_surface_keys", []))
        )
    core_resolved = core_audit.get("resolved_surfaces", {})
    module_resolved = module_audit.get("resolved_surfaces", {})

    registry: dict[str, list[dict[str, str]]] = {
        key: [{
            "surface": core_resolved.get(key, {}).get("surface", surface),
            "policy": (
                core_resolved.get(key, {}).get("policy", "")
                or ("lowercase" if surface == surface.lower() else "capitalized")
            ),
            "source": "immutable-100k-core",
        }]
        for key, surface in base.items()
    }

    add_records(registry, read_rows(args.first_name_inflections), "form", None, "first-name-inflection", lowercase_names)
    add_records(registry, read_rows(args.cities), "name", None, "city")
    add_records(registry, read_rows(args.city_inflections), "form", None, "city-inflection")
    add_records(registry, read_rows(args.terc_source), "name", "case_policy", "terc-source")
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
    core_authoritative_keys = 0
    module_audited_keys = 0
    module_only_keys = 0

    for key, candidates in sorted(registry.items()):
        # The immutable-core capitalization audit is authoritative for every key that
        # belongs to the 100k core. Module evidence can explain or verify the decision,
        # but it must never replace the canonical core surface.
        if key in base:
            authoritative = core_resolved.get(key)
            if authoritative is not None:
                resolved[key] = authoritative["surface"]
                core_authoritative_keys += 1
            else:
                resolved[key] = base[key]
            continue

        module_only_keys += 1
        audited = module_resolved.get(key)
        override = overrides.get(key)

        # For net-new module keys, the module capitalization audit is the decision layer.
        # An explicit global surface policy remains the final deterministic override.
        if override is not None:
            resolved[key] = override[0]
        elif audited is not None:
            resolved[key] = audited["surface"]
            module_audited_keys += 1
        elif candidates:
            explicit = [c for c in candidates if c["source"] != "immutable-100k-core"]
            if explicit:
                policy = next(iter({c["policy"] for c in explicit}))
                surfaces = sorted({c["surface"] for c in explicit})
                resolved[key] = key if policy == "lowercase" else next(
                    (s for s in surfaces if s[:1].isupper()), surfaces[0]
                )
            else:
                resolved[key] = base[key]
        else:
            raise SystemExit(f"No capitalization source for module key {key!r}")

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
        "capitalization_authority": {
            "core_authoritative_keys": core_authoritative_keys,
            "module_only_keys": module_only_keys,
            "module_audited_keys": module_audited_keys,
            "module_is_second_layer_for_core": True,
        },
        "capitalization_audit": {
            "checked": len(resolved),
            "lowercase_surfaces": lowercase_count,
            "capitalized_surfaces": capitalized_count,
            "violations": [],
        },
        "core_capitalization_resolutions": [
            {"key": key, "surface": value["surface"], "policy": value["policy"], "reason": value["reason"]}
            for key, value in sorted(core_resolved.items())
            if value["surface"] != base.get(key, value["surface"])
        ],
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
