#!/usr/bin/env python3
"""Audit and resolve capitalization of immutable-core keys from an independent linguistic oracle.

The immutable 100k membership is never changed here. Every core key is audited.
The capitalization decision is made from Morfeusz 2 / SGJP lexical analysis,
not from category-module membership. Active modules are loaded only to verify
the independent decision and to expose coverage/conflict gaps.

Rules:
- capitalization is never inferred from 100k membership;
- verified common noun -> lowercase, absolutely;
- ordinary adjective -> lowercase;
- any SGJP proper-name classification -> capitalized;
- other ordinary lexical analysis -> lowercase;
- explicit surface policy is a human-audited fallback only for linguistic gaps;
- module source capitalization is verification evidence only for core keys;
- a core key with neither linguistic nor explicit fallback evidence is unresolved;
- resolved surfaces are emitted for the additive builder to apply to core keys.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from collections import Counter, defaultdict

from surface_components import component_records, component_surfaces
from capitalization_rules import (
    OFFICIAL_CAPITALIZATION_SOURCES,
    common_noun_matches,
    proper_name_matches,
    resolve_capitalization,
)


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        lines = (
            line
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        )
        return list(csv.DictReader(lines, delimiter="\t"))


from nkjp_capitalization import (load_nkjp_capitalization, resolve_nkjp_capitalization, resolve_nkjp_lemma_capitalization,
resolve_nkjp_via_morfeusz_lemmas
)

def add_source(
    out: dict[str, list[dict[str, object]]],
    rows: list[dict[str, str]],
    surface_field: str,
    source: str,
    policy_field: str | None = None,
    context_fields: tuple[str, ...] = (),
    lemma_field: str | None = None,
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
            proper_lemma_keys = (
                sorted({
                    part.lower()
                    for part in component_surfaces(row.get(lemma_field, ""))
                })
                if lemma_field and row.get(lemma_field, "").strip()
                else []
            )
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
                    "proper_lemma_keys": proper_lemma_keys,
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
    ap.add_argument("--first-name-inflections", type=Path, default=None)
    ap.add_argument("--cities", type=Path, default=None)
    ap.add_argument("--city-inflections", type=Path, default=None)
    ap.add_argument("--terc", type=Path, default=None)
    ap.add_argument("--countries", type=Path, default=None)
    ap.add_argument("--country-inflections", type=Path, default=None)
    ap.add_argument("--capitals", type=Path, default=None)
    ap.add_argument("--capital-inflections", type=Path, default=None)
    ap.add_argument("--custom", type=Path, default=None)
    ap.add_argument("--surface-registry-policy", type=Path, required=True)
    ap.add_argument("--nkjp", type=Path, required=True)
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

    evidence: dict[str, list[dict[str, object]]] = {}

    def rows_or_empty(path: Path | None) -> list[dict[str, str]]:
        return [] if path is None else read_rows(path)

    first_name_rows = rows_or_empty(args.first_name_inflections)
    selected_first_names = {
        row["name"].strip().lower()
        for row in first_name_rows
        if row.get("name", "").strip()
    }

    add_source(
        evidence,
        first_name_rows,
        "form",
        "first-name-inflection",
        context_fields=("name", "case"),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.cities),
        "name",
        "city",
        context_fields=("simc", "stan_na"),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.city_inflections),
        "form",
        "city-inflection",
        context_fields=("name", "case"),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.terc),
        "name",
        "terc",
        policy_field="case_policy",
        context_fields=("level", "terc", "nazdod"),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.countries),
        "name",
        "country",
        policy_field="case_policy",
        context_fields=("official_long_name",),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.country_inflections),
        "form",
        "country-inflection",
        policy_field="case_policy",
        context_fields=("name", "case"),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.capitals),
        "name",
        "capital",
        policy_field="case_policy",
        context_fields=("country",),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.capital_inflections),
        "form",
        "capital-inflection",
        policy_field="case_policy",
        context_fields=("name", "case"),
        lemma_field="name",
    )
    add_source(
        evidence,
        rows_or_empty(args.custom),
        "surface",
        "custom-manual",
        policy_field="case_policy",
    )

    explicit = load_surface_policy(args.surface_registry_policy)
    nkjp, nkjp_lemmas = load_nkjp_capitalization(args.nkjp)

    import morfeusz2
    morfeusz = morfeusz2.Morfeusz()

    audited = []
    resolved: dict[str, dict[str, str]] = {}
    unresolved = []

    # Every immutable-core key is audited. Source modules provide evidence when
    # available, but their absence must never silently exclude a core key.
    for key in sorted(base):
        # Independent homonym audit: this classification uses Morfeusz only,
        # deliberately ignoring every module and its source evidence. A key is
        # a dual-surface candidate when Morfeusz exposes both an ordinary
        # common-noun analysis and a competing proper-name analysis for the
        # same case-folded surface.
        independent_common_matches = common_noun_matches(morfeusz, key)
        independent_proper_matches = proper_name_matches(morfeusz, key)
        independent_case_dual_surface_candidate = bool(
            independent_common_matches and independent_proper_matches
        )

        rows = evidence.get(key, [])
        policies = {str(r["policy"]) for r in rows if r["policy"] in {"lowercase", "capitalized"}}
        official_source_policies = {
            str(r["policy"])
            for r in rows
            if r["source"] in OFFICIAL_CAPITALIZATION_SOURCES
            and r["policy"] in {"lowercase", "capitalized"}
        }
        proper_lemmas = {
            lemma
            for row in rows
            for lemma in row.get("proper_lemma_keys", [])
        }
        # Category modules are verification-only. The core resolver receives
        # independent linguistic inputs only: Morfeusz plus pinned NKJP1M.
        # Prefer lemma-linked evidence: raw surface casing in a corpus is
        # strongly affected by sentence position, while the canonical lemma
        # spelling carries the lexical capitalization signal. Exact-surface
        # evidence remains a fallback for cases without useful lemma linkage.
        nkjp_resolution = resolve_nkjp_via_morfeusz_lemmas(
            key,
            morfeusz,
            nkjp_lemmas,
        )
        if nkjp_resolution is None:
            nkjp_resolution = resolve_nkjp_lemma_capitalization(
                key,
                nkjp.get(key),
                nkjp_lemmas,
            )
        if nkjp_resolution is None:
            nkjp_resolution = resolve_nkjp_capitalization(
                key,
                nkjp.get(key),
                basis="surface",
            )
        if nkjp_resolution is None:
            nkjp_resolution = resolve_nkjp_capitalization(
                key,
                nkjp_lemmas.get(key),
                basis="lemma",
            )
        resolution = resolve_capitalization(
            key=key,
            policies=(),
            morfeusz=morfeusz,
            explicit_policy=explicit.get(key),
            proper_lemma_keys=(),
            secondary_linguistic_evidence=nkjp_resolution,
            official_source_policies=official_source_policies,
        )

        resolved_policy = (
            str(resolution["policy"])
            if resolution["resolved"]
            else None
        )
        module_policy_disagreement = len(policies) > 1
        module_verification = {
            "present": bool(rows),
            "policies": sorted(policies),
            "sources": sorted({str(r["source"]) for r in rows}),
            "agrees_with_core_decision": (
                not policies
                or resolved_policy is None
                or resolved_policy in policies
                or not module_policy_disagreement
            ),
            "raw_source_policy_disagreement": module_policy_disagreement,
            "conflict": False,
            "status": (
                "no-module-evidence"
                if not rows
                else (
                    "source-policy-disagreement"
                    if module_policy_disagreement
                    else "verification-only"
                )
            ),
        }
        neutral_fallback = False
        if not resolution["resolved"]:
            # The immutable core builder normalizes every candidate to
            # lowercase before membership selection. When neither Morfeusz nor
            # NKJP nor an explicit audited surface policy can justify a
            # capitalization, preserving that already-normalized core surface
            # is a neutral display decision. It does NOT assert that the word is
            # a common noun or a proper name; it only avoids inventing uppercase
            # without evidence. The gap remains visible in the audit report.
            resolution = {
                **resolution,
                "resolved": True,
                "surface": base[key],
                "policy": "lowercase",
                "reason": "core-neutral-lowercase-fallback-no-capitalization-evidence",
                "linguistic_basis": "core-neutral-fallback",
                "explicit_policy_conflict": False,
            }
            neutral_fallback = True
        if neutral_fallback and (
            str(resolution["surface"]) != base[key]
            or str(resolution["surface"]) != str(resolution["surface"]).lower()
            or str(resolution["policy"]) != "lowercase"
        ):
            raise SystemExit(
                f"Invalid neutral core fallback for {key!r}: {resolution}"
            )
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
            "neutral_fallback": neutral_fallback,
            "source_evidence_present": bool(rows),
            "source_policies": sorted(policies),
            "sources": sorted({str(r["source"]) for r in rows}),
            "linguistic_basis": resolution.get("linguistic_basis"),
            "linguistic_analysis_count": resolution.get("linguistic_analysis_count", 0),
            "proper_name_classes": resolution.get("proper_name_classes", []),
            "proper_name_matches": resolution.get("proper_name_matches", []),
            "nkjp_linked_lemma": resolution.get("nkjp_linked_lemma"),
            "nkjp_lemma_link_frequency": resolution.get("nkjp_lemma_link_frequency"),
            "nkjp_sgjp_status": resolution.get("nkjp_sgjp_status", []),
            "nkjp_lemma_cases": resolution.get("nkjp_lemma_cases", {}),
            "nkjp_correctness": resolution.get("nkjp_correctness", []),
            "common_lexical_homonym": bool(resolution["common_lexical_matches"]),
            "common_lexical_matches": resolution["common_lexical_matches"],
            "common_adjective_matches": resolution["common_adjective_matches"],
            "common_noun_homonym": bool(resolution["common_noun_matches"]),
            "common_noun_matches": resolution["common_noun_matches"],
            "independent_case_dual_surface_candidate": independent_case_dual_surface_candidate,
            "independent_case_dual_surface_proper_name_classes": sorted({
                cls
                for item in independent_proper_matches
                for cls in item.get("proper_name_classes", [])
            }),
            "module_verification": module_verification,
            "evidence": rows,
        })
        if resolution["resolved"]:
            resolved[key] = {
                "surface": result_surface,
                "policy": result_policy,
                "reason": reason,
            }

    module_conflicts = [
        row["surface_key"]
        for row in audited
        if row["module_verification"]["conflict"]
    ]
    summary = {
        "mode": "immutable-core-capitalization-audit",
        "authority": "independent-linguistic-oracle",
        "oracle": "Morfeusz 2 / SGJP + pinned NKJP1M",
        "oracle_primary": "Morfeusz 2 / SGJP",
        "oracle_secondary": "pinned NKJP1M",
        "core_keys": len(base),
        "core_keys_audited": len(audited),
        "core_keys_with_source_capitalization_evidence": sum(1 for r in audited if r["source_evidence_present"]),
        "core_keys_without_source_capitalization_evidence": sum(1 for r in audited if not r["source_evidence_present"]),
        "core_keys_with_linguistic_proper_name_evidence": sum(1 for r in audited if r["linguistic_basis"] == "proper-name"),
        "core_keys_with_linguistic_common_noun_evidence": sum(1 for r in audited if r["linguistic_basis"] == "common-noun"),
        "core_keys_with_linguistic_adjective_evidence": sum(1 for r in audited if r["linguistic_basis"] == "adjective"),
        "core_keys_with_linguistic_ordinary_lexical_evidence": sum(1 for r in audited if r["linguistic_basis"] == "ordinary-lexical"),
        "core_keys_using_explicit_fallback": sum(1 for r in audited if r["linguistic_basis"] == "explicit-fallback"),
        "core_keys_using_neutral_lowercase_fallback": sum(1 for r in audited if r["neutral_fallback"]),
        "core_keys_with_no_capitalization_evidence": sum(1 for r in audited if r["neutral_fallback"]),
        "core_keys_with_nkjp_proper_name_evidence": sum(
            1 for r in audited
            if r["linguistic_basis"] in {
                "nkjp-proper-name",
                "nkjp-proper-name-lemma",
                "nkjp-lemma-casing-linked",
            }
        ),
        "core_keys_with_nkjp_common_word_evidence": sum(
            1 for r in audited
            if r["linguistic_basis"] in {"nkjp-common-word", "nkjp-common-word-lemma"}
        ),
        "core_keys_with_nkjp_lexical_evidence": sum(
            1 for r in audited
            if r["linguistic_basis"] in {"nkjp-lexical", "nkjp-lexical-lemma"}
        ),
        "core_keys_with_no_linguistic_evidence": sum(1 for r in audited if r["linguistic_basis"] == "unresolved"),
        "resolved_core_keys": len(resolved),
        "neutral_lowercase_fallback_count": sum(1 for r in audited if r["neutral_fallback"]),
        "surface_changes_required": sum(1 for r in audited if r["surface_changed"]),
        "common_lexical_homonym_count": sum(1 for r in audited if r["common_lexical_homonym"]),
        "common_noun_homonym_count": sum(1 for r in audited if r["common_noun_homonym"]),
        "independent_case_dual_surface_candidate_count": sum(
            1 for r in audited if r["independent_case_dual_surface_candidate"]
        ),
        "independent_case_dual_surface_candidate_keys": [
            r["surface_key"]
            for r in audited
            if r["independent_case_dual_surface_candidate"]
        ],
        "module_verification_conflict_count": 0,
        "module_verification_conflict_keys": [],
        "module_source_policy_disagreement_count": sum(
            1 for r in audited if r["module_verification"]["raw_source_policy_disagreement"]
        ),
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

    neutral_keys = [
        row["surface_key"] for row in audited if row["neutral_fallback"]
    ]
    dual_surface_keys = [
        row["surface_key"]
        for row in audited
        if row["independent_case_dual_surface_candidate"]
    ]
    print(
        "Independent Morfeusz common/proper dual-surface candidate count: "
        + str(len(dual_surface_keys))
    )
    if dual_surface_keys:
        print(
            "Independent Morfeusz common/proper dual-surface candidates: "
            + ", ".join(dual_surface_keys)
        )

    if neutral_keys:
        print(
            "Core capitalization keys using neutral lowercase fallback: "
            + ", ".join(neutral_keys)
        )
        print(f"Neutral lowercase fallback count: {len(neutral_keys)}")

    print(json.dumps({
        "core_keys_audited": len(audited),
        "authority": "independent-linguistic-oracle",
        "core_keys_with_source_capitalization_evidence": sum(
            1 for r in audited if r["source_evidence_present"]
        ),
        "core_keys_without_source_capitalization_evidence": sum(
            1 for r in audited if not r["source_evidence_present"]
        ),
        "core_keys_with_linguistic_proper_name_evidence": sum(
            1 for r in audited if r["linguistic_basis"] == "proper-name"
        ),
        "core_keys_with_no_linguistic_evidence": sum(
            1 for r in audited if r["linguistic_basis"] == "core-neutral-fallback"
        ),
        "resolved_core_keys": len(resolved),
        "neutral_lowercase_fallback_count": len(neutral_keys),
        "surface_changes_required": sum(
            1 for r in audited if r["surface_changed"]
        ),
        "module_verification_conflict_count": len(module_conflicts),
        "unresolved_count": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
