#!/usr/bin/env python3
"""Audit selected first names for homonymy with Polish common nouns.

This is an audit/gating tool only. It never copies Morfeusz/SGJP data into the
distributable language pack. A selected first name is a common-noun homonym when
its lowercase orthographic form receives at least one SGJP/Morfeusz analysis
tagged as a noun (subst:...) and classified as `nazwa_pospolita`.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

COMMON_NOUN_CLASS = "nazwa_pospolita"


def selected_names(history_report: Path, historical_tsv: Path) -> list[dict[str, str]]:
    report = json.loads(history_report.read_text(encoding="utf-8"))
    rows: list[dict[str, str]] = []
    for gender, key in (("F", "top_female"), ("M", "top_male")):
        for item in report[key][:215]:
            rows.append({"gender": gender, "name": str(item["name"]).strip(), "layer": "modern"})
    with historical_tsv.open(encoding="utf-8", newline="") as handle:
        for item in csv.DictReader(handle, delimiter="\t"):
            rows.append({
                "gender": item["gender"],
                "name": item["name"].strip(),
                "layer": "historical",
            })
    if len(rows) != 470 or sum(r["gender"] == "F" for r in rows) != 235 or sum(r["gender"] == "M" for r in rows) != 235:
        raise SystemExit("Expected exactly 470 names: 235 F + 235 M")
    return rows


def analyse_name(morfeusz, name: str) -> list[dict]:
    analyses = morfeusz.analyse(name.lower())
    out: list[dict] = []
    for item in analyses:
        if len(item) < 3:
            continue
        payload = item[2]
        if not isinstance(payload, (tuple, list)) or len(payload) < 4:
            continue
        orth = str(payload[0])
        lemma = str(payload[1])
        tag = str(payload[2])
        classes = payload[3] if isinstance(payload[3], (tuple, list)) else []
        classes = [str(x) for x in classes]
        if tag.startswith("subst:") and COMMON_NOUN_CLASS in classes:
            out.append({
                "orth": orth,
                "lemma": lemma,
                "tag": tag,
                "classes": classes,
            })
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--history-report", type=Path, required=True)
    ap.add_argument("--historical-first-names", type=Path, required=True)
    ap.add_argument("--out-json", type=Path, required=True)
    ap.add_argument("--out-tsv", type=Path, required=True)
    ap.add_argument("--out-blocklist", type=Path, required=True)
    ap.add_argument("--surface-policy", type=Path, required=True)
    args = ap.parse_args()

    import morfeusz2

    morfeusz = morfeusz2.Morfeusz()
    surface_policy: dict[str, str] = {}
    with args.surface_policy.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            surface_policy[row["name"].strip().lower()] = row["policy"].strip()
    selected = selected_names(args.history_report, args.historical_first_names)

    rows: list[dict] = []
    for item in selected:
        matches = analyse_name(morfeusz, item["name"])
        rows.append({
            **item,
            "common_noun_homonym": bool(matches),
            "surface_policy": surface_policy.get(item["name"].lower(), "capitalized_name"),
            "matches": matches,
        })

    homonyms = [r for r in rows if r["common_noun_homonym"]]
    homonym_names = sorted({r["name"].lower() for r in homonyms})
    lowercase = sorted(
        r["name"].lower() for r in homonyms
        if r["surface_policy"] == "lowercase_common_noun"
    )
    capitalized = sorted(
        r["name"].lower() for r in homonyms
        if r["surface_policy"] == "capitalized_name"
    )
    excluded = sorted(
        r["name"].lower() for r in selected
        if r["name"].lower() in surface_policy and surface_policy[r["name"].lower()] == "exclude"
    )

    summary = {
        "mode": "audit-and-gate",
        "oracle": "Morfeusz 2 / SGJP",
        "morfeusz_version": morfeusz2.Morfeusz().getVersion() if hasattr(morfeusz2.Morfeusz, "getVersion") else "unknown",
        "rule": "lowercase selected-name form has a noun (subst:...) analysis classified as nazwa_pospolita",
        "selected_total": len(rows),
        "selected_female": sum(r["gender"] == "F" for r in rows),
        "selected_male": sum(r["gender"] == "M" for r in rows),
        "common_noun_homonym_count": len(homonyms),
        "common_noun_homonym_female": sum(r["gender"] == "F" for r in homonyms),
        "common_noun_homonym_male": sum(r["gender"] == "M" for r in homonyms),
        "homonym_names": homonym_names,
        "lowercase_common_noun_names": lowercase,
        "capitalized_homonym_names": capitalized,
        "excluded_names": excluded,
        "non_homonym_count": len(rows) - len(homonyms),
        "rows": rows,
    }

    args.out_json.parent.mkdir(parents=True, exist_ok=True)
    args.out_tsv.parent.mkdir(parents=True, exist_ok=True)
    args.out_json.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    args.out_blocklist.parent.mkdir(parents=True, exist_ok=True)
    args.out_blocklist.write_text("\n".join(capitalized) + ("\n" if capitalized else ""), encoding="utf-8")

    with args.out_tsv.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow([
            "gender", "name", "layer", "common_noun_homonym",
            "matches",
        ])
        for row in rows:
            writer.writerow([
                row["gender"],
                row["name"],
                row["layer"],
                str(row["common_noun_homonym"]).lower(),
                json.dumps(row["matches"], ensure_ascii=False, separators=(",", ":")),
            ])

    print(json.dumps({
        k: summary[k]
        for k in (
            "morfeusz_version",
            "selected_total",
            "selected_female",
            "selected_male",
            "common_noun_homonym_count",
            "common_noun_homonym_female",
            "common_noun_homonym_male",
            "blocked_names",
        )
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
