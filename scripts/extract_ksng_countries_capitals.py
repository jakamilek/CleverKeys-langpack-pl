#!/usr/bin/env python3
"""Extract Polish country and primary-capital names from the official KSNG/GUGiK PDFs."""
from __future__ import annotations
import argparse, csv, json, re
from pathlib import Path
from pypdf import PdfReader

SURFACE_RE = re.compile(r"^[A-Za-ząćęłńóśźżĄĆĘŁŃÓŚŹŻ]+$")

def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser()
    ap.add_argument("--main-pdf", type=Path, required=True)
    ap.add_argument("--update-pdf", type=Path, required=True)
    ap.add_argument("--out-countries", type=Path, required=True)
    ap.add_argument("--out-countries-flat", type=Path, required=True)
    ap.add_argument("--out-capitals", type=Path, required=True)
    ap.add_argument("--out-capitals-flat", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    return ap.parse_args()

def _normalize_abbreviations(text: str) -> str:
    """Repair PDF extractors that split short abbreviations into spaced glyphs."""
    text = re.sub(r"(?i)\\bp\\s*o\\s*l\\s*\\.", "pol.", text)
    text = re.sub(r"(?i)\\bst\\s*o\\s*l\\s*\\.", "stol.", text)
    text = re.sub(r"(?i)\\bD\\s*\\.", "D.", text)
    text = re.sub(r"(?i)\\bMc\\s*\\.", "Mc.", text)
    return text


def _score_country_markers(text: str) -> int:
    return len(re.findall(r"(?i)(?<!\\w)pol\\.\\s+", text))


def pdf_text(path: Path) -> str:
    """Extract the KSNG PDF using the text representation that preserves entries."""
    import shutil
    import subprocess

    candidates: list[tuple[str, str]] = []

    reader = PdfReader(str(path))
    for mode in ("default", "layout"):
        try:
            if mode == "layout":
                text = "\\n".join(
                    (page.extract_text(extraction_mode="layout") or "")
                    for page in reader.pages
                )
            else:
                text = "\\n".join((page.extract_text() or "") for page in reader.pages)
            candidates.append((f"pypdf-{mode}", _normalize_abbreviations(text)))
        except Exception:
            continue

    exe = shutil.which("pdftotext")
    if exe:
        for mode in ("layout", "raw"):
            try:
                args = [exe]
                if mode == "layout":
                    args.append("-layout")
                else:
                    args.append("-raw")
                args.extend([str(path), "-"])
                result = subprocess.run(
                    args,
                    check=True,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                )
                candidates.append((f"pdftotext-{mode}", _normalize_abbreviations(result.stdout)))
            except Exception:
                continue

    if not candidates:
        raise RuntimeError("No usable PDF text extraction method available")

    scored = sorted(
        ((name, text, _score_country_markers(text)) for name, text in candidates),
        key=lambda item: item[2],
        reverse=True,
    )
    print(
        "KSNG PDF extraction candidates:",
        ", ".join(f"{name}={score}" for name, _, score in scored),
    )
    best_name, best_text, best_score = scored[0]
    if best_score < 150:
        sample = [
            line for line in best_text.splitlines()
            if "pol" in line.lower()
        ][:20]
        raise RuntimeError(
            f"Could not obtain enough KSNG country markers: "
            f"best={best_name} count={best_score} sample={sample!r}"
        )
    return best_text
def normalize(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\r", "").replace("\f", "")
    return "\n".join(line.strip() for line in text.split("\n") if line.strip())

def parse_pol(block: str) -> dict[str, str]:
    m = re.search(
        r"(?<!\w)pol\.\s*(.*?)(?=\s+(?:przym|obyw|mieszk|stol)\.)",
        block,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not m:
        raise ValueError("missing Polish country section")
    v = re.sub(r"\s+", " ", m.group(1)).strip()
    name = re.split(r",\s*D\.|\s+ndm\.|;", v, maxsplit=1)[0].strip()
    gen = re.search(r"\bD\.\s+([^,;]+)", v)
    loc = re.search(r"\bMc\.\s+([^;]+)", v)
    ndm = bool(re.search(r"\bndm\.", v))
    official = v.split(";", 1)[1].strip() if ";" in v else ""
    if not name:
        raise ValueError("empty country name")
    return {"name": name, "genitive": gen.group(1).strip() if gen else "",
            "locative": loc.group(1).strip() if loc else "",
            "ndm": "yes" if ndm else "no", "official_name": official}

def parse_capital(block: str) -> dict[str, str]:
    m = re.search(r"(?<!\w)stol\.\s*(.*)$", block, flags=re.IGNORECASE | re.DOTALL)
    if not m:
        raise ValueError("missing capital section")
    v = re.sub(r"\s+", " ", m.group(1)).strip()
    name = re.split(r",\s*D\.|\s+ndm\.|;", v, maxsplit=1)[0].strip()
    gen = re.search(r"\bD\.\s+([^,;]+)", v)
    loc = re.search(r"\bMc\.\s+([^;]+)", v)
    ndm = bool(re.search(r"\bndm\.", v))
    if not name:
        raise ValueError("empty capital name")
    return {"name": name, "genitive": gen.group(1).strip() if gen else "",
            "locative": loc.group(1).strip() if loc else "",
            "ndm": "yes" if ndm else "no"}

def parse_main(text: str) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    start = text.rfind("Część I. Państwa")
    end = text.find("Część II. Terytoria niesamodzielne", start + 1)
    if start < 0 or end < 0:
        raise ValueError("Could not isolate Part I")
    section = text[start:end]
    matches = list(re.finditer(r"(?<!\w)pol\.\s+", section, flags=re.IGNORECASE))
    if len(matches) != 197:
        raise ValueError(f"Expected 197 country entries, got {len(matches)}")
    countries, capitals = [], []
    for i, m in enumerate(matches):
        block = section[m.start(): matches[i+1].start() if i+1 < len(matches) else len(section)]
        pol = parse_pol(block)
        cap = parse_capital(block)
        countries.append({
            "name": pol["name"], "official_genitive": pol["genitive"],
            "official_locative": pol["locative"], "official_ndm": pol["ndm"],
            "official_long_name": pol["official_name"], "case_policy": "capitalized",
            "source": "KSNG/GUGiK official 2025 list",
        })
        capitals.append({
            "country": pol["name"], "name": cap["name"],
            "official_genitive": cap["genitive"], "official_locative": cap["locative"],
            "official_ndm": cap["ndm"], "case_policy": "capitalized",
            "source": "KSNG/GUGiK official 2025 list",
        })
    return countries, capitals

def apply_update(capitals: list[dict[str, str]]) -> None:
    rows = [r for r in capitals if r["country"].lower() == "gwinea równikowa"]
    if len(rows) != 1:
        raise ValueError("Expected one Gwinea Równikowa entry")
    rows[0].update({
        "name": "Ciudad de la Paz", "official_genitive": "",
        "official_locative": "", "official_ndm": "yes",
        "source": "KSNG/GUGiK 2025 + update 1 (2026-01)",
    })

def write_rows(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as h:
        w = csv.DictWriter(h, fieldnames=fields, delimiter="\t", lineterminator="\n")
        w.writeheader(); w.writerows(rows)

def dedup_flat(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    out = {}; 
    for row in rows:
        if not SURFACE_RE.fullmatch(row["name"]):
            continue
        out.setdefault(row["name"].lower(), row)
    return [out[k] for k in sorted(out)]

def main() -> int:
    args = parse_args()
    countries, capitals = parse_main(normalize(pdf_text(args.main_pdf)))
    update_text = normalize(pdf_text(args.update_pdf))
    if "Ciudad de la Paz" not in update_text or "Gwinea Równikowa" not in update_text:
        raise ValueError("2026 update PDF missing expected amendment")
    apply_update(capitals)
    country_fields = ["name","official_genitive","official_locative","official_ndm",
                      "official_long_name","case_policy","source"]
    capital_fields = ["country","name","official_genitive","official_locative",
                      "official_ndm","case_policy","source"]
    write_rows(args.out_countries, countries, country_fields)
    write_rows(args.out_capitals, capitals, capital_fields)
    cf = dedup_flat(countries); kf = dedup_flat(capitals)
    write_rows(args.out_countries_flat, cf, country_fields)
    write_rows(args.out_capitals_flat, kf, capital_fields)
    report = {
        "source": "KSNG/GUGiK 2025 + update 1 (2026-01)",
        "country_records": len(countries), "capital_records": len(capitals),
        "country_flat_unique": len(cf), "capital_flat_unique": len(kf),
        "country_multi_or_non_project_alphabet": len(countries) - len(cf),
        "capital_multi_or_non_project_alphabet": len(capitals) - len(kf),
        "update_applied": "Gwinea Równikowa -> Ciudad de la Paz",
    }
    args.out_report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
