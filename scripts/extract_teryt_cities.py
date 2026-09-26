#!/usr/bin/env python3
"""Extract all official city names (SIMC RM=96) from the TERYT archive.

The source layer preserves full multiword/hyphenated names. CKDT admission and
capitalization audit operate on their word components; downstream one-token
morphology generation may intentionally select only single-token names.
"""
from __future__ import annotations

import argparse
import csv
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

POLISH_WORD_RE = re.compile(r"^[a-ząćęłńóśźż]+$", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    return ap.parse_args()


def strip_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].upper()


def text_of(elem: ET.Element, key: str) -> str:
    for child in elem:
        if strip_tag(child.tag) == key.upper():
            return (child.text or "").strip()
    return ""


def main() -> int:
    args = parse_args()
    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.parent.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.zip) as zf:
        xml_names = [
            n for n in zf.namelist()
            if n.upper().endswith(".XML") and "SIMC" in n.upper()
        ]
        if len(xml_names) != 1:
            raise SystemExit(
                f"Expected exactly one SIMC XML in archive, found: {xml_names}"
            )
        with zf.open(xml_names[0]) as fh:
            root = ET.parse(fh).getroot()

    rows: list[dict[str, str]] = []
    all_city_rows = 0
    skipped_non_word_surface = 0

    for elem in root.iter():
        if strip_tag(elem.tag) != "ROW":
            continue
        rm = text_of(elem, "RM")
        if rm != "96":
            continue
        all_city_rows += 1
        name = text_of(elem, "NAZWA")
        sym = text_of(elem, "SYM")
        stan_na = text_of(elem, "STAN_NA")
        if not name or not sym:
            raise SystemExit("SIMC city row missing NAZWA or SYM")
        rows.append({
            "name": name,
            "simc": sym,
            "rm": rm,
            "stan_na": stan_na,
            "source": "GUS TERYT SIMC",
        })

    unique: dict[str, dict[str, str]] = {}
    for row in rows:
        key = row["name"].lower()
        prior = unique.get(key)
        if prior is None:
            unique[key] = row
        elif prior["name"] != row["name"]:
            raise SystemExit(
                f"Conflicting city casing for lowercase key {key!r}: "
                f"{prior['name']!r} vs {row['name']!r}"
            )

    final_rows = sorted(unique.values(), key=lambda r: (r["name"].lower(), r["simc"]))
    for row in final_rows:
        if not POLISH_WORD_RE.fullmatch(row["name"]):
            skipped_non_word_surface += 1

    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["name", "simc", "rm", "stan_na", "source"],
            delimiter="\t",
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(final_rows)

    report = {
        "source": "GUS TERYT SIMC",
        "rm_city_rows": all_city_rows,
        "city_rows": len(rows),
        "unique_city_names": len(final_rows),
        "single_token_city_names": sum(1 for r in final_rows if POLISH_WORD_RE.fullmatch(r["name"])),
        "multi_component_city_names": sum(1 for r in final_rows if len(__import__("re").findall(r"[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]+", r["name"])) > 1),
        "non_word_surface_city_names": skipped_non_word_surface,
        "deduplicated_lowercase_names": len(rows) - len(final_rows),
    }
    args.out_report.write_text(
        __import__("json").dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(__import__("json").dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
