#!/usr/bin/env python3
"""Generate complete validated singular inflections for TERC admin names.

All 16 voivodeships are included, including the two hyphenated names. Lower
levels retain the existing one-token eligibility gate."""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from surface_components import LEXICAL_HYPHENS, hyphen_components, is_hyphenated

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
        # All voivodeships require complete singular paradigms, including
        # hyphenated names. Lower-level units retain the existing one-token gate.
        if row["level"] != "voivodeship" and row["eligible_single_token"] != "yes":
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
    voivodeship_names = set()
    for unit_key in sorted(names):
        row_meta = names[unit_key]
        lower_name = row_meta["name"].strip().lower()
        name = row_meta["name"]
        generated = {("nom", name)}

        if row_meta["level"] == "voivodeship":
            # Voivodeship names are adjectival. For a hyphenated name such as
            # "kujawsko-pomorskie", inflect only the final adjective and keep
            # the invariant first component unchanged.
            from polish_inflection import odmien_przymiotnik, podaj_przymiotnik, NIJAKI
            if is_hyphenated(name):
                parts = hyphen_components(name)
                separator = next((char for char in name if char in LEXICAL_HYPHENS), "-")
            else:
                parts = [name]
                separator = ""
            last = parts[-1].strip().lower()
            analyses = podaj_przymiotnik(last)
            lemmas = sorted({
                str(a.lemat).strip().lower()
                for a in analyses
                if str(a.liczba) == "sg" and str(a.rodzaj) == "n"
            })
            if not lemmas:
                raise SystemExit(
                    "No SGJP adjective lemma for voivodeship "
                    + repr(name) + " final component " + repr(last)
                )
            lemma = lemmas[0]
            for case_tag, const in constants.items():
                if case_tag == "nom":
                    continue
                try:
                    form = str(
                        odmien_przymiotnik(lemma, const, NIJAKI, default=None) or ""
                    ).strip()
                except Exception:
                    form = ""
                if not form:
                    continue
                validated = podaj_przymiotnik(form)
                if not any(
                    str(a.lemat).strip().lower() == lemma
                    and str(a.przypadek) == case_tag
                    and str(a.liczba) == "sg"
                    and str(a.rodzaj) == "n"
                    for a in validated
                ):
                    continue
                prefix = separator.join(part.strip() for part in parts[:-1])
                composed = (prefix + separator + form) if prefix else form
                generated.add((case_tag, composed))
            voivodeship_names.add(unit_key)
        else:
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

    if len(voivodeship_names) != 16:
        raise SystemExit(
            "TERC voivodeship generation requires all 16 units, got "
            + str(len(voivodeship_names))
        )
    missing_voivodeship_cases = {
        unit_key: sorted(set(CASES) - case_coverage.get(unit_key, set()))
        for unit_key in sorted(voivodeship_names)
        if set(CASES) - case_coverage.get(unit_key, set())
    }
    if missing_voivodeship_cases:
        raise SystemExit(
            "TERC voivodeship full-inflection gap: "
            + json.dumps(missing_voivodeship_cases, ensure_ascii=False, sort_keys=True)
        )

    report = {
        "oracle": "Morfeusz 2 / SGJP + polish-inflection SGJP adjective rules",
        "morfeusz_version": str(morfeusz2.__version__),
        "category": "terc",
        "number": "sg",
        "input_identity": "level+terc",
        "input_units_total": len(names),
        "voivodeship_units": len(voivodeship_names),
        "voivodeship_full_inflection": True,
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
