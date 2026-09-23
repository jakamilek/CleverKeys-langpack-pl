#!/usr/bin/env python3
"""Audit Polish proper-noun coverage and casing against official public sources.

Sources:
- Ministry of Digital Affairs / dane.gov.pl: current living-person first names,
  female and male snapshots dated 2026-01-20 (resource IDs 1159670/1159669).
- GUGiK / Geoportal PRNG WFS: official locality names in Poland.

This is an audit-only tool. It does not modify source data or auto-promote
proper nouns into the language pack.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import tempfile
import unicodedata
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlencode, urljoin
from urllib.request import HTTPError, Request, urlopen
import xml.etree.ElementTree as ET

PL_ALPHABET = set("aąbcćdeęfghijklłmnńoóprsśtuwyzźż")
WORD_RE = re.compile(r"^[a-ząćęłńóśźż]+$", re.IGNORECASE)
NAMES_RES = {
    "female_first_names_2026_01_20": 1159670,
    "male_first_names_2026_01_20": 1159669,
}
DANE_API = "https://api.dane.gov.pl/1.4/resources/{resource_id}/download/"
DANE_RESOURCE_PAGES = {
    1159670: "https://dane.gov.pl/pl/dataset/1667,lista-imion-wystepujacych-w-rejestrze-pesel-osoby-zyjace/resource/1159670/table?page=1&per_page=20&q=&sort=",
    1159669: "https://dane.gov.pl/pl/dataset/1667,lista-imion-wystepujacych-w-rejestrze-pesel-osoby-zyjace/resource/1159669/table?page=1&per_page=20&q=&sort=",
}
DANE_DATASET_RESOURCES = "https://api.dane.gov.pl/1.4/datasets/1667,lista-imion-wystepujacych-w-rejestrze-pesel-osoby-zyjace/resources?per_page=100"
PRNG_WFS = "https://mapy.geoportal.gov.pl/wss/service/PZGiK/PRNG/WFS/GeographicalNames"


def fold(value: str) -> str:
    value = unicodedata.normalize("NFD", value.lower())
    return "".join(c for c in value if unicodedata.category(c) != "Mn").replace("ł", "l")


def is_single_token(word: str) -> bool:
    return bool(WORD_RE.fullmatch(word)) and all(
        ch.lower() in PL_ALPHABET for ch in word
    )


def canonical_name(raw: str) -> str | None:
    value = raw.strip()
    if not value or not is_single_token(value):
        return None
    lower = value.lower()
    return lower[0].upper() + lower[1:]


def fetch_bytes(url: str, headers: dict[str, str] | None = None) -> tuple[bytes, str]:
    request = Request(url, headers=headers or {})
    with urlopen(request, timeout=90) as response:
        return response.read(), response.headers.get_content_type()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def download_dane_csv(resource_id: int, out_dir: Path) -> dict:
    url = DANE_API.format(resource_id=resource_id)
    resolved = url

    def save_result(data: bytes, content_type: str) -> dict:
        path = out_dir / f"resource-{resource_id}.csv"
        path.write_bytes(data)
        return {
            "resource_id": resource_id,
            "api_url": url,
            "resolved_url": resolved,
            "content_type": content_type,
            "sha256": sha256(data),
            "bytes": len(data),
            "path": str(path),
        }

    try:
        data, content_type = fetch_bytes(
            url, {"Accept": "application/json, text/csv, */*"}
        )
        stripped = data.lstrip()
        if content_type == "application/json" or stripped.startswith(b"{"):
            metadata = json.loads(data.decode("utf-8"))
            resolved = metadata.get("file") or metadata.get("link")
            if not resolved:
                raise RuntimeError(
                    f"data.gov.pl resource {resource_id}: no file/link in {metadata}"
                )
            data, content_type = fetch_bytes(
                resolved, {"Accept": "text/csv,application/octet-stream,*/*"}
            )
        return save_result(data, content_type)
    except HTTPError as exc:
        if exc.code != 404:
            raise

    # Some current data.gov.pl resource IDs return 404 on the historical
    # /download/ route. The public API exposes resources through the dataset
    # relationship; use that relation to resolve the actual download URL.
    try:
        resources_bytes, resources_type = fetch_bytes(
            DANE_DATASET_RESOURCES, {"Accept": "application/vnd.api+json, application/json"}
        )
        resources = json.loads(resources_bytes.decode("utf-8"))
        for item in resources.get("data", []):
            if str(item.get("id")) != str(resource_id):
                continue
            attrs = item.get("attributes") or {}
            candidates = [
                attrs.get("downloadUrl"),
                attrs.get("download_url"),
                attrs.get("url"),
                attrs.get("file"),
                attrs.get("link"),
                (item.get("links") or {}).get("download"),
                (item.get("links") or {}).get("related"),
            ]
            for candidate in candidates:
                if not candidate or not isinstance(candidate, str):
                    continue
                try:
                    resolved = candidate
                    data, content_type = fetch_bytes(
                        resolved, {"Accept": "text/csv,application/octet-stream,*/*"}
                    )
                    return save_result(data, content_type)
                except HTTPError:
                    continue
            break
    except HTTPError:
        pass

    # Try direct resource metadata endpoints as a secondary compatibility path.
    metadata_candidates = [
        f"https://api.dane.gov.pl/1.4/resources/{resource_id}/",
        f"https://api.dane.gov.pl/resources/{resource_id}/",
        f"https://api.dane.gov.pl/1.4/resources/{resource_id}",
        f"https://api.dane.gov.pl/resources/{resource_id}",
    ]
    for metadata_url in metadata_candidates:
        try:
            metadata_bytes, metadata_type = fetch_bytes(
                metadata_url, {"Accept": "application/json"}
            )
        except HTTPError as metadata_exc:
            if metadata_exc.code == 404:
                continue
            raise
        stripped = metadata_bytes.lstrip()
        if metadata_type == "application/json" or stripped.startswith(b"{"):
            metadata = json.loads(metadata_bytes.decode("utf-8"))
            resolved_candidate = metadata.get("file") or metadata.get("link")
            if resolved_candidate:
                resolved = resolved_candidate
                data, content_type = fetch_bytes(
                    resolved, {"Accept": "text/csv,application/octet-stream,*/*"}
                )
                return save_result(data, content_type)

    page_url = DANE_RESOURCE_PAGES.get(resource_id)
    if not page_url:
        raise RuntimeError(f"No public resource page configured for {resource_id}")

    html, _ = fetch_bytes(
        page_url, {"Accept": "text/html,application/xhtml+xml"}
    )
    text = html.decode("utf-8", errors="replace")
    hrefs = re.findall(r"href=[\"']([^\"']+)[\"']", text, flags=re.IGNORECASE)
    csv_candidates = []
    for href in hrefs:
        href = unquote(href.replace("&amp;", "&"))
        candidate = urljoin(page_url, href)
        low = candidate.lower()
        if ".csv" in low or "format=csv" in low or ("csv" in low and "download" in low):
            csv_candidates.append(candidate)

    if not csv_candidates:
        raise RuntimeError(
            f"data.gov.pl resource {resource_id}: API download and metadata endpoints "
            "returned 404, and the resource page exposed no CSV download URL"
        )

    resolved = csv_candidates[0]
    data, content_type = fetch_bytes(
        resolved, {"Accept": "text/csv,application/octet-stream,*/*"}
    )
    return save_result(data, content_type)

def _names_from_rows(rows: list[list[str]], path: Path) -> set[str]:
    header = rows[0] if rows else None
    if not header:
        raise RuntimeError(f"Empty table: {path}")

    def normalized_header(value: str) -> str:
        return fold(value).replace("_", "").replace(" ", "")

    candidates = [
        index
        for index, value in enumerate(header)
        if "imie" in normalized_header(value)
    ]
    if not candidates:
        raise RuntimeError(
            f"Cannot locate name column in {path}: {header}"
        )

    index = candidates[0]
    names: set[str] = set()
    for row in rows[1:]:
        if index >= len(row):
            continue
        canonical = canonical_name(row[index])
        if canonical:
            names.add(canonical)
    return names


def _parse_name_xlsx(path: Path) -> set[str]:
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

        relationships = ET.fromstring(
            archive.read("xl/_rels/workbook.xml.rels")
        )
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
                rows.append([values.get(index, "") for index in range(width)])

        return _names_from_rows(rows, path)


def parse_name_csv(path: Path) -> set[str]:
    raw = path.read_bytes()
    if raw.startswith(b"PK\x03\x04"):
        return _parse_name_xlsx(path)

    text = None
    for encoding in ("utf-8-sig", "utf-8", "cp1250", "iso-8859-2"):
        try:
            text = raw.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if text is None:
        raise UnicodeDecodeError(
            "unknown",
            raw,
            0,
            min(len(raw), 1),
            f"cannot decode {path} using UTF-8, cp1250 or ISO-8859-2",
        )
    try:
        dialect = csv.Sniffer().sniff(text[:4096], delimiters=";,\t,")
    except csv.Error:
        dialect = csv.excel
        dialect.delimiter = ";"

    rows = list(csv.reader(io.StringIO(text, newline=""), dialect))
    return _names_from_rows(rows, path)


def local_tag(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].lower()


def fetch_prng_feature_types() -> list[dict[str, str]]:
    query = urlencode({
        "service": "WFS",
        "version": "2.0.0",
        "request": "GetCapabilities",
    })
    data, _ = fetch_bytes(
        PRNG_WFS + "?" + query,
        {"Accept": "text/xml, application/xml"},
    )
    root = ET.fromstring(data)
    feature_types: list[dict[str, str]] = []

    for feature_type in root.iter():
        if local_tag(feature_type.tag) != "featuretype":
            continue
        name = ""
        title = ""
        for child in feature_type:
            tag = local_tag(child.tag)
            value = (child.text or "").strip()
            if tag == "name":
                name = value
            elif tag == "title":
                title = value
        if name:
            feature_types.append({"name": name, "title": title})
    return feature_types


def choose_official_locality_layer(
    feature_types: list[dict[str, str]],
) -> dict[str, str]:
    for feature_type in feature_types:
        haystack = fold(
            feature_type["title"] + " " + feature_type["name"]
        )
        if "urzedowe nazwymiejscowosci" in haystack:
            return feature_type

    for feature_type in feature_types:
        haystack = fold(
            feature_type["title"] + " " + feature_type["name"]
        )
        if "miejscowosci" in haystack and "urzed" in haystack:
            return feature_type

    raise RuntimeError(
        "PRNG WFS: official locality layer not found; feature types="
        + json.dumps(feature_types, ensure_ascii=False)
    )


def parse_prng_page(
    data: bytes,
) -> tuple[list[tuple[str, str]], int | None]:
    root = ET.fromstring(data)
    rows: list[tuple[str, str]] = []

    for member in root.iter():
        if local_tag(member.tag) not in {"featuremember", "member"}:
            continue

        name = ""
        genitive = ""
        for node in member.iter():
            tag = local_tag(node.tag)
            value = (node.text or "").strip()
            if tag == "nazwaglowna":
                name = value
            elif tag == "dopelniacz":
                genitive = value

        if name:
            rows.append((name, genitive))

    number_returned = root.attrib.get("numberReturned")
    returned = (
        int(number_returned)
        if number_returned and number_returned.isdigit()
        else None
    )
    return rows, returned


def fetch_prng_localities(
    out_dir: Path,
) -> tuple[dict, set[str], dict[str, set[str]]]:
    feature_types = fetch_prng_feature_types()
    layer = choose_official_locality_layer(feature_types)

    all_rows: list[tuple[str, str]] = []
    page_size = 10000

    for start_index in range(0, 200000, page_size):
        query = urlencode({
            "service": "WFS",
            "version": "2.0.0",
            "request": "GetFeature",
            "typeNames": layer["name"],
            "count": page_size,
            "startIndex": start_index,
        })
        data, _ = fetch_bytes(
            PRNG_WFS + "?" + query,
            {"Accept": "application/xml"},
        )
        page_path = out_dir / f"prng-{start_index:06d}.gml"
        page_path.write_bytes(data)

        page_rows, number_returned = parse_prng_page(data)
        all_rows.extend(page_rows)

        if not page_rows:
            break
        if number_returned is not None and number_returned < page_size:
            break
        if len(page_rows) < page_size:
            break

    names: set[str] = set()
    genitives: dict[str, set[str]] = {}

    for raw_name, raw_genitive in all_rows:
        name = canonical_name(raw_name)
        if not name:
            continue

        names.add(name)
        genitive = canonical_name(raw_genitive)
        if genitive:
            genitives.setdefault(name, set()).add(genitive)

    manifest = {
        "service": PRNG_WFS,
        "layer": layer,
        "feature_type_count": len(feature_types),
        "raw_features": len(all_rows),
        "single_token_localities": len(names),
    }
    return manifest, names, genitives


def audit_source(
    kind: str,
    source_forms: set[str],
    pack_raw: set[str],
    reviewed_lower: set[str],
    variants_by_lower: dict[str, set[str]],
) -> list[dict]:
    normalized_pack = set(variants_by_lower)
    rows: list[dict] = []

    for form in sorted(source_forms):
        lower = form.lower()
        current_variants = sorted(variants_by_lower.get(lower, set()))
        if form in pack_raw:
            status = "canonical_present"
        elif lower in normalized_pack:
            status = "lowercase_only"
        else:
            status = "missing_from_pack"

        rows.append({
            "kind": kind,
            "canonical": form,
            "lower": lower,
            "status": status,
            "current_variants": current_variants,
            "reviewed": lower in reviewed_lower,
        })
    return rows


def run_morphology(
    forms: set[str],
    pack_raw: set[str],
) -> list[dict]:
    try:
        import morfeusz2
    except Exception as exc:
        return [{"status": "unavailable", "reason": repr(exc)}]

    morfeusz = morfeusz2.Morfeusz()
    normalized_pack = {word.lower() for word in pack_raw}
    output: list[dict] = []

    # Inflection coverage is actionable only when the canonical lemma itself
    # is represented by the pack. This keeps the full audit over packed proper
    # nouns tractable while still checking every generated form for those
    # lemmas.
    scoped_forms = {
        form for form in forms
        if form.lower() in normalized_pack
    }

    for lemma in sorted(scoped_forms):
        generated: set[str] = set()
        try:
            interpretations = morfeusz.generate(lemma)
        except Exception as exc:
            output.append({
                "lemma": lemma,
                "status": "error",
                "reason": repr(exc),
            })
            continue

        for interpretation in interpretations:
            if interpretation.lemma.lower() != lemma.lower():
                continue
            form = interpretation.orth
            if not is_single_token(form):
                continue
            surface = form[0].upper() + form[1:].lower()
            generated.add(surface)

        generated.add(lemma)
        missing = sorted(
            form for form in generated
            if form.lower() not in normalized_pack
        )
        present = sorted(
            form for form in generated
            if form.lower() in normalized_pack
        )
        output.append({
            "lemma": lemma,
            "status": "ok",
            "generated_forms": sorted(generated),
            "present_in_pack": present,
            "missing_from_pack": missing,
        })

    return output


def load_reviewed(path: Path) -> set[str]:
    reviewed_lower: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("\t")
        if len(parts) != 4:
            raise RuntimeError(
                f"Malformed reviewed proper-noun row: {path}: {line}"
            )
        for form in parts[1].split(";"):
            value = form.strip()
            if value:
                reviewed_lower.add(value.lower())
    return reviewed_lower


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wordlist", type=Path, required=True)
    parser.add_argument("--reviewed-proper-nouns", type=Path, required=True)
    parser.add_argument("--out-report", type=Path, required=True)
    parser.add_argument("--out-tsv", type=Path, required=True)
    parser.add_argument("--out-sources", type=Path, required=True)
    parser.add_argument("--workdir", type=Path, default=None)
    parser.add_argument("--no-morphology", action="store_true")
    args = parser.parse_args()

    workdir = args.workdir or Path(
        tempfile.mkdtemp(prefix="pl-proper-audit-")
    )
    workdir.mkdir(parents=True, exist_ok=True)

    pack_raw = {
        line.strip()
        for line in args.wordlist.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    reviewed_lower = load_reviewed(args.reviewed_proper_nouns)
    variants_by_lower: dict[str, set[str]] = {}
    for word in pack_raw:
        variants_by_lower.setdefault(word.lower(), set()).add(word)

    source_manifest = []
    name_forms: set[str] = set()
    for label, resource_id in NAMES_RES.items():
        metadata = download_dane_csv(resource_id, workdir)
        source_manifest.append({
            "source": label,
            **{key: value for key, value in metadata.items() if key != "path"},
        })
        name_forms |= parse_name_csv(Path(metadata["path"]))

    prng_manifest, place_forms, place_genitives = fetch_prng_localities(
        workdir
    )
    source_manifest.append({
        "source": "prng_official_localities",
        **prng_manifest,
    })

    name_rows = audit_source(
        "given_name", name_forms, pack_raw, reviewed_lower, variants_by_lower
    )
    place_rows = audit_source(
        "locality", place_forms, pack_raw, reviewed_lower, variants_by_lower
    )

    place_genitive_rows = []
    normalized_pack = set(variants_by_lower)
    for lemma in sorted(place_genitives):
        for form in sorted(place_genitives[lemma]):
            if form in pack_raw:
                status = "canonical_present"
            elif form.lower() in normalized_pack:
                status = "lowercase_only"
            else:
                status = "missing_from_pack"

            place_genitive_rows.append({
                "kind": "locality_genitive",
                "canonical": form,
                "lower": form.lower(),
                "status": status,
                "base_locality": lemma,
            })

    if args.no_morphology:
        morphology = []
    else:
        morphology = run_morphology(
            name_forms | place_forms,
            pack_raw,
        )

    all_rows = name_rows + place_rows + place_genitive_rows

    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    with args.out_tsv.open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            "kind",
            "canonical",
            "lower",
            "status",
            "reviewed",
            "current_variants",
            "base_locality",
        ])
        for row in all_rows:
            writer.writerow([
                row.get("kind", ""),
                row.get("canonical", ""),
                row.get("lower", ""),
                row.get("status", ""),
                str(row.get("reviewed", False)),
                ";".join(row.get("current_variants", [])),
                row.get("base_locality", ""),
            ])

    counts: dict[str, int] = {}
    for row in all_rows:
        key = f"{row['kind']}:{row['status']}"
        counts[key] = counts.get(key, 0) + 1

    report = {
        "mode": "audit-only",
        "promotion": False,
        "morphology_scope": "lemmas whose canonical lowercase form is present in the pack",
        "pack_word_count": len(pack_raw),
        "sources": source_manifest,
        "source_counts": {
            "given_names_single_token": len(name_forms),
            "official_localities_single_token": len(place_forms),
            "official_locality_genitive_forms": sum(
                len(values) for values in place_genitives.values()
            ),
        },
        "coverage": counts,
        "candidates": {
            "lowercase_only": sum(
                1 for row in all_rows if row["status"] == "lowercase_only"
            ),
            "missing_from_pack": sum(
                1 for row in all_rows if row["status"] == "missing_from_pack"
            ),
            "already_canonical": sum(
                1 for row in all_rows
                if row["status"] == "canonical_present"
            ),
            "reviewed_already": sum(
                1 for row in all_rows if row.get("reviewed")
            ),
        },
        "top_lowercase_only": sorted(
            [
                row for row in all_rows
                if row["status"] == "lowercase_only"
            ],
            key=lambda row: (row["kind"], row["canonical"]),
        )[:500],
        "top_missing": sorted(
            [
                row for row in all_rows
                if row["status"] == "missing_from_pack"
            ],
            key=lambda row: (row["kind"], row["canonical"]),
        )[:500],
        "morphology_audit": morphology,
    }

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    args.out_sources.parent.mkdir(parents=True, exist_ok=True)
    args.out_sources.write_text(
        json.dumps({
            "source_manifest": source_manifest,
            "retrieved_artifacts": sorted(
                path.name for path in workdir.iterdir()
            ),
        }, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({
        "pack_word_count": len(pack_raw),
        "given_names_single_token": len(name_forms),
        "official_localities_single_token": len(place_forms),
        "lowercase_only": report["candidates"]["lowercase_only"],
        "missing_from_pack": report["candidates"]["missing_from_pack"],
        "already_canonical": report["candidates"]["already_canonical"],
        "reviewed_already": report["candidates"]["reviewed_already"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
