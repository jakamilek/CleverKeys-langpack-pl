#!/usr/bin/env python3
"""Generate explicit singular inflection forms for the selected CleverKeys Polish first names.

The selected first-name list remains the authoritative source for which names exist.
Morfeusz 2 / SGJP is used only to enumerate attested singular substantive forms for
those already-approved names. No new names are imported.

Output TSV columns:
name	gender	case_tag	form	source	morfeusz_version

Only singular (sg) substantive forms are emitted. Indeclinable names therefore
produce only the forms actually supplied by the SGJP/Morfeusz generator.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CASES = ("nom", "gen", "dat", "acc", "inst", "loc", "voc")


def load_selected_names(
    history_report: Path,
    historical_tsv: Path,
    surface_policy: Path,
) -> tuple[list[dict[str, str]], dict[str, str]]:
    report = json.loads(history_report.read_text(encoding="utf-8"))
    selected: list[dict[str, str]] = []

    for gender, key in (("F", "top_female"), ("M", "top_male")):
        for row in report[key][:215]:
            selected.append({
                "gender": gender,
                "name": str(row["name"]).strip(),
                "layer": "modern",
            })

    with historical_tsv.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            selected.append({
                "gender": row["gender"],
                "name": row["name"].strip(),
                "layer": "historical",
            })

    if len(selected) != 470:
        raise SystemExit(f"Expected 470 selected names, got {len(selected)}")

    policy: dict[str, str] = {}
    with surface_policy.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            policy[row["name"].strip().lower()] = row["policy"].strip()

    active = [
        row for row in selected
        if policy.get(row["name"].lower(), "capitalized_name") != "exclude"
    ]
    if len(active) != 469:
        raise SystemExit(f"Expected 469 active names, got {len(active)}")

    return active, policy


def normalise_case(tag: str) -> set[str]:
    parts = tag.split(":")
    if len(parts) < 3:
        return set()
    if parts[0] != "subst" or parts[1] != "sg":
        return set()
    raw_cases = set()
    for chunk in parts[2].split("."):
        if chunk in CASES:
            raw_cases.add(chunk)
    return raw_cases


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history-report", type=Path, required=True)
    ap.add_argument("--historical-first-names", type=Path, required=True)
    ap.add_argument("--surface-policy", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

    import morfeusz2

    active_names, policy = load_selected_names(
        args.history_report, args.historical_first_names, args.surface_policy
    )
    morfeusz = morfeusz2.Morfeusz(
        expand_tags=True,
        expand_dot=True,
        expand_underscore=True,
    )

    rows: list[dict[str, str]] = []
    missing: list[dict[str, str]] = []
    by_name: dict[str, set[str]] = {}

    for item in active_names:
        name = item["name"]
        lower = name.lower()
        generated: set[tuple[str, str]] = set()

        # Morfeusz conditionally respects case for proper-name lemmas. Prefer the
        # canonical selected surface, then retry lowercase as a fallback.
        for lemma_query in (name, lower):
            for orth, lemma, tag, _names, _labels in morfeusz.generate(lemma_query):
                if str(lemma).lower() != lower:
                    continue
                if not tag.startswith("subst:sg:"):
                    continue
                for case_tag in sorted(normalise_case(tag)):
                    surface = str(orth).strip()
                    if not surface:
                        continue
                    if policy.get(lower) == "lowercase_common_noun":
                        surface = surface.lower()
                    else:
                        surface = surface[:1].upper() + surface[1:]
                    generated.add((case_tag, surface))
            if generated:
                break

        by_name[name] = {surface for _case, surface in generated}

        present_cases = {case for case, _surface in generated}
        if "nom" not in present_cases:
            missing.append({
                "name": name,
                "gender": item["gender"],
                "reason": "no-singular-nominative-generated",
            })
            continue

        for case_tag, surface in sorted(generated):
            rows.append({
                "name": name,
                "gender": item["gender"],
                "layer": item["layer"],
                "case": case_tag,
                "form": surface,
                "source": "Morfeusz 2 / SGJP",
                "morfeusz_version": str(morfeusz2.__version__),
            })

    if missing:
        details = ", ".join(x["name"] for x in missing)
        raise SystemExit(
            "Selected names missing singular nominative in Morfeusz/SGJP: " + details
        )

    # Every active name must have at least its nominative and no duplicate
    # (name, case, form) records.
    unique_keys = {(r["name"], r["case"], r["form"]) for r in rows}
    if len(unique_keys) != len(rows):
        raise SystemExit("Duplicate first-name inflection records detected")

    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t", lineterminator="\n")
        writer.writerow([
            "name", "gender", "layer", "case", "form", "source", "morfeusz_version"
        ])
        writer.writerows(
            [
                [
                    r["name"], r["gender"], r["layer"], r["case"],
                    r["form"], r["source"], r["morfeusz_version"]
                ]
                for r in sorted(rows, key=lambda r: (r["name"].lower(), CASES.index(r["case"]), r["form"]))
            ]
        )

    case_counts = {case: sum(1 for r in rows if r["case"] == case) for case in CASES}
    coverage = {
        name: sorted(
            {r["case"] for r in rows if r["name"] == name},
            key=CASES.index,
        )
        for name in by_name
    }

    report = {
        "mode": "selected-first-name-inflection-generation",
        "oracle": "Morfeusz 2 / SGJP",
        "morfeusz_version": str(morfeusz2.__version__),
        "selected_total": len(active_names),
        "inflection_record_count": len(rows),
        "case_counts": case_counts,
        "names_with_at_least_one_non_nom_form": sum(
            1 for cases in coverage.values() if len(cases) > 1
        ),
        "names_with_nom_only": sorted(
            name for name, cases in coverage.items() if cases == ["nom"]
        ),
        "coverage_by_name": coverage,
        "surface_policy": {
            "lowercase_common_noun_names": sorted(
                k for k, v in policy.items() if v == "lowercase_common_noun"
            ),
            "excluded_names": sorted(
                k for k, v in policy.items() if v == "exclude"
            ),
        },
        "provenance": {
            "selected_names": "official dane.gov.pl first-name statistics 2006-2025 + reviewed historical staging",
            "inflection_oracle": "Morfeusz 2 / SGJP",
            "license_basis": "SGJP inflectional data is distributed under 2-clause BSD; preserve attribution in project documentation",
        },
    }
    args.out_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "morfeusz_version": report["morfeusz_version"],
        "selected_total": report["selected_total"],
        "inflection_record_count": report["inflection_record_count"],
        "case_counts": report["case_counts"],
        "names_with_nom_only": len(report["names_with_nom_only"]),
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
