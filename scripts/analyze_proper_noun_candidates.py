#!/usr/bin/env python3
"""Build an audit-only triage report for proper-noun casing candidates.

The report combines the existing proper-noun audit TSV with the raw official
PESEL source files downloaded by the audit workflow. It never modifies the
language pack or promotes candidates.

Signals:
- PESEL first-name population count, when present in the official source.
- cross-kind lowercase collisions (given name/locality/genitive).
- Polish wordfreq Zipf score as a heuristic common-word signal.
- current CKDT variants and review status from the audit TSV.

The output is deliberately advisory: no threshold here authorizes promotion.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import unicodedata
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

PL_ALPHABET = set("aąbcćdeęfghijklłmnńoóprsśtuwyzźż")
WORD_RE = re.compile(r"^[a-ząćęłńóśźż]+$", re.IGNORECASE)


def fold(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(c for c in value if unicodedata.category(c) != "Mn").replace("ł", "l")


def canonical_name(raw: str) -> str | None:
    value = raw.strip()
    if not WORD_RE.fullmatch(value):
        return None
    if not all(ch.lower() in PL_ALPHABET for ch in value):
        return None
    lower = value.lower()
    return lower[0].upper() + lower[1:]


def normalized_header(value: str) -> str:
    return fold(value).replace("_", "").replace(" ", "")


def find_name_index(header: list[str], path: Path) -> int:
    candidates = [
        i for i, value in enumerate(header)
        if "imie" in normalized_header(value)
    ]
    if not candidates:
        raise RuntimeError(f"{path}: cannot locate PESEL name column in {header}")
    return candidates[0]


def find_count_index(header: list[str], path: Path) -> int:
    preferred = []
    for i, value in enumerate(header):
        norm = normalized_header(value)
        if "lp" == norm or norm in {"numer", "id"}:
            continue
        if "liczba" in norm and (
            "wystap" in norm or "osob" in norm or "rejestr" in norm
        ):
            preferred.append(i)
    if len(preferred) == 1:
        return preferred[0]

    broad = [
        i for i, value in enumerate(header)
        if "liczba" in normalized_header(value)
        and normalized_header(value) not in {"liczba", "liczbaporzadkowa"}
    ]
    if len(broad) == 1:
        return broad[0]

    raise RuntimeError(
        f"{path}: cannot identify PESEL population-count column in {header}; "
        "expected a header containing 'liczba' and preferably 'wystąp...' or 'osób'"
    )


def parse_int(value: str) -> int:
    cleaned = value.strip().replace(" ", "").replace(" ", "").replace(",", "")
    if not cleaned:
        return 0
    if not re.fullmatch(r"-?\d+", cleaned):
        raise ValueError(f"not an integer: {value!r}")
    return int(cleaned)


def rows_from_xlsx(path: Path) -> list[list[str]]:
    with zipfile.ZipFile(path) as archive:
        names = set(archive.namelist())
        required = {"xl/workbook.xml", "xl/_rels/workbook.xml.rels"}
        if not required.issubset(names):
            raise RuntimeError(f"Unsupported XLSX structure: {path}")

        workbook_ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        package_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.find(f"{{{workbook_ns}}}sheets")
        sheet = sheets.find(f"{{{workbook_ns}}}sheet") if sheets is not None else None
        if sheet is None:
            raise RuntimeError(f"XLSX has no worksheets: {path}")

        relationship_id = sheet.attrib.get(f"{{{rel_ns}}}id")
        if not relationship_id:
            raise RuntimeError(f"XLSX sheet has no relationship id: {path}")

        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = None
        for relation in relationships:
            if (
                relation.tag == f"{{{package_rel_ns}}}Relationship"
                and relation.attrib.get("Id") == relationship_id
            ):
                target = relation.attrib.get("Target")
                break
        if not target:
            raise RuntimeError(f"XLSX sheet relationship not found: {path}")

        sheet_path = str(Path("xl") / target).replace("\\", "/")
        if sheet_path not in names:
            sheet_path = "xl/" + target.lstrip("/")
        if sheet_path not in names:
            raise RuntimeError(f"XLSX worksheet target not found: {path}")

        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in names:
            shared_root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in shared_root.findall(f"{{{workbook_ns}}}si"):
                shared_strings.append("".join(item.itertext()))

        sheet_root = ET.fromstring(archive.read(sheet_path))
        rows: list[list[str]] = []
        for row in sheet_root.findall(f".//{{{workbook_ns}}}row"):
            values: dict[int, str] = {}
            for cell in row.findall(f"{{{workbook_ns}}}c"):
                ref = cell.attrib.get("r", "")
                match = re.match(r"([A-Z]+)", ref.upper())
                if not match:
                    continue
                column = 0
                for char in match.group(1):
                    column = column * 26 + (ord(char) - ord("A") + 1)
                column -= 1

                value = ""
                cell_type = cell.attrib.get("t")
                if cell_type == "s":
                    raw_value = cell.find(f"{{{workbook_ns}}}v")
                    if raw_value is not None and raw_value.text is not None:
                        value = shared_strings[int(raw_value.text)]
                elif cell_type == "inlineStr":
                    inline = cell.find(f"{{{workbook_ns}}}is")
                    if inline is not None:
                        value = "".join(inline.itertext())
                else:
                    raw_value = cell.find(f"{{{workbook_ns}}}v")
                    if raw_value is not None and raw_value.text is not None:
                        value = raw_value.text
                values[column] = value
            if values:
                width = max(values) + 1
                rows.append([values.get(i, "") for i in range(width)])
        return rows


def rows_from_source(path: Path) -> list[list[str]]:
    raw = path.read_bytes()
    if raw.startswith(b"PK\x03\x04"):
        return rows_from_xlsx(path)

    text = None
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "iso-8859-2"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise RuntimeError(f"{path}: cannot decode source")

    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
    return list(csv.reader(io.StringIO(text, newline=""), dialect))


def parse_pesel_counts(paths: list[Path]) -> tuple[dict[str, int], list[dict]]:
    totals: dict[str, int] = {}
    manifests: list[dict] = []
    for path in paths:
        rows = rows_from_source(path)
        if not rows:
            raise RuntimeError(f"{path}: empty source")
        name_index = find_name_index(rows[0], path)
        count_index = find_count_index(rows[0], path)
        row_count = 0
        for row in rows[1:]:
            if name_index >= len(row) or count_index >= len(row):
                continue
            canonical = canonical_name(row[name_index])
            if not canonical:
                continue
            count = parse_int(row[count_index])
            if count < 0:
                raise RuntimeError(f"{path}: negative PESEL count for {canonical}")
            totals[canonical.lower()] = totals.get(canonical.lower(), 0) + count
            row_count += 1
        manifests.append({
            "path": path.name,
            "rows_with_names": row_count,
            "name_column": rows[0][name_index],
            "count_column": rows[0][count_index],
        })
    return totals, manifests


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--audit-tsv", type=Path, required=True)
    ap.add_argument("--source-dir", type=Path, required=True)
    ap.add_argument("--wordlist", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    args = ap.parse_args()

    source_paths = sorted(args.source_dir.glob("resource-115*.csv"))
    if not source_paths:
        raise SystemExit(f"No PESEL resource files found in {args.source_dir}")

    pesel_counts, manifests = parse_pesel_counts(source_paths)

    with args.audit_tsv.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))

    by_lower: dict[str, list[dict]] = {}
    for row in rows:
        by_lower.setdefault(row["lower"], []).append(row)

    pack_words = {
        line.strip()
        for line in args.wordlist.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.startswith("#")
    }

    try:
        from wordfreq import zipf_frequency
    except Exception as exc:
        raise SystemExit(f"wordfreq is required for heuristic risk signal: {exc}")

    triage: list[dict] = []
    for row in rows:
        lower = row["lower"]
        variants = [x for x in by_lower[lower]]
        kinds = sorted({x["kind"] for x in variants})
        cross_kind_collision = len(kinds) > 1
        zipf = float(zipf_frequency(lower, "pl"))
        triage_row = {
            "kind": row["kind"],
            "canonical": row["canonical"],
            "lower": lower,
            "status": row["status"],
            "reviewed": row["reviewed"] == "True",
            "current_variants": row["current_variants"],
            "cross_kind_collision": cross_kind_collision,
            "collision_kinds": kinds,
            "pesel_population": pesel_counts.get(lower),
            "zipf_pl": zipf,
            "common_word_signal": zipf >= 4.0,
            "already_in_ckdt": lower in {w.lower() for w in pack_words},
        }
        triage.append(triage_row)

    lowercase_only = [x for x in triage if x["status"] == "lowercase_only"]
    candidates = [
        x for x in lowercase_only
        if x["kind"] == "given_name" and not x["cross_kind_collision"]
    ]
    candidates.sort(
        key=lambda x: (
            -(x["pesel_population"] or 0),
            x["common_word_signal"],
            -x["zipf_pl"],
            x["canonical"],
        )
    )

    report = {
        "mode": "audit-only",
        "promotion": False,
        "heuristics": {
            "common_word_signal_zipf_pl_gte": 4.0,
            "common_word_signal_is_not_a_promotion_gate": True,
        },
        "source_manifests": manifests,
        "counts": {
            "audit_rows": len(rows),
            "lowercase_only": len(lowercase_only),
            "lowercase_only_given_names": sum(
                1 for x in lowercase_only if x["kind"] == "given_name"
            ),
            "lowercase_only_localities": sum(
                1 for x in lowercase_only if x["kind"] == "locality"
            ),
            "lowercase_only_locality_genitives": sum(
                1 for x in lowercase_only if x["kind"] == "locality_genitive"
            ),
            "cross_kind_collisions": sum(
                1 for lower, group in by_lower.items()
                if len({x["kind"] for x in group}) > 1
            ),
            "given_name_lowercase_only_clean": len(candidates),
            "given_name_lowercase_only_with_collision": sum(
                1 for x in lowercase_only
                if x["kind"] == "given_name" and x["cross_kind_collision"]
            ),
            "given_name_lowercase_only_common_word_signal": sum(
                1 for x in lowercase_only
                if x["kind"] == "given_name" and x["common_word_signal"]
            ),
        },
        "top_given_name_casing_candidates": candidates[:500],
        "top_collision_examples": sorted(
            [
                x for x in lowercase_only
                if x["cross_kind_collision"]
            ],
            key=lambda x: (x["lower"], x["kind"])
        )[:500],
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            "kind", "canonical", "lower", "status", "reviewed",
            "cross_kind_collision", "collision_kinds",
            "pesel_population", "zipf_pl", "common_word_signal",
            "current_variants",
        ])
        for row in sorted(
            triage,
            key=lambda x: (x["status"], x["kind"], x["canonical"])
        ):
            writer.writerow([
                row["kind"],
                row["canonical"],
                row["lower"],
                row["status"],
                str(row["reviewed"]),
                str(row["cross_kind_collision"]),
                ";".join(row["collision_kinds"]),
                "" if row["pesel_population"] is None else row["pesel_population"],
                f'{row["zipf_pl"]:.3f}',
                str(row["common_word_signal"]),
                row["current_variants"],
            ])

    print(json.dumps({
        "mode": report["mode"],
        "promotion": report["promotion"],
        "counts": report["counts"],
        "source_manifests": report["source_manifests"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
