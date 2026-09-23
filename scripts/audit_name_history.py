#!/usr/bin/env python3
"""Audit a 20-year Polish first-name history from official dane.gov.pl data.

Scope:
- Full calendar years 2006..2025 (20 years).
- First names only (not second names, half-year releases, or voivodeship tables).
- Official Open Data portal resources published for the Ministry of Digital Affairs.

This tool is audit-only. It does not modify the language pack or promote names.
It resolves the yearly resources from the official dataset metadata, records
resource ids/URLs/SHA-256, aggregates first-name counts, and emits threshold
tables for a small historical core.

The report deliberately exposes multiple signals instead of making a hidden
promotion decision:
- cumulative first-name assignments over 20 years
- number of years present
- number of years in yearly top-100 / top-50
- recent 5-year assignments
- rank in the 20-year cumulative totals

A default "core" is reported as the top N names per gender by cumulative
assignments; it is advisory only.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
import zipfile
from collections import defaultdict
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPError, Request, urlopen
import xml.etree.ElementTree as ET

DANE_DATASET_RESOURCES = (
    "https://api.dane.gov.pl/1.4/datasets/219/resources?per_page=1000"
)
YEARS = tuple(range(2006, 2026))
RECENT_YEARS = set(range(2021, 2026))
NAME_RE = re.compile(r"^[A-Za-zĄąĆćĘęŁłŃńÓóŚśŹźŻż]+$")
TITLE_YEAR_RE = re.compile(
    r"(?i)imiona\s+(?:(?:żeńskie|męskie)\s+)?nadane\s+dzieciom\s+w\s+polsce\s+w\s+(\d{4})\s*(?:r\.|roku)"
)
TITLE_FIRST_RE = re.compile(r"(?i)imi[ęe]\s+pierwsze")
TITLE_SECOND_RE = re.compile(r"(?i)imi[ęe]\s+drugie")
TITLE_HALF_RE = re.compile(r"(?i)(?:i|ii)\s+połowie|półroczu|01\.01\.\d{4}\s*-\s*30\.06\.\d{4}")
TITLE_REGION_RE = re.compile(r"(?i)wg\s+(?:województw|usc|urzed|woj\.)")


def fold(value: str) -> str:
    import unicodedata
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(c for c in value if unicodedata.category(c) != "Mn").replace("ł", "l")


def norm_header(value: str) -> str:
    return fold(value).replace("_", "").replace(" ", "")


def canonical_name(value: str) -> str | None:
    value = value.strip().strip('"')
    if not value or not NAME_RE.fullmatch(value):
        return None
    low = value.lower()
    return low[0].upper() + low[1:]


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def fetch_bytes(url: str, headers: dict[str, str] | None = None) -> tuple[bytes, str, str]:
    request = Request(url, headers=headers or {})
    with urlopen(request, timeout=90) as response:
        return response.read(), response.headers.get_content_type(), response.geturl()


def flatten_text(value) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_text(v) for v in value.values())
    if isinstance(value, list):
        return " ".join(flatten_text(v) for v in value)
    return str(value) if value is not None else ""


def resource_title(item: dict) -> str:
    attrs = item.get("attributes") or {}
    for key in ("title", "name", "description"):
        value = attrs.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    for key in ("title", "name", "description"):
        value = item.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return flatten_text(item)


def resource_candidates(item: dict) -> list[str]:
    attrs = item.get("attributes") or {}
    links = item.get("links") or {}
    values = [
        attrs.get("downloadUrl"),
        attrs.get("download_url"),
        attrs.get("url"),
        attrs.get("file"),
        attrs.get("link"),
        links.get("download"),
        links.get("related"),
        item.get("downloadUrl"),
        item.get("url"),
        item.get("download_url"),
    ]
    out: list[str] = []
    for value in values:
        if isinstance(value, str) and value.startswith(("http://", "https://")):
            if value not in out:
                out.append(value)
    return out


def load_dataset_resources() -> list[dict]:
    data, _, _ = fetch_bytes(
        DANE_DATASET_RESOURCES,
        {"Accept": "application/json, application/vnd.api+json"},
    )
    payload = json.loads(data.decode("utf-8"))
    items = payload.get("data")
    if not isinstance(items, list):
        items = payload.get("results")
    if not isinstance(items, list):
        raise RuntimeError("dane.gov.pl dataset resources response has no data/results list")
    return items


def select_year_resources(items: list[dict]) -> dict[int, list[dict]]:
    selected: dict[int, list[dict]] = defaultdict(list)
    for item in items:
        title = resource_title(item)
        m = TITLE_YEAR_RE.search(title)
        if not m:
            continue
        year = int(m.group(1))
        if year not in YEARS:
            continue
        if not TITLE_FIRST_RE.search(title) or TITLE_SECOND_RE.search(title):
            continue
        if TITLE_HALF_RE.search(title) or TITLE_REGION_RE.search(title):
            continue
        resource_id = str(item.get("id") or (item.get("attributes") or {}).get("id") or "")
        if not resource_id:
            continue
        selected[year].append({
            "id": int(resource_id) if resource_id.isdigit() else resource_id,
            "title": title,
            "candidates": resource_candidates(item),
        })

    missing = [year for year in YEARS if not selected.get(year)]
    if missing:
        raise RuntimeError(
            "Could not resolve official first-name resources for years: "
            + ", ".join(map(str, missing))
        )
    return dict(selected)


def decode_rows_from_csv(data: bytes, path: Path) -> list[list[str]]:
    text = None
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "iso-8859-2"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise RuntimeError(f"{path}: cannot decode CSV using supported encodings")
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"
    return list(csv.reader(io.StringIO(text, newline=""), dialect))


def rows_from_xlsx(data: bytes, path: Path) -> list[list[str]]:
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        names = set(archive.namelist())
        required = {"xl/workbook.xml", "xl/_rels/workbook.xml.rels"}
        if not required.issubset(names):
            raise RuntimeError(f"{path}: unsupported XLSX structure")

        ns = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
        rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
        pkg_rel_ns = "http://schemas.openxmlformats.org/package/2006/relationships"

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        sheets = workbook.find(f"{{{ns}}}sheets")
        sheet = sheets.find(f"{{{ns}}}sheet") if sheets is not None else None
        if sheet is None:
            raise RuntimeError(f"{path}: XLSX has no worksheets")

        rel_id = sheet.attrib.get(f"{{{rel_ns}}}id")
        if not rel_id:
            raise RuntimeError(f"{path}: XLSX sheet has no relationship id")

        relationships = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        target = None
        for relation in relationships:
            if (
                relation.tag == f"{{{pkg_rel_ns}}}Relationship"
                and relation.attrib.get("Id") == rel_id
            ):
                target = relation.attrib.get("Target")
                break
        if not target:
            raise RuntimeError(f"{path}: worksheet relationship not found")

        sheet_path = str(Path("xl") / target).replace("\\", "/")
        if sheet_path not in names:
            sheet_path = "xl/" + target.lstrip("/")
        if sheet_path not in names:
            raise RuntimeError(f"{path}: worksheet target not found")

        shared: list[str] = []
        if "xl/sharedStrings.xml" in names:
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(f"{{{ns}}}si"):
                shared.append("".join(item.itertext()))

        root = ET.fromstring(archive.read(sheet_path))
        rows: list[list[str]] = []
        for row in root.findall(f".//{{{ns}}}row"):
            values: dict[int, str] = {}
            for cell in row.findall(f"{{{ns}}}c"):
                ref = cell.attrib.get("r", "")
                match = re.match(r"([A-Z]+)", ref.upper())
                if not match:
                    continue
                col = 0
                for char in match.group(1):
                    col = col * 26 + ord(char) - ord("A") + 1
                col -= 1

                value = ""
                cell_type = cell.attrib.get("t")
                raw_value = cell.find(f"{{{ns}}}v")
                if cell_type == "s":
                    if raw_value is not None and raw_value.text is not None:
                        value = shared[int(raw_value.text)]
                elif cell_type == "inlineStr":
                    inline = cell.find(f"{{{ns}}}is")
                    if inline is not None:
                        value = "".join(inline.itertext())
                elif raw_value is not None and raw_value.text is not None:
                    value = raw_value.text
                values[col] = value

            if values:
                width = max(values) + 1
                rows.append([values.get(i, "") for i in range(width)])
        return rows


def rows_from_data(data: bytes, title: str) -> list[list[str]]:
    if data.startswith(b"PK\x03\x04"):
        return rows_from_xlsx(data, Path(title))
    return decode_rows_from_csv(data, Path(title))


def find_col(header: list[str], needles: tuple[str, ...], label: str) -> int:
    hits = []
    for i, value in enumerate(header):
        norm = norm_header(value)
        if all(needle in norm for needle in needles):
            hits.append(i)
    if len(hits) != 1:
        raise RuntimeError(f"Expected one {label} column; got {hits} in {header}")
    return hits[0]


def parse_count(value: str) -> int:
    cleaned = (
        value.strip()
        .replace("\u00a0", "")
        .replace(" ", "")
        .replace(",", "")
        .replace(".", "")
    )
    if not cleaned:
        return 0
    if not re.fullmatch(r"\d+", cleaned):
        raise RuntimeError(f"Invalid name count value: {value!r}")
    return int(cleaned)


def parse_name_rows(
    rows: list[list[str]],
    title: str,
) -> dict[str, dict]:
    if not rows:
        raise RuntimeError(f"Empty source: {title}")
    header = rows[0]
    name_idx = find_col(header, ("imie",), "name")

    count_idx = None
    try:
        count_idx = find_col(header, ("liczba", "wystap"), "count")
    except RuntimeError:
        pass

    gender_idx = None
    for i, value in enumerate(header):
        if "plec" in norm_header(value):
            gender_idx = i
            break

    gender_hint = None
    low_title = title.lower()
    if "żeńskie" in low_title:
        gender_hint = "F"
    elif "męskie" in low_title:
        gender_hint = "M"

    out: dict[str, dict] = {}
    for row in rows[1:]:
        if name_idx >= len(row):
            continue
        name = canonical_name(row[name_idx])
        if not name:
            continue

        gender = gender_hint
        if gender_idx is not None and gender_idx < len(row):
            raw_gender = fold(row[gender_idx])
            if "kobiet" in raw_gender or "zensk" in raw_gender:
                gender = "F"
            elif "mezczy" in raw_gender or "mesk" in raw_gender:
                gender = "M"

        if gender not in {"F", "M"}:
            raise RuntimeError(
                f"Cannot determine gender for {name!r} in resource {title!r}"
            )
        if count_idx is None:
            raise RuntimeError(
                f"Cannot identify annual count column in resource {title!r}"
            )

        count = parse_count(row[count_idx]) if count_idx < len(row) else 0
        bucket = out.setdefault(name.lower(), {
            "name": name,
            "gender": gender,
            "count": 0,
        })
        if bucket["gender"] != gender:
            raise RuntimeError(
                f"Gender conflict for {name!r}: {bucket['gender']} vs {gender}"
            )
        bucket["count"] += count

    return out


def parse_historical_aggregate(
    rows: list[list[str]],
    years: range,
    title: str,
) -> dict[str, dict[int, dict[str, int]]]:
    if not rows:
        raise RuntimeError(f"Empty historical aggregate: {title}")
    header = rows[0]
    name_idx = find_col(header, ("imie",), "name")

    gender_idx = None
    for i, value in enumerate(header):
        if "plec" in norm_header(value):
            gender_idx = i
            break

    year_cols: dict[int, int] = {}
    for i, value in enumerate(header):
        raw = value.strip()
        if raw.isdigit() and len(raw) == 4:
            year = int(raw)
            if year in years:
                year_cols[year] = i

    if set(years).issubset(year_cols):
        out: dict[str, dict[int, dict[str, int]]] = {"F": {}, "M": {}}
        for row in rows[1:]:
            if name_idx >= len(row):
                continue
            name = canonical_name(row[name_idx])
            if not name:
                continue

            gender = None
            if gender_idx is not None and gender_idx < len(row):
                raw_gender = fold(row[gender_idx])
                if "kobiet" in raw_gender or "zensk" in raw_gender:
                    gender = "F"
                elif "mezczy" in raw_gender or "mesk" in raw_gender:
                    gender = "M"
            if gender not in {"F", "M"}:
                raise RuntimeError(
                    f"Cannot determine gender for {name!r} in aggregate {title!r}"
                )

            for year, col in year_cols.items():
                count = parse_count(row[col]) if col < len(row) else 0
                out[gender].setdefault(year, {})
                lower = name.lower()
                out[gender][year][lower] = (
                    out[gender][year].get(lower, 0) + count
                )
        return out

    # Fallback for a tall aggregate: one row per name/year.
    year_idx = None
    for i, value in enumerate(header):
        if norm_header(value) in {"rok", "year"}:
            year_idx = i
            break
    count_idx = find_col(header, ("liczba", "wystap"), "count")
    if year_idx is None:
        raise RuntimeError(
            f"Historical aggregate has neither year columns nor a ROK/YEAR column: {title!r}"
        )

    out = {"F": {}, "M": {}}
    for row in rows[1:]:
        if max(name_idx, year_idx, count_idx) >= len(row):
            continue
        try:
            year = int(row[year_idx].strip())
        except ValueError:
            continue
        if year not in years:
            continue
        name = canonical_name(row[name_idx])
        if not name:
            continue

        gender = None
        if gender_idx is not None:
            raw_gender = fold(row[gender_idx])
            if "kobiet" in raw_gender or "zensk" in raw_gender:
                gender = "F"
            elif "mezczy" in raw_gender or "mesk" in raw_gender:
                gender = "M"
        if gender not in {"F", "M"}:
            raise RuntimeError(
                f"Cannot determine gender for {name!r} in aggregate {title!r}"
            )

        count = parse_count(row[count_idx])
        lower = name.lower()
        out[gender].setdefault(year, {})
        out[gender][year][lower] = out[gender][year].get(lower, 0) + count
    return out

def download_resource(item: dict, out_dir: Path) -> tuple[bytes, dict]:
    # Reuse the downloader already exercised by the proper-noun audit. This
    # preserves its official resource metadata/page fallback behavior.
    from audit_proper_nouns import download_dane_csv

    metadata = download_dane_csv(int(item["id"]), out_dir)
    path = Path(metadata["path"])
    data = path.read_bytes()
    metadata = {
        **metadata,
        "title": item["title"],
    }
    return data, metadata

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-report", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--out-core", type=Path, required=True)
    ap.add_argument("--workdir", type=Path, default=None)
    ap.add_argument("--core-per-gender", type=int, default=300)
    args = ap.parse_args()

    workdir = args.workdir or Path(tempfile.mkdtemp(prefix="pl-name-history-"))
    workdir.mkdir(parents=True, exist_ok=True)

    resources = select_year_resources(load_dataset_resources())
    by_gender_year: dict[str, dict[int, dict[str, int]]] = {"F": {}, "M": {}}
    manifests = []

    # Download and parse the official 2000-2019 aggregate once, then retain
    # only the requested 2006-2019 slice.
    historical_item = resources[2006][0]
    historical_data, historical_manifest = download_resource(historical_item, workdir)
    historical_rows = rows_from_data(
        historical_data,
        historical_item["title"],
    )
    historical = parse_historical_aggregate(
        historical_rows,
        range(2006, 2020),
        historical_item["title"],
    )
    for gender in ("F", "M"):
        for year in range(2006, 2020):
            by_gender_year[gender][year] = historical[gender].get(year, {})
    manifests.append({
        **historical_manifest,
        "scope_used": "2006-2019 from official 2000-2019 aggregate",
    })

    # From 2020 onward, use exactly one national aggregate table for each
    # gender/year. Regional, half-year and second-name resources are excluded.
    for year in range(2020, 2026):
        for item in resources[year]:
            data, manifest = download_resource(item, workdir)
            parsed = parse_name_rows(
                rows_from_data(data, item["title"]),
                item["title"],
            )
            gender = item["gender_hint"]
            by_gender_year[gender][year] = {
                key: value["count"]
                for key, value in parsed.items()
            }
            manifests.append({
                **manifest,
                "scope_used": str(year),
                "gender": gender,
            })

    aggregates: dict[str, dict[str, dict]] = {"F": {}, "M": {}}
    for gender in ("F", "M"):
        for year in YEARS:
            year_rows = by_gender_year[gender].get(year, {})
            ranked = sorted(year_rows.items(), key=lambda kv: (-kv[1], kv[0]))
            for rank, (lower, count) in enumerate(ranked, 1):
                bucket = aggregates[gender].setdefault(lower, {
                    "name": lower[0].upper() + lower[1:],
                    "gender": gender,
                    "cumulative_count_20y": 0,
                    "years_present": 0,
                    "years_top50": 0,
                    "years_top100": 0,
                    "recent_5y_count": 0,
                    "year_counts": {},
                    "year_ranks": {},
                })
                bucket["cumulative_count_20y"] += count
                bucket["years_present"] += 1
                bucket["years_top50"] += rank <= 50
                bucket["years_top100"] += rank <= 100
                if year in RECENT_YEARS:
                    bucket["recent_5y_count"] += count
                bucket["year_counts"][str(year)] = count
                bucket["year_ranks"][str(year)] = rank

        ordered = sorted(
            aggregates[gender].values(),
            key=lambda row: (
                -row["cumulative_count_20y"],
                -row["years_top100"],
                -row["recent_5y_count"],
                row["name"],
            ),
        )
        for index, row in enumerate(ordered, 1):
            row["cumulative_rank_20y"] = index

    threshold_tables = {}
    for gender in ("F", "M"):
        ordered = sorted(
            aggregates[gender].values(),
            key=lambda row: row["cumulative_rank_20y"],
        )
        threshold_tables[gender] = {
            str(n): {
                "count": min(n, len(ordered)),
                "last_cumulative_count": ordered[min(n, len(ordered)) - 1]["cumulative_count_20y"]
                if ordered else 0,
                "last_years_top100": ordered[min(n, len(ordered)) - 1]["years_top100"]
                if ordered else 0,
            }
            for n in (100, 250, 500, 750, 1000)
        }

    core = []
    for gender in ("F", "M"):
        ordered = sorted(
            aggregates[gender].values(),
            key=lambda row: row["cumulative_rank_20y"],
        )
        core.extend(ordered[: args.core_per_gender])

    report = {
        "mode": "audit-only",
        "promotion": False,
        "scope": {
            "first_name_only": True,
            "years": list(YEARS),
            "year_count": len(YEARS),
            "recent_years": sorted(RECENT_YEARS),
            "source_dataset": "219, imiona-nadawane-dzieciom-w-polsce",
            "historical_aggregate_2000_2019": HISTORICAL_RESOURCE_ID,
        },
        "source_manifest": sorted(
            manifests,
            key=lambda x: (x["resource_id"], x.get("gender", ""), x["title"]),
        ),
        "counts": {
            "resources": len(manifests),
            "female_names_seen": len(aggregates["F"]),
            "male_names_seen": len(aggregates["M"]),
            "female_core_default": min(args.core_per_gender, len(aggregates["F"])),
            "male_core_default": min(args.core_per_gender, len(aggregates["M"])),
        },
        "thresholds": threshold_tables,
        "ranking_definition": {
            "primary": "cumulative first-name assignments across 2006-2025",
            "tie_break_1": "years in yearly top-100",
            "tie_break_2": "first-name assignments in 2021-2025",
            "tie_break_3": "canonical name",
        },
        "top_female": sorted(
            aggregates["F"].values(),
            key=lambda row: row["cumulative_rank_20y"],
        )[:1000],
        "top_male": sorted(
            aggregates["M"].values(),
            key=lambda row: row["cumulative_rank_20y"],
        )[:1000],
        "core_advisory": core,
    }

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            "gender", "name", "cumulative_rank_20y", "cumulative_count_20y",
            "years_present", "years_top50", "years_top100", "recent_5y_count",
        ])
        for gender in ("F", "M"):
            for row in sorted(
                aggregates[gender].values(),
                key=lambda x: x["cumulative_rank_20y"],
            ):
                writer.writerow([
                    gender,
                    row["name"],
                    row["cumulative_rank_20y"],
                    row["cumulative_count_20y"],
                    row["years_present"],
                    row["years_top50"],
                    row["years_top100"],
                    row["recent_5y_count"],
                ])

    args.out_core.parent.mkdir(parents=True, exist_ok=True)
    args.out_core.write_text(
        "\n".join(row["name"] for row in core) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "mode": report["mode"],
        "promotion": report["promotion"],
        "scope": report["scope"],
        "counts": report["counts"],
        "thresholds": report["thresholds"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
