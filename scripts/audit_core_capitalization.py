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
    """Aggregate pinned NKJP1M casing, lemma and SGJP-link evidence.

    NKJP classification NCH is intentionally not treated as a class decision:
    the source documents it as an automatic "not checked" label that may hide
    any other classification. The useful secondary casing evidence is kept
    from the SGJP-presence column (column 6), observed lemma casing and
    correctness (column 8), while Morfeusz remains the primary oracle.
    """
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
            if frequency <= 0:
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

    Important source constraint: NCH is only "not checked" and can represent
    any other classification, so NCH is never interpreted as lowercase or as
    proper-name evidence. Instead, this resolver uses:
    - explicit NKJP classes when present;
    - SGJP-presence casing statuses from column 6;
    - observed lemma casing when SGJP says the triple is present.

    The absolute common-noun rule has already run in Morfeusz and therefore
    cannot be overridden here.
    """
    if not record:
        return None

    normalized = key.lower()
    classes = record["classes"]
    forms = record["forms"]
    correctness = record.get("correctness", Counter())
    valid_correctness = {
        value for value, count in correctness.items()
        if int(count) > 0 and value in {"CORR", "TAGD", "PLTAN", "TAGE", "DIAL"}
    }
    if correctness and not valid_correctness:
        return None

    def valid_frequency(counter: Counter) -> int:
        if not counter:
            return 0
        return sum(
            int(count)
            for value, count in counter.items()
            if not correctness or value in valid_correctness
        )

    # The tagged table explicitly identifies CW / PN / ACRO / WEB / lexical
    # classes. NCH is intentionally neutral.
    if classes.get("CW", 0) > 0:
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": (
                "nkjp-common-word-lowercase-fallback"
                if basis == "surface"
                else "nkjp-common-word-lemma-lowercase-fallback"
            ),
            "linguistic_basis": (
                "nkjp-common-word" if basis == "surface" else "nkjp-common-word-lemma"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(record.get("sgjp_status", {})),
            "nkjp_lemma_cases": {},
            "nkjp_correctness": sorted(record.get("correctness", {})),
        }

    proper_classes = {"PN", "ACRO", "WEB"}
    if any(classes.get(value, 0) > 0 for value in proper_classes):
        lowercase_frequency = sum(
            int(count) for form, count in forms.items()
            if str(form)[:1].islower()
        )
        uppercase_frequency = sum(
            int(count) for form, count in forms.items()
            if str(form)[:1].isupper()
        )
        if uppercase_frequency > 0 and uppercase_frequency >= lowercase_frequency:
            surface = normalized[:1].upper() + normalized[1:]
            policy = "capitalized"
            reason = (
                "nkjp-proper-name-observed-casing-fallback"
                if basis == "surface"
                else "nkjp-proper-name-lemma-observed-casing-fallback"
            )
        elif lowercase_frequency > 0:
            surface = normalized
            policy = "lowercase"
            reason = (
                "nkjp-proper-name-lowercase-observed-fallback"
                if basis == "surface"
                else "nkjp-proper-name-lemma-lowercase-observed-fallback"
            )
        else:
            return None
        return {
            "resolved": True,
            "surface": surface,
            "policy": policy,
            "reason": reason,
            "linguistic_basis": (
                "nkjp-proper-name" if basis == "surface" else "nkjp-proper-name-lemma"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": sorted(
                value for value in classes if value in proper_classes
            ),
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(record.get("sgjp_status", {})),
            "nkjp_lemma_cases": {},
            "nkjp_correctness": sorted(record.get("correctness", {})),
        }

    lexical_classes = {"SPEC", "NEOL", "EXT", "SYMB", "COMPD"}
    if any(classes.get(value, 0) > 0 for value in lexical_classes):
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": (
                "nkjp-lexical-lowercase-fallback"
                if basis == "surface"
                else "nkjp-lexical-lemma-lowercase-fallback"
            ),
            "linguistic_basis": (
                "nkjp-lexical" if basis == "surface" else "nkjp-lexical-lemma"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(record.get("sgjp_status", {})),
            "nkjp_lemma_cases": {},
            "nkjp_correctness": sorted(record.get("correctness", {})),
        }

    # SGJP-presence status is an explicit secondary casing signal. These
    # statuses are directional by definition: LMM-CAPITAL points to a
    # capitalized lemma in SGJP; LMM-UNCAPITAL/LMM-LOWER/BTH-LOWER point to a
    # lowercase lemma. NCH is deliberately ignored here.
    sgjp_status = record.get("sgjp_status", Counter())
    capital_statuses = {
        "SGJP-LMM-CAPITAL",
    }
    lowercase_statuses = {
        "SGJP-LMM-UNCAPITAL",
        "SGJP-LMM-LOWER",
        "SGJP-BTH-LOWER",
    }
    capital_frequency = sum(
        int(sgjp_status.get(status, 0))
        for status in capital_statuses
    )
    lowercase_frequency = sum(
        int(sgjp_status.get(status, 0))
        for status in lowercase_statuses
    )

    lemma_forms = record.get("lemma_forms", Counter())
    lemma_capital_frequency = sum(
        int(count)
        for lemma, count in lemma_forms.items()
        if str(lemma)[:1].isupper()
    )
    lemma_lower_frequency = sum(
        int(count)
        for lemma, count in lemma_forms.items()
        if str(lemma)[:1].islower()
    )

    # Use SGJP status first. Observed lemma casing is a tiebreaker/backup and
    # is only accepted when one direction is strict; this avoids treating
    # corpus sentence-position casing as an authority.
    if capital_frequency > 0 and capital_frequency > lowercase_frequency:
        surface = normalized[:1].upper() + normalized[1:]
        return {
            "resolved": True,
            "surface": surface,
            "policy": "capitalized",
            "reason": (
                "nkjp-sgjp-capital-lemma-fallback"
                if basis == "surface" else "nkjp-sgjp-capital-lemma-linked-fallback"
            ),
            "linguistic_basis": (
                "nkjp-sgjp-casing" if basis == "surface" else "nkjp-sgjp-casing-lemma"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(sgjp_status),
            "nkjp_lemma_cases": {
                "capitalized_frequency": lemma_capital_frequency,
                "lowercase_frequency": lemma_lower_frequency,
            },
            "nkjp_correctness": sorted(correctness),
        }

    if lowercase_frequency > 0 and lowercase_frequency > capital_frequency:
        surface = normalized
        return {
            "resolved": True,
            "surface": surface,
            "policy": "lowercase",
            "reason": (
                "nkjp-sgjp-lower-lemma-fallback"
                if basis == "surface" else "nkjp-sgjp-lower-lemma-linked-fallback"
            ),
            "linguistic_basis": (
                "nkjp-sgjp-casing" if basis == "surface" else "nkjp-sgjp-casing-lemma"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(sgjp_status),
            "nkjp_lemma_cases": {
                "capitalized_frequency": lemma_capital_frequency,
                "lowercase_frequency": lemma_lower_frequency,
            },
            "nkjp_correctness": sorted(correctness),
        }

    if (
        not capital_frequency
        and not lowercase_frequency
        and lemma_capital_frequency > 0
        and lemma_capital_frequency > lemma_lower_frequency
    ):
        return {
            "resolved": True,
            "surface": normalized[:1].upper() + normalized[1:],
            "policy": "capitalized",
            "reason": (
                "nkjp-observed-lemma-capitalization-fallback"
                if basis == "surface" else "nkjp-observed-lemma-capitalization-lemma-fallback"
            ),
            "linguistic_basis": (
                "nkjp-lemma-casing" if basis == "surface" else "nkjp-lemma-casing-linked"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(sgjp_status),
            "nkjp_lemma_cases": {
                "capitalized_frequency": lemma_capital_frequency,
                "lowercase_frequency": lemma_lower_frequency,
            },
            "nkjp_correctness": sorted(correctness),
        }

    if (
        not capital_frequency
        and not lowercase_frequency
        and lemma_lower_frequency > 0
        and lemma_lower_frequency > lemma_capital_frequency
    ):
        return {
            "resolved": True,
            "surface": normalized,
            "policy": "lowercase",
            "reason": (
                "nkjp-observed-lemma-lowercase-fallback"
                if basis == "surface" else "nkjp-observed-lemma-lowercase-lemma-fallback"
            ),
            "linguistic_basis": (
                "nkjp-lemma-casing" if basis == "surface" else "nkjp-lemma-casing-linked"
            ),
            "explicit_policy_conflict": False,
            "common_lexical_matches": [],
            "common_adjective_matches": [],
            "common_noun_matches": [],
            "proper_name_matches": [],
            "proper_name_classes": [],
            "linguistic_analysis_count": 0,
            "nkjp_sgjp_status": sorted(sgjp_status),
            "nkjp_lemma_cases": {
                "capitalized_frequency": lemma_capital_frequency,
                "lowercase_frequency": lemma_lower_frequency,
            },
            "nkjp_correctness": sorted(correctness),
        }

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
