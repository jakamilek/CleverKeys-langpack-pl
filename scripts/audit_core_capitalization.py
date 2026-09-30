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
from capitalization_rules import resolve_capitalization


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        lines = (
            line
            for line in handle
            if line.strip() and not line.lstrip().startswith("#")
        )
        return list(csv.DictReader(lines, delimiter="\t"))


def load_nkjp_capitalization(path: Path) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    """Aggregate valid NKJP1M casing, lemma and SGJP-link evidence.

    NCH is only "not checked" and can hide any other classification, so it is
    never interpreted as a class. Rows marked as spelling/tagging errors are
    excluded before aggregation; accepted rows retain the SGJP-presence
    status, observed lemma casing and explicit classification.
    """
    accepted_correctness = {"CORR", "TAGD", "PLTAN", "TAGE", "DIAL"}
    out: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "forms": Counter(),
            "classes": Counter(),
            "tags": Counter(),
            "lemmas": Counter(),
            "lemma_forms": Counter(),
            "sgjp_status": Counter(),
            "morphology": Counter(),
            "correctness": Counter(),
        }
    )
    by_lemma: dict[str, dict[str, object]] = defaultdict(
        lambda: {
            "forms": Counter(),
            "classes": Counter(),
            "tags": Counter(),
            "lemma_forms": Counter(),
            "sgjp_status": Counter(),
            "morphology": Counter(),
            "correctness": Counter(),
        }
    )
    with path.open(encoding="utf-8", errors="strict") as handle:
        for line in handle:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 8:
                continue
            form = fields[0].strip()
            lemma = fields[1].strip()
            tag = fields[2].strip()
            morphology = fields[4].strip()
            sgjp_status = fields[5].strip()
            classification = fields[6].strip()
            correctness = fields[7].strip()
            if not form or not lemma or not classification:
                continue
            try:
                frequency = int(fields[3])
            except ValueError:
                continue
            if frequency <= 0 or correctness not in accepted_correctness:
                continue

            key = form.lower()
            row = out[key]
            row["forms"][form] += frequency
            row["classes"][classification] += frequency
            row["tags"][tag] += frequency
            row["lemmas"][lemma] += frequency
            row["lemma_forms"][lemma] += frequency
            row["sgjp_status"][sgjp_status] += frequency
            row["morphology"][morphology] += frequency
            row["correctness"][correctness] += frequency

            lemma_key = lemma.lower()
            lemma_row = by_lemma[lemma_key]
            lemma_row["forms"][form] += frequency
            lemma_row["classes"][classification] += frequency
            lemma_row["tags"][tag] += frequency
            lemma_row["lemma_forms"][lemma] += frequency
            lemma_row["sgjp_status"][sgjp_status] += frequency
            lemma_row["morphology"][morphology] += frequency
            lemma_row["correctness"][correctness] += frequency
    return dict(out), dict(by_lemma)

