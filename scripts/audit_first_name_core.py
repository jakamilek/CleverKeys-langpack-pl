#!/usr/bin/env python3
"""Audit the modern 2006-2025 first-name core against language evidence.

Audit-only. Never modifies the language pack or promotes names.
"""
from __future__ import annotations
import argparse, csv, gzip, json, re, subprocess, shutil
from pathlib import Path
from importlib.metadata import version as pkg_version

BLOCKLIST = {
    "chopin", "chopina", "goebbels", "goebbelsa",
    "catherine", "catalina", "cameron", "carli", "carlo",
    "castillo", "cali", "celli", "casino", "calli",
    "carrillo", "caroli", "cassino", "compos", "gourami",
    "celastial",
}
FOREIGN_LANGS = ("en","cs","sk","ru","uk","de","es","it","fr","pt","nl")

def parse_aosp(path: Path) -> set[str]:
    out=set()
    with gzip.open(path, "rt", encoding="utf-8") as fh:
        for raw in fh:
            m=re.search(r"(?:^|[\t ,])word=([^\t ,]+)", raw.strip())
            if m:
                out.add(m.group(1).strip('"').lower())
    return out

def hunspell_accepts(words: list[str]) -> set[str]:
    binary=shutil.which("hunspell")
    if not binary:
        raise SystemExit("hunspell missing")
    p=subprocess.run([binary,"-d","pl_PL","-G","-i","UTF-8"],
                     input="\n".join(words)+"\n",text=True,capture_output=True,
                     timeout=300,check=False)
    if p.returncode != 0:
        raise SystemExit(p.stderr[-1000:])
    return {x.strip().lower() for x in p.stdout.splitlines() if x.strip()}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--history-report",type=Path,required=True)
    ap.add_argument("--preview-wordlist",type=Path,required=True)
    ap.add_argument("--aosp",type=Path,required=True)
    ap.add_argument("--historical-first-names",type=Path,required=True)
    ap.add_argument("--out-json",type=Path,required=True)
    ap.add_argument("--out-tsv",type=Path,required=True)
    args=ap.parse_args()

    report=json.loads(args.history_report.read_text(encoding="utf-8"))
    core=[]
    for gender,key in (("F","top_female"),("M","top_male")):
        for row in report[key][:215]:
            core.append({**row,"gender":gender,"layer":"modern"})
    with args.historical_first_names.open(encoding="utf-8", newline="") as handle:
        historical_rows=list(csv.DictReader(handle, delimiter="\t"))
    if len(historical_rows)!=40 or sum(r["gender"]=="F" for r in historical_rows)!=20 or sum(r["gender"]=="M" for r in historical_rows)!=20:
        raise SystemExit("Historical first-name staging must contain exactly 20 F + 20 M rows")
    for row in historical_rows:
        core.append({
            "name":row["name"],
            "gender":row["gender"],
            "layer":"historical",
            "cumulative_rank_20y":"",
            "cumulative_count_20y":"",
            "years_present":"",
            "years_top100":"",
            "recent_5y_count":"",
            "historical_basis":row["basis"],
            "historical_source":row["source"],
            "historical_status":row["status"],
        })
    assert len(core)==470

    preview={x.strip().lower() for x in args.preview_wordlist.read_text(encoding="utf-8").splitlines()
             if x.strip() and not x.startswith("#")}
    aosp=parse_aosp(args.aosp)

    from wordfreq import zipf_frequency
    words=[r["name"].lower() for r in core]
    spell=hunspell_accepts(words)

    rows=[]
    for r in core:
        name=r["name"]; lower=name.lower()
        z=float(zipf_frequency(lower,"pl"))
        best_lang=""; best_z=0.0
        for lang in FOREIGN_LANGS:
            f=float(zipf_frequency(lower,lang))
            if f>best_z: best_lang,best_z=lang,f
        foreign = best_z>=3.0 and best_z>z+1.0
        row={
            "gender":r["gender"],"name":name,"layer":r.get("layer","modern"),
            "rank_20y":r.get("cumulative_rank_20y",""),
            "count_20y":r.get("cumulative_count_20y",""),
            "years_present":r.get("years_present",""),
            "years_top100":r.get("years_top100",""),
            "recent_5y_count":r.get("recent_5y_count",""),
            "in_preview":lower in preview,
            "hunspell":lower in spell,
            "aosp":lower in aosp,
            "zipf_pl":round(z,3),
            "common_word_signal":z>=4.0,
            "foreign_dominant_signal":foreign,
            "foreign_language":best_lang if foreign else "",
            "foreign_zipf":round(best_z,3),
            "regression_blocked":lower in BLOCKLIST,
        }
        if row["regression_blocked"]:
            row["audit_status"]="BLOCKED_REGRESSION"
        elif not row["in_preview"]:
            row["audit_status"]="NOT_IN_PREVIEW"
        elif row["foreign_dominant_signal"]:
            row["audit_status"]="IN_PREVIEW_FOREIGN_SIGNAL"
        elif row["common_word_signal"]:
            row["audit_status"]="IN_PREVIEW_COMMON_WORD_SIGNAL"
        else:
            row["audit_status"]="IN_PREVIEW_CLEAN_SIGNAL"
        rows.append(row)

    status_counts={}
    for r in rows: status_counts[r["audit_status"]]=status_counts.get(r["audit_status"],0)+1

    exceptions=[r for r in rows if r["audit_status"]!="IN_PREVIEW_CLEAN_SIGNAL"]
    out={
        "mode":"audit-only","promotion":False,
        "runtime_test_target":"CleverKeys debug 2.0.0",
        "scope":{"modern_core_per_gender":215,"historical_addition_per_gender":20,"selected_per_gender":235,"selected_total":470,"years":"2006-2025 modern layer + historical staging"},
        "evidence":{"wordfreq_version":pkg_version("wordfreq"),
                    "aosp_source":"pinned AOSP Polish dictionary used by pl-preview workflow",
                    "hunspell_dictionary":"pl_PL"},
        "counts":{"core_total":470,"female":235,"male":235,"modern_female":215,"modern_male":215,"historical_female":20,"historical_male":20,
                  "in_preview":sum(r["in_preview"] for r in rows),
                  "hunspell":sum(r["hunspell"] for r in rows),
                  "aosp":sum(r["aosp"] for r in rows),
                  "common_word_signal":sum(r["common_word_signal"] for r in rows),
                  "foreign_dominant_signal":sum(r["foreign_dominant_signal"] for r in rows),
                  "regression_blocked":sum(r["regression_blocked"] for r in rows),
                  "status_counts":status_counts},
        "exceptions":exceptions,
        "rows":rows,
    }
    args.out_json.parent.mkdir(parents=True,exist_ok=True)
    args.out_json.write_text(json.dumps(out,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    args.out_tsv.parent.mkdir(parents=True,exist_ok=True)
    with args.out_tsv.open("w",encoding="utf-8",newline="") as fh:
        w=csv.DictWriter(fh,delimiter="\t",fieldnames=list(rows[0]))
        w.writeheader(); w.writerows(rows)
    print(json.dumps({"counts":out["counts"],"exceptions":exceptions[:100]},ensure_ascii=False,indent=2))

if __name__=="__main__":
    main()
