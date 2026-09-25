#!/usr/bin/env python3
"""Generate complete available case paradigms for one-token KSNG country/capital names."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
import morfeusz2

CASES = {"nom","gen","dat","acc","inst","loc","voc"}
SURFACE_RE = re.compile(r"^[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--countries", type=Path, required=True)
    ap.add_argument("--capitals", type=Path, required=True)
    ap.add_argument("--out-countries", type=Path, required=True)
    ap.add_argument("--out-capitals", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    return ap.parse_args()

def load(path: Path) -> list[dict[str,str]]:
    with path.open(encoding="utf-8", newline="") as h:
        return list(csv.DictReader(h, delimiter="\t"))

def tag_parts(tag: str) -> tuple[str,str,set[str]]:
    p = tag.split(":")
    if len(p) < 3 or p[0] != "subst" or p[1] not in {"sg","pl"}:
        return "", "", set()
    return "subst", p[1], {x for x in p[2].split(".") if x in CASES}

def gen_rows(rows: list[dict[str,str]], category: str, rejected_official: list[dict[str,str]]) -> list[dict[str,str]]:
    out = []
    for row in rows:
        name = row["name"].strip()
        if not SURFACE_RE.fullmatch(name):
            continue
        lower = name.lower()
        policy = row["case_policy"]
        generated: dict[tuple[str,str,str],str] = {}
        # The official source is authoritative for the base and its published D./Mc. forms.
        generated[("source","nom","source")] = name
        if row.get("official_ndm") != "yes":
            if row.get("official_genitive"):
                form = row["official_genitive"].strip()
                if SURFACE_RE.fullmatch(form):
                    generated[("source","gen","source")] = form
                else:
                    rejected_official.append({"category": category, "name": name, "case": "gen", "form": form, "reason": "official form is not a single dictionary token"})
            if row.get("official_locative"):
                form = row["official_locative"].strip()
                if SURFACE_RE.fullmatch(form):
                    generated[("source","loc","source")] = form
                else:
                    rejected_official.append({"category": category, "name": name, "case": "loc", "form": form, "reason": "official form is not a single dictionary token"})
        for orth, lemma, tag, _names, _labels in morfeusz2.Morfeusz(
            expand_tags=True, expand_dot=True, expand_underscore=True
        ).generate(name):
            if str(lemma).lower() != lower:
                continue
            _, number, cases = tag_parts(str(tag))
            for case in sorted(cases):
                surface = str(orth).strip()
                if not surface or not SURFACE_RE.fullmatch(surface):
                    continue
                if policy == "capitalized":
                    surface = surface[:1].upper() + surface[1:]
                else:
                    surface = surface.lower()
                generated[("morfeusz",case,number)] = surface
        for (origin, case, number), surface in sorted(generated.items(), key=lambda x: (x[0][1], x[0][2], x[1])):
            out.append({
                "category": category, "name": name, "number": number,
                "case": case, "form": surface, "case_policy": policy,
                "source": "KSNG/GUGiK official form" if origin == "source" else
                          "Morfeusz 2 / SGJP generated from KSNG/GUGiK name",
                "morfeusz_version": str(morfeusz2.__version__),
            })
    return out

def write(path: Path, rows: list[dict[str,str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = ["category","name","number","case","form","case_policy","source","morfeusz_version"]
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def main() -> int:
    args = parse_args()
    rejected_official: list[dict[str,str]] = []
    countries = gen_rows(load(args.countries), "country", rejected_official)
    capitals = gen_rows(load(args.capitals), "capital", rejected_official)
    write(args.out_countries, countries)
    write(args.out_capitals, capitals)
    report = {
        "oracle": "Morfeusz 2",
        "countries_forms": len(countries),
        "capital_forms": len(capitals),
        "countries_items": len({r["name"].lower() for r in countries}),
        "capital_items": len({r["name"].lower() for r in capitals}),
        "rejected_official_source_forms": rejected_official,
    }
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