def resolve_nkjp_capitalization(
    key: str,
    record: dict[str, object] | None,
    *,
    basis: str = "surface",
) -> dict[str, object] | None:
    """Resolve a Morfeusz gap from conservative NKJP secondary evidence.

    NCH is only "not checked" and may hide any other classification, so it is
    never interpreted as a class. Explicit classes remain useful. The SGJP
    presence statuses are directional when they explicitly encode the lemma
    capitalization match; otherwise a strict observed lemma-case majority is
    used. PN alone never implies uppercase.
    """
    if not record:
        return None

    normalized = key.lower()
    classes = record.get("classes", Counter())
    forms = record.get("forms", Counter())
    sgjp_status = record.get("sgjp_status", Counter())
    lemma_forms = record.get("lemma_forms", Counter())
    correctness = record.get("correctness", Counter())

    def payload(
        *,
        surface: str,
        policy: str,
        reason: str,
        basis_name: str,
        proper_name_classes: list[str] | None = None,
        casing_source: str,
    ) -> dict[str, object]:
        return {
            "resolved": True,
            "surface": surface,
            "policy": policy,
            "reason": reason,
            "linguistic_basis": basis_name,
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": proper_name_classes or [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(sgjp_status),
            "nkjp_lemma_cases": {
                "capitalized_frequency": sum(
                    int(count) for lemma, count in lemma_forms.items()
                    if str(lemma)[:1].isupper()
                ),
                "lowercase_frequency": sum(
                    int(count) for lemma, count in lemma_forms.items()
                    if str(lemma)[:1].islower()
                ),
                "source": casing_source,
            },
            "nkjp_correctness": sorted(correctness),
        }

    lemma_capital_frequency = sum(
        int(count) for lemma, count in lemma_forms.items()
        if str(lemma)[:1].isupper()
    )
    lemma_lower_frequency = sum(
        int(count) for lemma, count in lemma_forms.items()
        if str(lemma)[:1].islower()
    )

    # Column 6 explicitly records how the NKJP triple matched SGJP. These
    # labels are directional by definition: LMM-CAPITAL means the capitalized
    # lemma spelling matched, while LMM-UNCAPITAL/LMM-LOWER/BTH-LOWER indicate
    # lowercase matching. Use only a strict direction; mixed evidence stays
    # unresolved until lemma casing breaks the tie.
    capital_status_frequency = int(sgjp_status.get("SGJP-LMM-CAPITAL", 0))
    lowercase_status_frequency = sum(
        int(sgjp_status.get(status, 0))
        for status in {
            "SGJP-LMM-UNCAPITAL",
            "SGJP-LMM-LOWER",
            "SGJP-BTH-LOWER",
        }
    )

    if capital_status_frequency > 0 and capital_status_frequency > lowercase_status_frequency:
        return payload(
            surface=normalized[:1].upper() + normalized[1:],
            policy="capitalized",
            reason=(
                "nkjp-sgjp-explicit-capitalization-fallback"
                if basis == "surface"
                else "nkjp-sgjp-explicit-capitalization-lemma-linked-fallback"
            ),
            basis_name=(
                "nkjp-sgjp-explicit-casing"
                if basis == "surface"
                else "nkjp-sgjp-explicit-casing-lemma"
            ),
            proper_name_classes=sorted(
                value for value in classes if value in {"PN", "ACRO", "WEB"}
            ),
            casing_source="sgjp-directional-match",
        )

    if lowercase_status_frequency > 0 and lowercase_status_frequency > capital_status_frequency:
        return payload(
            surface=normalized,
            policy="lowercase",
            reason=(
                "nkjp-sgjp-explicit-lowercase-fallback"
                if basis == "surface"
                else "nkjp-sgjp-explicit-lowercase-lemma-linked-fallback"
            ),
            basis_name=(
                "nkjp-sgjp-explicit-casing"
                if basis == "surface"
                else "nkjp-sgjp-explicit-casing-lemma"
            ),
            casing_source="sgjp-directional-match",
        )

    # Explicit common/lexical classifications remain useful, but they are
    # consulted only after SGJP's directional casing signal and never override
    # the primary Morfeusz common-noun rule (which ran earlier).
    if classes.get("CW", 0) > 0:
        return payload(
            surface=normalized,
            policy="lowercase",
            reason=(
                "nkjp-common-word-lowercase-fallback"
                if basis == "surface"
                else "nkjp-common-word-lemma-lowercase-fallback"
            ),
            basis_name=(
                "nkjp-common-word"
                if basis == "surface"
                else "nkjp-common-word-lemma"
            ),
            casing_source="explicit-classification",
        )

    proper_classes = {"PN", "ACRO", "WEB"}
    observed_proper = sorted(value for value in classes if value in proper_classes)
    if observed_proper:
        # PN is not synonymous with uppercase. Only use a strict observed
        # surface-case direction after SGJP directional evidence has failed.
        lowercase_frequency = sum(
            int(count) for form, count in forms.items()
            if str(form)[:1].islower()
        )
        uppercase_frequency = sum(
            int(count) for form, count in forms.items()
            if str(form)[:1].isupper()
        )
        if uppercase_frequency > 0 and uppercase_frequency > lowercase_frequency:
            return payload(
                surface=normalized[:1].upper() + normalized[1:],
                policy="capitalized",
                reason=(
                    "nkjp-proper-name-observed-casing-fallback"
                    if basis == "surface"
                    else "nkjp-proper-name-lemma-observed-casing-fallback"
                ),
                basis_name=(
                    "nkjp-proper-name"
                    if basis == "surface"
                    else "nkjp-proper-name-lemma"
                ),
                proper_name_classes=observed_proper,
                casing_source="explicit-classification-plus-surface-casing",
            )
        if lowercase_frequency > 0 and lowercase_frequency > uppercase_frequency:
            return payload(
                surface=normalized,
                policy="lowercase",
                reason=(
                    "nkjp-proper-name-lowercase-observed-fallback"
                    if basis == "surface"
                    else "nkjp-proper-name-lemma-lowercase-observed-fallback"
                ),
                basis_name=(
                    "nkjp-proper-name"
                    if basis == "surface"
                    else "nkjp-proper-name-lemma"
                ),
                proper_name_classes=observed_proper,
                casing_source="explicit-classification-plus-surface-casing",
            )

    lexical_classes = {"SPEC", "NEOL", "EXT", "SYMB", "COMPD"}
    if any(classes.get(value, 0) > 0 for value in lexical_classes):
        return payload(
            surface=normalized,
            policy="lowercase",
            reason=(
                "nkjp-lexical-lowercase-fallback"
                if basis == "surface"
                else "nkjp-lexical-lemma-lowercase-fallback"
            ),
            basis_name=(
                "nkjp-lexical"
                if basis == "surface"
                else "nkjp-lexical-lemma"
            ),
            casing_source="explicit-classification",
        )

    # SGJP-EXACT only confirms exact presence. When no directional LMM status
    # exists, use a strict observed lemma-case majority as independent evidence.
    if lemma_capital_frequency > 0 and lemma_capital_frequency > lemma_lower_frequency:
        return payload(
            surface=normalized[:1].upper() + normalized[1:],
            policy="capitalized",
            reason=(
                "nkjp-observed-lemma-capitalization-fallback"
                if basis == "surface"
                else "nkjp-observed-lemma-capitalization-lemma-fallback"
            ),
            basis_name=(
                "nkjp-lemma-casing"
                if basis == "surface"
                else "nkjp-lemma-casing-linked"
            ),
            casing_source="observed-lemma-casing",
        )

    if lemma_lower_frequency > 0 and lemma_lower_frequency > lemma_capital_frequency:
        return payload(
            surface=normalized,
            policy="lowercase",
            reason=(
                "nkjp-observed-lemma-lowercase-fallback"
                if basis == "surface"
                else "nkjp-observed-lemma-lowercase-lemma-fallback"
            ),
            basis_name=(
                "nkjp-lemma-casing"
                if basis == "surface"
                else "nkjp-lemma-casing-linked"
            ),
            casing_source="observed-lemma-casing",
        )

    return None

