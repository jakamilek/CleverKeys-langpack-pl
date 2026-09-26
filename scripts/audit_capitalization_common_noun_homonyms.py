#!/usr/bin/env python3
"""Audit capitalization candidates for common-noun homonym collisions.

This is a generic audit for all additive modules. It intentionally does not use
membership in the immutable 100k core as evidence for or against capitalization.
For every candidate surface whose module policy requires capitalization, Morfeusz
2 / SGJP is queried on the lowercase spelling. If a common-noun (nazwa_pospolita)
analysis exists, the final surface must have an explicit auditable resolution in
surface_registry_policy.tsv or an explicit lowercase first-name policy.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from surface_components import component_surfaces

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


def common_noun_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    analyses = morfeusz.analyse(surface.lower())
    matches: list[dict[str, object]] = []
    for item in analyses:
        if len(item) < 3:
            continue
        payload = item[2]
        if not isinstance(payload, (tuple, list)) or len(payload) < 4:
            continue
        orth = str(payload[0])
        lemma = str(payload[1])
        tag = str(payload[2])
        classes = payload[3] if isinstance(payload[3], (tuple, list)) else []
        classes = [str(x) for x in classes]
        if tag.startswith("subst:") and COMMON_NOUN_CLASS in classes:
            matches.append(
                {
                    "orth": orth,
                    "lemma": lemma,
                    "tag": tag,
                    "classes": classes,
                }
            )
    return matches


def main() -> int:
    ap = argparse.ArgumentParser()
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
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    args = ap.parse_args()

    import morfeusz2

    lower_name_policies = {
        row["name"].strip().lower()
        for row in read_rows(args.first_name_surface_policy)
        if row["policy"].strip() == "lowercase_common_noun"
    }
    excluded_names = {
        row["name"].strip().lower()
        for row in read_rows(args.first_name_surface_policy)
        if row["policy"].strip() == "exclude"
    }

    candidates: dict[str, list[dict[str, str]]] = {}
    add_candidates(
        candidates,
        read_rows(args.first_name_inflections),
        "form",
        None,
        "first-name-inflection",
        lower_name_policies,
        "name",
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
    common_noun_count = 0
    capitalized_candidate_count = 0

    for key, rows in sorted(candidates.items()):
        capitalized = [r for r in rows if r["policy"] == "capitalized"]
        if not capitalized:
            continue
        capitalized_candidate_count += 1
        matches = common_noun_matches(morfeusz, key)
        has_common_noun = bool(matches)
        resolution = policy.get(key)
        resolved = True
        resolution_reason = None

        if len({r["policy"] for r in capitalized}) > 1 and resolution is None:
            resolved = False
            resolution_reason = "mixed-source-capitalization-policy-without-explicit-resolution"
        elif resolution is not None:
            canonical, case_policy = resolution
            if canonical.lower() != key:
                resolved = False
                resolution_reason = "policy-key-mismatch"
            elif has_common_noun and (case_policy != "lowercase" or canonical != key):
                resolved = False
                resolution_reason = "policy-does-not-select-lowercase-common-noun-surface"
            else:
                resolution_reason = "explicit-surface-registry-policy"
        elif has_common_noun:
            common_noun_count += 1
            if key in lower_name_policies:
                resolution_reason = "explicit-first-name-lowercase-common-noun-policy"
            else:
                resolved = False
                resolution_reason = "common-noun-homonym-without-explicit-lowercase-resolution"

        if has_common_noun:
            common_noun_count += 1 if resolution is not None and resolved else 0

        row = {
            "surface_key": key,
            "capitalized_candidates": sorted(
                {(r["surface"], r["source"]) for r in capitalized}
            ),
            "sources": sorted({r["source"] for r in rows}),
            "common_noun_homonym": has_common_noun,
            "common_noun_matches": matches,
            "explicit_surface_policy": (
                {"surface": resolution[0], "policy": resolution[1]}
                if resolution is not None
                else None
            ),
            "resolved": resolved,
            "resolution_reason": resolution_reason,
        }
        audited.append(row)
        if not resolved:
            unresolved.append(row)

    summary = {
        "mode": "generic-capitalization-common-noun-audit",
        "oracle": "Morfeusz 2 / SGJP",
        "rule": (
            "Capitalization candidates are audited independently of immutable-core "
            "membership; a common-noun homonym requires an explicit lowercase resolution."
        ),
        "capitalized_candidate_surface_count": capitalized_candidate_count,
        "common_noun_homonym_surface_count": common_noun_count,
        "unresolved_count": len(unresolved),
        "unresolved_surface_keys": [r["surface_key"] for r in unresolved],
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
