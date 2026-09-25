#!/usr/bin/env python3
"""Select production TERC inflections by administrative level and audited frequency rules.

Full Morfeusz output remains the audit source. This selector creates the production
candidate layer:
  * voivodeship: all validated singular forms;
  * gmina: nominative only;
  * powiat: all non-nominative forms observed in NKJP1M; when none is observed,
    retain one useful form chosen by grammatical case priority, with wordfreq as
    a secondary tie-break.

No combined NKJP+wordfreq score is constructed.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

CASES = ("nom", "gen", "dat", "acc", "inst", "loc", "voc")
CASE_PRIORITY = {"gen": 6, "loc": 5, "acc": 4, "inst": 3, "dat": 2, "voc": 1}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_nkjp(path: Path) -> dict[str, int]:
    result: dict[str, int] = {}
    with path.open(encoding="utf-8", errors="strict") as handle:
        for line in handle:
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 4:
                continue
            form = fields[0].strip().lower()
            try:
                count = int(fields[3])
            except ValueError:
                continue
            if form:
                result[form] = result.get(form, 0) + count
    if not result:
        raise SystemExit(f"No usable NKJP frequency rows found in {path}")
    return result


def load_full(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle, delimiter="\t"))
    required = {"name", "level", "terc", "case", "form", "case_policy", "source", "morfeusz_version"}
    if set(rows[0].keys()) != required if rows else True:
        raise SystemExit(f"Malformed TERC inflection header {path}")
    for line_no, row in enumerate(rows, 2):
        if row.get("number", "sg") != "sg" or row["case"] not in CASES or not row["form"].strip():
            raise SystemExit(f"Malformed TERC inflection row {path}:{line_no}")
    return rows


def select(rows: list[dict[str, str]], nkjp: dict[str, int], wordfreq_fn, input_path: Path, nkjp_path: Path) -> tuple[list[dict[str, str]], dict]:
    groups: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = ("terc", row["level"], row["terc"], row["name"])
        groups[key].append(row)

    selected: list[dict[str, str]] = []
    excluded: list[dict[str, str]] = []
    counts_full = Counter()
    counts_selected = Counter()

    for key in sorted(groups):
        _category, level, terc, name = key
        group = sorted(groups[key], key=lambda r: (CASES.index(r["case"]), r["form"]))
        counts_full[level] += len(group)

        nominative = [r for r in group if r["case"] == "nom"]
        if not nominative:
            raise SystemExit(f"TERC item without nominative form: {level}/{terc}/{name}")
        keep = list(nominative)

        if level == "voivodeship":
            keep.extend(r for r in group if r["case"] != "nom")
            mode = "full"
        elif level == "gmina":
            mode = "nominative-only"
        elif level == "powiat":
            observed = [
                r for r in group
                if r["case"] != "nom" and nkjp.get(r["form"].lower(), 0) > 0
            ]
            if observed:
                keep.extend(observed)
                mode = "nkjp-observed"
            else:
                available = [r for r in group if r["case"] != "nom"]
                if available:
                    fallback = max(
                        available,
                        key=lambda r: (
                            float(wordfreq_fn(r["form"], "pl")),
                            CASE_PRIORITY[r["case"]],
                            -CASES.index(r["case"]),
                            r["form"],
                        ),
                    )
                    keep.append(fallback)
                    mode = "weighted-fallback"
                else:
                    mode = "nominative-only-no-non-nom"
        else:
            raise SystemExit(f"Unknown TERC level {level!r}")

        keep_keys = {(r["case"], r["form"]) for r in keep}
        for row in group:
            marker = dict(row)
            if (row["case"], row["form"]) in keep_keys:
                marker["retention"] = mode
                selected.append(marker)
                counts_selected[level] += 1
            else:
                marker["retention"] = (
                    "excluded-gmina-nominative-only"
                    if level == "gmina" and row["case"] != "nom"
                    else "excluded-powiat-frequency-not-observed"
                )
                excluded.append(marker)

    report = {
        "policy": {
            "voivodeship": "retain all validated singular forms",
            "powiat": "retain all non-nominative forms observed in NKJP1M; if none observed, retain one useful non-nominative form using wordfreq as secondary signal and CASE_PRIORITY as grammatical weight",
            "gmina": "retain nominative only",
            "nkjp_primary": True,
            "wordfreq_secondary": True,
            "combined_score": False,
            "case_priority": CASE_PRIORITY,
        },
        "source": {
            "full_inflections_sha256": sha256(input_path),
            "nkjp_sha256": sha256(nkjp_path),
        },
        "full_records_by_level": dict(counts_full),
        "selected_records_by_level": dict(counts_selected),
        "selected_record_count": len(selected),
        "excluded_record_count": len(excluded),
        "powiat_fallback_records": sum(1 for r in selected if r["retention"] == "weighted-fallback"),
        "powiat_observed_records": sum(1 for r in selected if r["retention"] == "nkjp-observed"),
        "excluded_examples": excluded[:100],
    }
    return selected, report


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", type=Path, required=True)
    ap.add_argument("--nkjp", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--out-report", type=Path, required=True)
    args = ap.parse_args()

    from wordfreq import zipf_frequency

    rows = load_full(args.input)
    selected, report = select(rows, load_nkjp(args.nkjp), zipf_frequency, args.input, args.nkjp)

    fields = list(rows[0].keys()) + ["retention"]
    with args.out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(selected)

    args.out_report.parent.mkdir(parents=True, exist_ok=True)
    args.out_report.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({
        "full_records_by_level": report["full_records_by_level"],
        "selected_records_by_level": report["selected_records_by_level"],
        "selected_record_count": report["selected_record_count"],
        "excluded_record_count": report["excluded_record_count"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
