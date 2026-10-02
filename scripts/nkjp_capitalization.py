#!/usr/bin/env python3
"""Shared NKJP1M secondary capitalization evidence helpers."""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path

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

def resolve_nkjp_via_morfeusz_lemmas(
    key: str,
    morfeusz,
    nkjp_lemmas: dict[str, dict[str, object]],
) -> dict[str, object] | None:
    """Use independent Morfeusz form-to-lemma linkage to consult NKJP1M."""
    lemma_keys: set[str] = set()
    try:
        analyses = morfeusz.analyse(key)
    except Exception:
        analyses = []
    for item in analyses:
        if len(item) < 2:
            continue
        lemma = str(item[1]).strip().lower()
        if lemma:
            lemma_keys.add(lemma)

    for lemma in sorted(lemma_keys):
        resolution = resolve_nkjp_capitalization(
            lemma,
            nkjp_lemmas.get(lemma),
            basis="lemma",
        )
        if resolution is None or str(resolution.get("policy")) != "capitalized":
            continue
        return {
            **resolution,
            "nkjp_linked_lemma": lemma,
            "nkjp_lemma_link_source": "morfeusz-form-to-lemma",
            "linguistic_basis": "nkjp-lemma-casing-linked",
        }
    return None


