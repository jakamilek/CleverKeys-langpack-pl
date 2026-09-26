#!/usr/bin/env python3
"""Generate complete validated singular inflections for one-token TERC admin names."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CASES = ("nom", "gen", "dat", "acc", "inst", "loc", "voc")
OUTPUT_FIELDS = (
    "category",
    "name",
    "level",
    "terc",
    "number",
    "case",
    "form",
    "case_policy",
    "source",
    "morfeusz_version",
)


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {
        "level",
        "terc",
        "woj",
        "pow",
        "gmi",
        "rodz",
        "name",
        "nazdod",
        "stan_na",
        "eligible_single_token",
        "case_policy",
        "source_name",
        "source",
    }
    if set(rows[0].keys()) != required if rows else True:
        raise SystemExit(f"Malformed TERC source header {path}")
    return rows


def case_from_tag(tag: str) -> set[str]:
    parts = tag.split(":")
    if len(parts) < 3 or parts[0] != "subst" or parts[1] != "sg":
        return set()
    return {c for c in parts[2].split(".") if c in CASES}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--terc", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

    rows = load_tsv(args.terc)
    names = {}
    for row in rows:
        if row["eligible_single_token"] != "yes":
            continue
        lower = row["name"].strip().lower()
        unit_key = (row["level"], row["terc"])
        # TERC code identifies the administrative unit. Do not collapse distinct
        # units that happen to share the same Polish name.
        prior = names.get(unit_key)
        if prior is not None and prior["name"].strip().lower() != lower:
            raise SystemExit(
                f"Conflicting TERC identity for {row['level']}/{row['terc']}: "
                f"{prior['name']!r} vs {row['name']!r}"
            )
        names[unit_key] = row

    import morfeusz2
    from polish_inflection import (
        MIANOWNIK, DOPEŁNIACZ, CELOWNIK, BIERNIK, NARZĘDNIK, MIEJSCOWNIK,
        WOŁACZ, POJEDYNCZA, odmien_warianty, podaj,
    )
    constants = {
        "nom": MIANOWNIK, "gen": DOPEŁNIACZ, "dat": CELOWNIK, "acc": BIERNIK,
        "inst": NARZĘDNIK, "loc": MIEJSCOWNIK, "voc": WOŁACZ,
    }
    morfeusz = morfeusz2.Morfeusz(expand_tags=True, expand_dot=True, expand_underscore=True)

    out = []
    case_coverage = {}
    for unit_key in sorted(names):
        row_meta = names[unit_key]
        lower_name = row_meta["name"].strip().lower()
        name = row_meta["name"]
        generated = {("nom", name)}
        for lemma_query in (name, lower_name):
            for orth, lemma, tag, _names, _labels in morfeusz.generate(lemma_query):
                if str(lemma).lower() != lower_name or not tag.startswith("subst:sg:"):
                    continue
                for case_tag in sorted(case_from_tag(tag)):
                    surface = str(orth).strip()
                    if surface:
                        generated.add((case_tag, surface[:1].upper() + surface[1:]))
        for case_tag, const in constants.items():
            if case_tag == "nom":
                continue
            try:
                variants = list(odmien_warianty(lower_name, const, POJEDYNCZA))
            except Exception:
                variants = []
            for variant in variants:
                form = str(variant).strip()
                if not form:
                    continue
                analyses = podaj(form, liczba=POJEDYNCZA)
                if any(
                    str(a.lemat).lower() == lower_name
                    and str(a.przypadek) == case_tag
                    and str(a.liczba) == "sg"
                    for a in analyses
                ):
                    generated.add((case_tag, form[:1].upper() + form[1:]))

        policy = row_meta.get("case_policy", "capitalized")
        for case_tag, surface in sorted(generated, key=lambda x: (CASES.index(x[0]), x[1])):
            surface = surface.lower() if policy == "lowercase" else surface[:1].upper() + surface[1:]
            out.append({
                "category": "terc",
                "name": name,
                "level": row_meta["level"],
                "terc": row_meta["terc"],
                "number": "sg",
                "case": case_tag,
                "form": surface,
                "case_policy": policy,
                "source": "Morfeusz 2 / SGJP generated from GUS TERYT TERC",
                "morfeusz_version": str(morfeusz2.__version__),
            })
        case_coverage[unit_key] = {case for case, _ in generated}

    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=OUTPUT_FIELDS,
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(out)

    report = {
        "oracle": "Morfeusz 2 / SGJP",
        "morfeusz_version": str(morfeusz2.__version__),
        "category": "terc",
        "number": "sg",
        "input_identity": "level+terc",
        "input_one_token_units": len(names),
        "inflection_record_count": len(out),
        "names_with_non_nominative": sum(
            1 for cases in case_coverage.values() if len(cases) > 1
        ),
    }
    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
