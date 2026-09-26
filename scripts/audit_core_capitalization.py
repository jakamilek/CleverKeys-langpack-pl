#!/usr/bin/env python3
"""Audit and resolve capitalization of immutable-core keys using source evidence.

The immutable 100k membership is never changed here. Only the canonical surface
(casing) may be corrected for a core key, based on independently retained source
evidence. This audit runs before module assembly.

Rules:
- source evidence is collected from all active module/source layers, including
  multi-component names;
- capitalization is never inferred from 100k membership;
- a capitalized source candidate is checked independently for a common-noun
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
    special_policy: dict[str, str] | None = None,
    context_fields: tuple[str, ...] = (),
) -> None:
    special_policy = special_policy or {}
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
            policy = special_policy.get(key, source_component_policy)
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


def common_lexical_matches(morfeusz, surface: str) -> list[dict[str, object]]:
    matches = []
    ordinary_pos = {"subst", "adj", "adv", "verb", "part", "prep", "conj", "num", "ger", "ppron", "pron"}
    for item in morfeusz.analyse(surface.lower()):
        if len(item) < 3:
            continue
        payload = item[2]
        if not isinstance(payload, (tuple, list)) or len(payload) < 4:
            continue
        orth, lemma, tag = str(payload[0]), str(payload[1]), str(payload[2])
        classes = payload[3] if isinstance(payload[3], (tuple, list)) else []
        classes = [str(x) for x in classes]
        pos = tag.split(":", 1)[0]
        proper_classes = [cls for cls in classes if cls.startswith("nazwa_") and cls != "nazwa_pospolita"]
        if pos in ordinary_pos and not proper_classes:
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
    ap.add_argument("--base", type=Path, required=True)
    ap.add_argument("--first-name-inflections", type=Path, required=True)
    ap.add_argument("--first-name-surface-policy", type=Path, required=True)
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

    name_policy = {
        row["name"].strip().lower(): row["policy"].strip()
        for row in read_rows(args.first_name_surface_policy)
    }
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
        special_policy=name_policy,
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
        capitalized_rows = [r for r in rows if r["policy"] == "capitalized"]
        noun_matches = common_lexical_matches(morfeusz, key) if capitalized_rows else []
        override = explicit.get(key)

        result_surface = base[key]
        result_policy = "lowercase"
        reason = "core-default"

        if override is not None:
            result_surface, result_policy = override
            reason = "explicit-surface-registry-policy"
            if result_surface.lower() != key:
                unresolved.append({
                    "key": key,
                    "reason": "explicit-policy-key-mismatch",
                })
        elif capitalized_rows:
            if key in name_policy and name_policy[key] == "lowercase_common_noun":
                result_surface = key
                result_policy = "lowercase"
                reason = "explicit-first-name-lowercase-policy"
            elif (
                any(r["source"] == "first-name-inflection" for r in rows)
                and policies == {"capitalized"}
            ):
                # Selected first-name surfaces are explicitly audited as name forms.
                # A common-noun analysis must not erase that capitalization; only an
                # explicit lowercase name policy or a cross-source policy conflict can.
                result_surface = key[:1].upper() + key[1:]
                result_policy = "capitalized"
                reason = "first-name-category-capitalized-policy"
            elif any("nazwa_pospolita" in m.get("classes", []) for m in noun_matches):
                # Only a verified common-noun reading overrides a proper-name surface.
                # Other ordinary lexical analyses are not enough to erase capitalization
                # in the word-oriented CKDT.
                result_surface = key
                result_policy = "lowercase"
                reason = "common-lexical-homonym-default-lowercase"
            elif policies == {"lowercase"}:
                result_surface = key
                result_policy = "lowercase"
                reason = "lowercase-source-evidence"
            elif len(policies) > 1:
                # Mixed evidence without lexical evidence is a genuine ambiguity and
                # must remain auditable instead of being silently guessed.
                unresolved.append({
                    "key": key,
                    "reason": "mixed-source-capitalization-policy-without-explicit-resolution",
                    "policies": sorted(policies),
                })
                result_surface = base[key]
                result_policy = "lowercase"
                reason = "unresolved-mixed-policy"
            else:
                result_surface = key[:1].upper() + key[1:]
                result_policy = "capitalized"
                reason = "capitalized-source-without-common-lexical-homonym"
        elif policies == {"lowercase"}:
            result_surface = key
            result_policy = "lowercase"
            reason = "lowercase-source-evidence"

        changed = result_surface != base[key]
        audited.append({
            "surface_key": key,
            "core_surface": base[key],
            "resolved_surface": result_surface,
            "resolved_policy": result_policy,
            "surface_changed": changed,
            "reason": reason,
            "source_policies": sorted(policies),
            "sources": sorted({str(r["source"]) for r in rows}),
            "common_lexical_homonym": bool(noun_matches),
            "common_lexical_matches": noun_matches,
            "common_noun_homonym": any("nazwa_pospolita" in m.get("classes", []) for m in noun_matches),
            "common_noun_matches": [m for m in noun_matches if "nazwa_pospolita" in m.get("classes", [])],
            "evidence": rows,
        })
        if not any(item.get("key") == key for item in unresolved):
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