def resolve_nkjp_lemma_capitalization(
    key: str,
    surface_record: dict[str, object] | None,
    by_lemma: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    """Resolve via lemmas linked to the exact NKJP surface.

    The lemma index is keyed by lemma, not by inflected surface. Therefore an
    unresolved form such as "batmana" must first use the exact-surface record
    to discover its observed lemma ("batman"), and only then consult the
    aggregated lemma evidence.
    """
    if not surface_record:
        return None

    lemmas = surface_record.get("lemmas", {})
    if not isinstance(lemmas, Counter):
        return None

    candidates = sorted(
        (
            (str(lemma).strip().lower(), int(frequency))
            for lemma, frequency in lemmas.items()
            if str(lemma).strip() and int(frequency) > 0
        ),
        key=lambda item: (-item[1], item[0]),
    )
    for lemma, frequency in candidates:
        resolution = resolve_nkjp_capitalization(
            key,
            by_lemma.get(lemma),
            basis="lemma",
        )
        if resolution is None:
            continue
        return {
            **resolution,
            "nkjp_linked_lemma": lemma,
            "nkjp_lemma_link_frequency": frequency,
        }
    return None

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
        rows = evidence.get(key, [])
        policies = {str(r["policy"]) for r in rows if r["policy"] in {"lowercase", "capitalized"}}
        proper_lemmas = {
            lemma
            for row in rows
            for lemma in row.get("proper_lemma_keys", [])
        }
        # CORE AUTHORITY: module capitalization policies and module lemma lineage
        # are verification evidence only. They must never decide a core surface.
        resolution = resolve_capitalization(
            key=key,
            policies=(),
            morfeusz=morfeusz,
            explicit_policy=explicit.get(key),
            proper_lemma_keys=(),
        )
        if not resolution["resolved"]:
            nkjp_resolution = resolve_nkjp_capitalization(
                key, nkjp.get(key), basis="surface"
            )
            if nkjp_resolution is None:
                nkjp_resolution = resolve_nkjp_lemma_capitalization(
                    key,
                    nkjp.get(key),
                    nkjp_lemmas,
                )
            if nkjp_resolution is None:
                # Preserve direct lemma-key coverage for base forms that have
                # lemma evidence even when no exact-surface record is available.
                nkjp_resolution = resolve_nkjp_capitalization(
                    key,
                    nkjp_lemmas.get(key),
                    basis="lemma",
                )
            if nkjp_resolution is not None:
                resolution = {**resolution, **nkjp_resolution}

        resolved_policy = (
            str(resolution["policy"])
            if resolution["resolved"]
            else None
        )
        module_verification = {
            "present": bool(rows),
            "policies": sorted(policies),
            "sources": sorted({str(r["source"]) for r in rows}),
            "agrees_with_linguistic_decision": (
                not policies
                or resolved_policy is None
                or policies == {resolved_policy}
            ),
            "conflict": bool(
                policies
                and resolved_policy is not None
                and policies != {resolved_policy}
            ),
            "status": (
                "no-module-evidence"
                if not rows
                else (
                    "agree"
                    if not policies or (
                        resolved_policy is not None
                        and policies == {resolved_policy}
                    )
                    else "module-vs-oracle-conflict"
                )
            ),
        }
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
        "core_keys_with_nkjp_proper_name_evidence": sum(
            1 for r in audited
            if r["linguistic_basis"] in {"nkjp-proper-name", "nkjp-proper-name-lemma"}
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
        "surface_changes_required": sum(1 for r in audited if r["surface_changed"]),
        "common_lexical_homonym_count": sum(1 for r in audited if r["common_lexical_homonym"]),
        "common_noun_homonym_count": sum(1 for r in audited if r["common_noun_homonym"]),
        "module_verification_conflict_count": len(module_conflicts),
        "module_verification_conflict_keys": module_conflicts,
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

        # Compact source diagnostic for the next audit iteration. This is
        # deliberately read-only: it never changes a resolution or membership.
        # A small sample is enough to determine whether the remaining gaps are
        # missing NKJP surface rows, mixed/uncased lemmas, or unusable SGJP links.
        diagnostic_keys = [
            row["key"] for row in unresolved[:25]
        ]
        print("NKJP unresolved diagnostics:")
        for diagnostic_key in diagnostic_keys:
            record = nkjp.get(diagnostic_key)
            if record is None:
                print(f"  {diagnostic_key}: surface=NONE")
                continue
            lemmas = record.get("lemmas", Counter())
            linked = []
            if isinstance(lemmas, Counter):
                candidates = sorted(
                    (
                        (str(lemma).lower(), int(freq))
                        for lemma, freq in lemmas.items()
                        if str(lemma).strip() and int(freq) > 0
                    ),
                    key=lambda item: (-item[1], item[0]),
                )[:3]
                for lemma, link_frequency in candidates:
                    linked_record = nkjp_lemmas.get(lemma)
                    linked.append({
                        "lemma": lemma,
                        "surface_link_frequency": link_frequency,
                        "record": (
                            None
                            if linked_record is None
                            else {
                                "forms": dict(linked_record.get("forms", {})),
                                "classes": dict(linked_record.get("classes", {})),
                                "sgjp_status": dict(linked_record.get("sgjp_status", {})),
                                "lemma_forms": dict(linked_record.get("lemma_forms", {})),
                                "correctness": dict(linked_record.get("correctness", {})),
                            }
                        ),
                    })
            print(json.dumps({
                "key": diagnostic_key,
                "surface": {
                    "forms": dict(record.get("forms", {})),
                    "classes": dict(record.get("classes", {})),
                    "sgjp_status": dict(record.get("sgjp_status", {})),
                    "lemmas": dict(record.get("lemmas", {})),
                    "lemma_forms": dict(record.get("lemma_forms", {})),
                    "correctness": dict(record.get("correctness", {})),
                },
                "linked_lemmas": linked,
            }, ensure_ascii=False, sort_keys=True))

        return 1

    print(json.dumps({
        "core_keys_audited": len(audited),
        "authority": "independent-linguistic-oracle",
        "core_keys_with_source_capitalization_evidence": sum(1 for r in audited if r["source_evidence_present"]),
        "core_keys_without_source_capitalization_evidence": sum(1 for r in audited if not r["source_evidence_present"]),
        "core_keys_with_linguistic_proper_name_evidence": sum(1 for r in audited if r["linguistic_basis"] == "proper-name"),
        "core_keys_with_no_linguistic_evidence": sum(1 for r in audited if r["linguistic_basis"] == "unresolved"),
        "resolved_core_keys": len(resolved),
        "surface_changes_required": sum(1 for r in audited if r["surface_changed"]),
        "module_verification_conflict_count": len(module_conflicts),
        "unresolved_count": 0,
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
