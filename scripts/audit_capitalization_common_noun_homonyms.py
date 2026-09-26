#!/usr/bin/env python3
"""Audit and resolve capitalization for every active additive-module key.

This audit is the module-side decision layer built on the single project-wide
capitalization resolver. It intentionally does not use immutable-core membership
to decide casing. Every module key is resolved, including lowercase-only keys,
so downstream builders never need their own capitalization fallback.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from surface_components import component_surfaces
from capitalization_rules import resolve_capitalization

COMMON_NOUN_CLASS = "nazwa_pospolita"


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        lines = (
            line
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        )
        return list(csv.DictReader(lines, delimiter="\t"))


def add_candidates(
    out: dict[str, list[dict[str, str]]],
    rows: list[dict[str, str]],
    surface_field: str,
    policy_field: str | None,
    source: str,
    lower_names: set[str] = frozenset(),
    name_field: str | None = None,
) -> None:
    for row in rows:
        surface = row.get(surface_field, "").strip()
        if not surface:
            continue
        policy = (
            row.get(policy_field, "").strip()
            if policy_field
            else ("lowercase" if surface == surface.lower() else "capitalized")
        )
        if not policy:
            continue
        if name_field and row.get(name_field, "").strip().lower() in lower_names:
            policy = "lowercase"
            surface = surface.lower()
        for component in component_surfaces(surface):
            component_policy = policy if component[:1].isupper() else "lowercase"
            out.setdefault(component.lower(), []).append(
                {
                    "surface": component,
                    "policy": component_policy,
                    "source": source,
                }
            )


def load_surface_policy(path: Path) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for row in read_rows(path):
        key = row["surface_key"].strip().lower()
        surface = row["canonical_surface"].strip()
        policy = row["case_policy"].strip()
        if not key or surface.lower() != key:
            raise SystemExit(f"Malformed surface policy key/surface in {path}: {row}")
        if policy not in {"lowercase", "capitalized"}:
            raise SystemExit(f"Malformed surface policy case in {path}: {row}")
        out[key] = (surface, policy)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--first-name-inflections", type=Path, required=True)
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
    ap.add_argument(
        "--core-capitalization-audit",
        type=Path,
        default=None,
        help="Optional authoritative core audit. Core-overlapping surfaces are verified, not re-resolved here.",
    )
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    args = ap.parse_args()

    import morfeusz2

    first_name_rows = read_rows(args.first_name_inflections)
    candidates: dict[str, list[dict[str, str]]] = {}
    add_candidates(
        candidates,
        first_name_rows,
        "form",
        None,
        "first-name-inflection",
    )
    add_candidates(candidates, read_rows(args.cities), "name", None, "city")
    add_candidates(
        candidates, read_rows(args.city_inflections), "form", None, "city-inflection"
    )
    add_candidates(candidates, read_rows(args.terc_source), "name", "case_policy", "terc-source")
    add_candidates(
        candidates,
        read_rows(args.terc_inflections),
        "form",
        "case_policy",
        "terc",
    )
    add_candidates(
        candidates, read_rows(args.countries), "name", "case_policy", "country"
    )
    add_candidates(
        candidates,
        read_rows(args.country_inflections),
        "form",
        "case_policy",
        "country-inflection",
    )
    add_candidates(
        candidates, read_rows(args.capitals), "name", "case_policy", "capital"
    )
    add_candidates(
        candidates,
        read_rows(args.capital_inflections),
        "form",
        "case_policy",
        "capital-inflection",
    )
    add_candidates(
        candidates, read_rows(args.custom), "surface", "case_policy", "custom-manual"
    )

    policy = load_surface_policy(args.surface_registry_policy)
    core_resolved: dict[str, dict[str, str]] = {}
    if args.core_capitalization_audit:
        core_audit = json.loads(args.core_capitalization_audit.read_text(encoding="utf-8"))
        if core_audit.get("unresolved_count", 0):
            raise SystemExit(
                "Authoritative core capitalization audit is unresolved: "
                + ", ".join(core_audit.get("unresolved_keys", []))
            )
        core_resolved = core_audit.get("resolved_surfaces", {})
    core_keys = set(core_resolved)
    # Explicit global surface policies are themselves capitalization decisions and
    # must also be audited, independently of whether the key is present in a module.
    for key, (surface, case_policy) in policy.items():
        candidates.setdefault(key, []).append(
            {
                "surface": surface,
                "policy": case_policy,
                "source": "surface-registry-policy",
            }
        )

    morfeusz = morfeusz2.Morfeusz()

    audited = []
    unresolved = []
    resolved_surfaces: dict[str, dict[str, str]] = {}
    common_noun_count = 0
    capitalized_candidate_count = 0
    core_authoritative_count = 0

    for key, rows in sorted(candidates.items()):
        if key in core_keys:
            authoritative = core_resolved[key]
            audited.append({
                "surface_key": key,
                "capitalized_candidates": sorted({
                    (r["surface"], r["source"])
                    for r in rows
                    if r["policy"] == "capitalized"
                }),
                "sources": sorted({r["source"] for r in rows}),
                "common_lexical_homonym": None,
                "common_noun_homonym": None,
                "common_lexical_matches": [],
                "common_adjective_matches": [],
                "common_noun_matches": [],
                "explicit_surface_policy": (
                    {"surface": policy[key][0], "policy": policy[key][1]}
                    if key in policy else None
                ),
                "resolved": True,
                "resolution_reason": "core-authoritative",
                "core_authoritative": True,
                "canonical_surface": authoritative["surface"],
                "canonical_policy": authoritative["policy"],
            })
            resolved_surfaces[key] = authoritative
            core_authoritative_count += 1
            continue

        # Every module-only key goes through the same shared resolver, even when
        # its source evidence is lowercase-only. This is what makes adjective
        # -> lowercase and all other project-wide rules apply uniformly.
        policies = {
            r["policy"]
            for r in rows
            if r["policy"] in {"lowercase", "capitalized"}
        }
        resolution = resolve_capitalization(
            key=key,
            policies=policies,
            morfeusz=morfeusz,
            explicit_policy=policy.get(key),
        )
        capitalized = [r for r in rows if r["policy"] == "capitalized"]
        if capitalized:
            capitalized_candidate_count += 1

        row = {
            "surface_key": key,
            "capitalized_candidates": sorted({
                (r["surface"], r["source"]) for r in capitalized
            }),
            "sources": sorted({r["source"] for r in rows}),
            "common_lexical_homonym": bool(resolution["common_lexical_matches"]),
            "common_noun_homonym": bool(resolution["common_noun_matches"]),
            "common_lexical_matches": resolution["common_lexical_matches"],
            "common_adjective_matches": resolution["common_adjective_matches"],
            "common_noun_matches": resolution["common_noun_matches"],
            "explicit_surface_policy": (
                {"surface": policy[key][0], "policy": policy[key][1]}
                if key in policy else None
            ),
            "resolved": bool(resolution["resolved"]),
            "resolution_reason": str(resolution["reason"]),
            "core_authoritative": False,
            "canonical_surface": str(resolution["surface"]),
            "canonical_policy": str(resolution["policy"]),
        }
        audited.append(row)
        if resolution["resolved"]:
            resolved_surfaces[key] = {
                "surface": str(resolution["surface"]),
                "policy": str(resolution["policy"]),
                "reason": str(resolution["reason"]),
            }
        else:
            unresolved.append(row)
        if resolution["common_noun_matches"]:
            common_noun_count += 1

    summary = {
        "mode": "generic-capitalization-common-noun-audit",
        "oracle": "Morfeusz 2 / SGJP",
        "rule": (
            "Capitalization candidates are audited independently of immutable-core "
            "membership; common-noun homonymy defaults lowercase unless an explicitly "
            "audited first-name surface or explicit surface policy resolves capitalization."
        ),
        "capitalized_candidate_surface_count": capitalized_candidate_count,
        "common_noun_homonym_surface_count": common_noun_count,
        "unresolved_count": len(unresolved),
        "unresolved_surface_keys": [r["surface_key"] for r in unresolved],
        "resolved_surfaces": resolved_surfaces,
        "core_authoritative_keys": core_authoritative_count,
        "module_only_keys_analyzed": sum(
            1 for row in audited if not row.get("core_authoritative")
        ),
        "module_only_keys_resolved": sum(
            1
            for row in audited
            if not row.get("core_authoritative") and row.get("resolved")
        ),
        "audited": audited,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(
            [
                "surface_key",
                "capitalized_candidates",
                "common_noun_homonym",
                "common_noun_matches",
                "explicit_surface_policy",
                "resolved",
                "resolution_reason",
                "core_authoritative",
                "canonical_surface",
                "canonical_policy",
            ]
        )
        for row in audited:
            writer.writerow(
                [
                    row["surface_key"],
                    json.dumps(row["capitalized_candidates"], ensure_ascii=False),
                    str(row["common_noun_homonym"]).lower(),
                    json.dumps(row["common_noun_matches"], ensure_ascii=False),
                    json.dumps(row["explicit_surface_policy"], ensure_ascii=False),
                    str(row["resolved"]).lower(),
                    row["resolution_reason"] or "",
                ]
            )

    if unresolved:
        print(
            "Unresolved common-noun capitalization collisions: "
            + ", ".join(r["surface_key"] for r in unresolved)
        )
        return 1

    print(
        json.dumps(
            {
                "capitalized_candidate_surface_count": capitalized_candidate_count,
                "common_noun_homonym_surface_count": common_noun_count,
                "unresolved_count": 0,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
