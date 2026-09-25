#!/usr/bin/env python3
"""Generate complete validated singular inflections for one-token TERC admin names."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

CASES = ("nom", "gen", "dat", "acc", "inst", "loc", "voc")


def load_tsv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


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
        names.setdefault(lower, row)

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
    for lower_name in sorted(names):
        name = names[lower_name]["name"]
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
        for case_tag, surface in sorted(generated, key=lambda x: (CASES.index(x[0]), x[1])):
            out.append({
                "name": name,
                "level": names[lower_name]["level"],
                "terc": names[lower_name]["terc"],
                "case": case_tag,
                "form": surface,
                "source": "Morfeusz 2 / SGJP generated from GUS TERYT TERC",
                "morfeusz_version": str(morfeusz2.__version__),
            })
        case_coverage[lower_name] = {case for case, _ in generated}

    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name","level","terc","case","form","source","morfeusz_version"], delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)

    report = {
        "oracle": "Morfeusz 2 / SGJP",
        "morfeusz_version": str(morfeusz2.__version__),
        "input_unique_one_token_names": len(names),
        "inflection_record_count": len(out),
        "names_with_non_nominative": sum(1 for cases in case_coverage.values() if len(cases) > 1),
    }
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    raise SystemExit(main())
