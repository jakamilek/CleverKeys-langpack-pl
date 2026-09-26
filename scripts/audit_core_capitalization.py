#!/usr/bin/env python3
"""Audit and resolve capitalization of immutable-core keys using source evidence.

The immutable 100k membership is never changed here. Only the canonical surface
(casing) may be corrected for a core key, based on independently retained source
evidence. This audit runs before module assembly.

Rules:
- source evidence is collected from all active module/source layers, including
  multi-component names;
- capitalization is never inferred from 100k membership;
- a capitalized source candidate is checked independently for a verified common-noun
  homonym using Morfeusz 2 / SGJP;
- capitalized-vs-lowercase source conflicts require explicit surface policy;
- a capitalized candidate with a common-noun homonym requires an explicit
  lowercase resolution;
- a capitalized candidate without a common-noun homonym may resolve
  deterministically to capitalized;
- resolved surfaces are emitted for the additive builder to apply to core keys.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from surface_components import component_records
from capitalization_rules import resolve_capitalization


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        lines = (
            line
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        )
        return list(csv.DictReader(lines, delimiter="\t"))


def add_source(
    out: dict[str, list[dict[str, object]]],
    rows: list[dict[str, str]],
    surface_field: str,
    source: str,
    policy_field: str | None = None,
    context_fields: tuple[str, ...] = (),
) -> None:
    for row in rows:
        raw = row.get(surface_field, "").strip()
        if not raw:
            continue
        phrase = raw
        base_policy = (
            row.get(policy_field, "").strip()
            if policy_field
            else (
                "capitalized"
                if raw[:1].isupper()
                else "lowercase"
            )
        )
        if not base_policy:
            continue
        for index, component in component_records(raw):
            key = component.lower()
            # Phrase-level capitalization is not inherited mechanically. A component
            # written lowercase in the official source remains lowercase even when
            # another component of the same phrase starts with a capital letter.
            source_component_policy = (
                "lowercase"
                if base_policy == "lowercase" or component[:1].islower()
                else "capitalized"
            )
            policy = source_component_policy
            candidate = component
            if policy == "lowercase":
                candidate = component.lower()
            elif policy == "capitalized":
                candidate = component[:1].upper() + component[1:]
            out.setdefault(key, []).append(
                {
                    "surface": candidate,
                    "policy": policy,
                    "source": source,
                    "source_phrase": phrase,
                    "component_index": index,
                    "context": {
                        field: row.get(field, "")
                        for field in context_fields
                        if row.get(field, "")
                    },
                }
            )


def load_surface_policy(path: Path) -> dict[str, tuple[str, str]]:
    out: dict[str, tuple[str, str]] = {}
    for row in read_rows(path):
        key = row["surface_key"].strip().lower()
        surface = row["canonical_surface"].strip()
        policy = row["case_policy"].strip()
        if not key or surface.lower() != key:
            raise SystemExit(f"Malformed surface policy key/surface: {row}")
        if policy not in {"lowercase", "capitalized"}:
            raise SystemExit(f"Malformed surface policy case: {row}")
        out[key] = (surface, policy)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--first-name-inflections", type=Path, required=True)
    ap.add_argument("--cities", type=Path, required=True)
    ap.add_argument("--city-inflections", type=Path, required=True)
    ap.add_argument("--terc", type=Path, required=True)
    ap.add_argument("--countries", type=Path, required=True)
    ap.add_argument("--country-inflections", type=Path, required=True)
    ap.add_argument("--capitals", type=Path, required=True)
    ap.add_argument("--capital-inflections", type=Path, required=True)
    ap.add_argument("--custom", type=Path, required=True)
    ap.add_argument("--surface-registry-policy", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    args = ap.parse_args()

    base: dict[str, str] = {}
    for line in args.base.read_text(encoding="utf-8").splitlines():
        value = line.strip()
        if not value or value.startswith("#"):
            continue
        base[value.lower()] = value
    if len(base) != 100000:
        raise SystemExit(f"Immutable core must contain exactly 100000 keys, got {len(base)}")

    first_name_rows = read_rows(args.first_name_inflections)
    selected_first_names = {
        row["name"].strip().lower()
        for row in first_name_rows
        if row.get("name", "").strip()
    }
    evidence: dict[str, list[dict[str, object]]] = {}

    add_source(
        evidence,
        first_name_rows,
        "form",
        "first-name-inflection",
        context_fields=("name", "case"),
    )
    add_source(
        evidence,
        read_rows(args.cities),
        "name",
        "city",
        context_fields=("simc", "stan_na"),
    )
    add_source(
        evidence,
        read_rows(args.city_inflections),
        "form",
        "city-inflection",
        context_fields=("name", "case"),
    )
    add_source(
        evidence,
        read_rows(args.terc),
        "name",
        "terc",
        policy_field="case_policy",
        context_fields=("level", "terc", "nazdod"),
    )
    add_source(
        evidence,
        read_rows(args.countries),
        "name",
        "country",
        policy_field="case_policy",
        context_fields=("official_long_name",),
    )
    add_source(
        evidence,
        read_rows(args.country_inflections),
        "form",
        "country-inflection",
        policy_field="case_policy",
        context_fields=("name", "case"),
    )
    add_source(
        evidence,
        read_rows(args.capitals),
        "name",
        "capital",
        policy_field="case_policy",
        context_fields=("country",),
    )
    add_source(
        evidence,
        read_rows(args.capital_inflections),
        "form",
        "capital-inflection",
        policy_field="case_policy",
        context_fields=("name", "case"),
    )
    add_source(
        evidence,
        read_rows(args.custom),
        "surface",
        "custom-manual",
        policy_field="case_policy",
    )

    explicit = load_surface_policy(args.surface_registry_policy)

    import morfeusz2
    morfeusz = morfeusz2.Morfeusz()

    audited = []
    resolved: dict[str, dict[str, str]] = {}
    unresolved = []

    for key in sorted(set(base) & set(evidence)):
        rows = evidence[key]
        policies = {str(r["policy"]) for r in rows if r["policy"] in {"lowercase", "capitalized"}}
        resolution = resolve_capitalization(
            key=key,
            policies=policies,
            morfeusz=morfeusz,
            explicit_policy=explicit.get(key),
        )
        if not resolution["resolved"]:
            unresolved.append({
                "key": key,
                "reason": resolution["reason"],
                "policies": sorted(policies),
            })
        result_surface = str(resolution["surface"])
        result_policy = str(resolution["policy"])
        reason = str(resolution["reason"])
        audited.append({
            "surface_key": key,
            "core_surface": base[key],
            "resolved_surface": result_surface,
            "resolved_policy": result_policy,
            "surface_changed": result_surface != base[key],
            "reason": reason,
            "source_policies": sorted(policies),
            "sources": sorted({str(r["source"]) for r in rows}),
            "common_lexical_homonym": bool(resolution["common_lexical_matches"]),
            "common_lexical_matches": resolution["common_lexical_matches"],
            "common_adjective_matches": resolution["common_adjective_matches"],
            "common_noun_homonym": bool(resolution["common_noun_matches"]),
            "common_noun_matches": resolution["common_noun_matches"],
            "evidence": rows,
        })
        if resolution["resolved"]:
            resolved[key] = {
                "surface": result_surface,
                "policy": result_policy,
                "reason": reason,
            }

    summary = {
        "mode": "immutable-core-capitalization-audit",
        "core_keys": len(base),
        "core_keys_with_source_capitalization_evidence": len(audited),
        "resolved_core_keys": len(resolved),
        "surface_changes_required": sum(1 for r in audited if r["surface_changed"]),
        "common_lexical_homonym_count": sum(1 for r in audited if r["common_lexical_homonym"]),
        "common_noun_homonym_count": sum(1 for r in audited if r["common_noun_homonym"]),
        "unresolved_count": len(unresolved),
        "unresolved_keys": [r["key"] for r in unresolved],
        "resolved_surfaces": resolved,
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
                "core_surface",
                "resolved_surface",
                "resolved_policy",
                "surface_changed",
                "reason",
                "source_policies",
                "sources",
                "common_noun_homonym",
            ]
        )
        for row in audited:
            writer.writerow(
                [
                    row["surface_key"],
                    row["core_surface"],
                    row["resolved_surface"],
                    row["resolved_policy"],
                    str(row["surface_changed"]).lower(),
                    row["reason"],
                    json.dumps(row["source_policies"], ensure_ascii=False),
                    json.dumps(row["sources"], ensure_ascii=False),
                    str(row["common_noun_homonym"]).lower(),
                ]
            )

    if unresolved:
        print(
            "Unresolved core capitalization collisions: "
            + ", ".join(r["key"] for r in unresolved)
        )
        return 1

    print(json.dumps({
        "core_keys_with_source_capitalization_evidence": len(audited),
        "resolved_core_keys": len(resolved),
        "surface_changes_required": sum(1 for r in audited if r["surface_changed"]),
        "common_noun_homonym_count": sum(1 for r in audited if r["common_noun_homonym"]),
        "unresolved_count": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
