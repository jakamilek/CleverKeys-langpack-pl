#!/usr/bin/env python3
"""Extract the three-level Polish administrative division from official TERC.xml."""
from __future__ import annotations

import argparse
import csv
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

POLISH_WORD_RE = re.compile(r"^[a-ząćęłńóśźż]+$", re.IGNORECASE)
GMINA_RODZ = {"1", "2", "3"}


def canonical_surface(name: str, level: str, kind: str) -> tuple[str, str]:
    """Return the CKDT surface and explicit casing policy for an admin unit name."""
    value = name.strip()
    if level == "voivodeship":
        # TERYT stores voivodeship names in uppercase; ordinary Polish usage writes
        # the standalone adjective with an initial capital only in a name-like layer.
        return value[:1].upper() + value[1:].lower(), "capitalized"
    if level == "powiat" and kind == "powiat":
        # Powiat names are adjectival: powiat cieszyński -> cieszyński.
        return value.lower(), "lowercase"
    # City-with-powiat-rights and gmina names identify concrete units and retain
    # proper-name capitalization from the official source.
    return value, "capitalized"




def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    ap.add_argument("--out-flat-tsv", type=Path, required=True)
    return ap.parse_args()


def strip_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].upper()


def text_of(elem: ET.Element, key: str) -> str:
    """Read a named <col> field from the official TERC row structure."""
    wanted = key.upper()
    for child in elem:
        if strip_tag(child.tag) != "COL":
            continue
        if str(child.attrib.get("name", "")).upper() == wanted:
            return (child.text or "").strip()
    return ""


def main() -> int:
    args = parse_args()
    with zipfile.ZipFile(args.zip) as zf:
        xml_names = [n for n in zf.namelist() if n.upper().endswith(".XML") and "TERC" in n.upper()]
        if len(xml_names) != 1:
            raise SystemExit(f"Expected exactly one TERC XML in archive, found: {xml_names}")
        with zf.open(xml_names[0]) as fh:
            root = ET.parse(fh).getroot()

    rows = []
    counts = {"voivodeship": 0, "powiat": 0, "gmina": 0}
    skipped_lower_level = 0

    for elem in root.iter():
        if strip_tag(elem.tag) != "ROW":
            continue
        woj = text_of(elem, "WOJ")
        pow_ = text_of(elem, "POW")
        gmi = text_of(elem, "GMI")
        rodz = text_of(elem, "RODZ")
        name = text_of(elem, "NAZWA")
        kind = text_of(elem, "NAZDOD")
        stan_na = text_of(elem, "STAN_NA")
        if not woj or not name or not kind:
            raise SystemExit("TERC row missing WOJ/NAZWA/NAZDOD")

        level = None
        if not pow_ and not gmi and not rodz and kind == "województwo":
            level = "voivodeship"
        elif pow_ and not gmi and not rodz and kind in {
            "powiat", "miasto na prawach powiatu", "miasto stołeczne, na prawach powiatu",
        }:
            level = "powiat"
        elif pow_ and gmi and rodz in GMINA_RODZ and kind in {
            "gmina miejska", "gmina wiejska", "gmina miejsko-wiejska", "miasto stołeczne",
        }:
            level = "gmina"
        else:
            skipped_lower_level += 1
            continue

        counts[level] += 1
        canonical_name, case_policy = canonical_surface(name, level, kind)
        eligible_single_token = bool(POLISH_WORD_RE.fullmatch(canonical_name))
        rows.append({
            "level": level,
            "terc": woj + pow_ + gmi + rodz,
            "woj": woj,
            "pow": pow_,
            "gmi": gmi,
            "rodz": rodz,
            "name": canonical_name,
            "case_policy": case_policy,
            "source_name": name,
            "nazdod": kind,
            "stan_na": stan_na,
            "eligible_single_token": "yes" if eligible_single_token else "no",
            "source": "GUS TERYT TERC",
        })

    expected = {"voivodeship": 16, "powiat": 380, "gmina": 2479}
    if counts != expected:
        raise SystemExit(f"Unexpected TERC counts: got {counts}, expected {expected}")

    for output in (args.out_tsv, args.out_flat_tsv):
        output.parent.mkdir(parents=True, exist_ok=True)

    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level", "terc", "woj", "pow", "gmi", "rodz", "name",
                "nazdod", "stan_na", "eligible_single_token", "case_policy",
                "source_name", "source",
            ],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda r: (r["level"], r["terc"], r["name"].lower())))

    flat_rows = [row for row in rows if row["eligible_single_token"] == "yes"]
    with args.out_flat_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "level", "terc", "woj", "pow", "gmi", "rodz", "name",
                "nazdod", "stan_na", "eligible_single_token", "case_policy",
                "source_name", "source",
            ],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(sorted(flat_rows, key=lambda r: (r["level"], r["terc"], r["name"].lower())))

    unique_keys = {}
    for row in rows:
        unique_keys.setdefault(row["name"].lower(), set()).add(row["terc"])
    report = {
        "source": "GUS TERYT TERC",
        "counts": counts,
        "total_records": len(rows),
        "unique_case_insensitive_names": len(unique_keys),
        "duplicate_name_keys": sum(1 for codes in unique_keys.values() if len(codes) > 1),
        "single_token_records": len(flat_rows),
        "flat_output": str(args.out_flat_tsv),
        "multi_token_records": sum(1 for r in rows if r["eligible_single_token"] == "no"),
        "skipped_lower_level_or_non_three_level_rows": skipped_lower_level,
    }
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
