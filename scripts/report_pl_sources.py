#!/usr/bin/env python3
"""
Report-only audit of the controlled Polish CleverKeys source stack.

This script never writes source/ dictionary data and never promotes anything.
It measures the pinned wordfreq candidate stream against optional AOSP and
Hunspell evidence. The generated JSON is an audit artifact, not a production
dictionary.

Expected build-time dependencies:
  pip install "git+https://github.com/rspeer/wordfreq@912caf64b657478d1dff113eefdc078947d54bb1"

Optional external oracle:
  hunspell with the pl_PL dictionary installed.

Optional AOSP snapshot:
  the controlled AOSP pl_wordlist.combined.gz. The loader accepts either the
  CleverKeys transformed headword<TAB>flags format or the upstream combined
  format containing word=... records.
"""

from __future__ import annotations

import argparse
import gzip
import importlib.metadata
import json
import re
import shutil
import subprocess
from pathlib import Path

POLISH_ALPHABET = set("aąbcćdeęfghijklłmnńoóprsśtuwyzźż")
WORD_RE = re.compile(r"^[a-ząćęłńóśźż]+$", re.IGNORECASE)
EXPECTED_WORDFREQ_COMMIT = "912caf64b657478d1dff1138efdc078947d54bb1"
EXPECTED_WORDFREQ_DATA_SHA = "3be96f3eacf5b8d886a2df3eeb9d4e893212eef5"


def load_wordfreq():
    try:
        from wordfreq import iter_wordlist, zipf_frequency  # type: ignore
    except ImportError as exc:
        raise SystemExit(
            "wordfreq is required. Install the pinned build-time source: "
            "git+https://github.com/rspeer/wordfreq@"
            + EXPECTED_WORDFREQ_COMMIT
        ) from exc
    try:
        version = importlib.metadata.version("wordfreq")
    except importlib.metadata.PackageNotFoundError:
        version = "unknown"
    return iter_wordlist, zipf_frequency, version


def is_polish_candidate(word: str) -> bool:
    if not (2 <= len(word) <= 25):
        return False
    if not word.isalpha() or not WORD_RE.fullmatch(word):
        return False
    return all(ch.lower() in POLISH_ALPHABET for ch in word)


def load_aosp(path: Path) -> tuple[set[str], dict[str, int]]:
    opener = gzip.open if path.suffix == ".gz" else open
    words: set[str] = set()
    stats = {"lines": 0, "word_marked": 0, "plain_candidates": 0, "parsed": 0}
    with opener(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            stats["lines"] += 1
            line = line.strip()
            if not line:
                continue

            if "word=" in line:
                stats["word_marked"] += 1
                match = re.search(r"(?:^|[\\t ,])word=([^\\t ,]+)", line)
                head = match.group(1) if match else ""
            else:
                head = line.split("\\t", 1)[0].strip()

            word = head.strip().strip('"').lower()
            if is_polish_candidate(word):
                if "word=" not in line:
                    stats["plain_candidates"] += 1
                words.add(word)
    stats["parsed"] = len(words)
    return words, stats


def hunspell_accepts(words: list[str]) -> tuple[set[str], dict[str, object]]:
    binary = shutil.which("hunspell")
    meta: dict[str, object] = {"available": bool(binary), "dictionary": "pl_PL"}
    if not binary:
        meta["status"] = "missing"
        return set(), meta

    proc = subprocess.run(
        [binary, "-d", "pl_PL", "-G", "-i", "UTF-8"],
        input="\n".join(words) + "\n",
        text=True,
        capture_output=True,
        timeout=600,
        check=False,
    )
    meta["returncode"] = proc.returncode
    if proc.returncode != 0:
        meta["status"] = "failed"
        meta["stderr"] = proc.stderr[-1000:]
        return set(), meta

    accepted = {line.strip().lower() for line in proc.stdout.splitlines() if line.strip()}
    meta["status"] = "ok"
    meta["accepted"] = len(accepted)
    return accepted, meta


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--top", type=int, default=100000)
    ap.add_argument("--aosp", type=Path)
    ap.add_argument("--out", type=Path, default=Path("build/pl-source-audit.json"))
    ap.add_argument("--require-hunspell", action="store_true")
    ap.add_argument("--require-aosp", action="store_true")
    args = ap.parse_args()

    iter_wordlist, zipf_frequency, wf_version = load_wordfreq()

    ranked: list[str] = []
    seen: set[str] = set()
    rejected_script = 0
    for word in iter_wordlist("pl"):
        candidate = word.lower()
        if candidate in seen:
            continue
        if is_polish_candidate(candidate):
            seen.add(candidate)
            ranked.append(candidate)
            if len(ranked) >= args.top:
                break
        else:
            rejected_script += 1

    aosp, aosp_stats = load_aosp(args.aosp) if args.aosp else (set(), {"lines": 0, "word_marked": 0, "plain_candidates": 0, "parsed": 0})
    hunspell, hunspell_meta = hunspell_accepts(ranked)

    if args.require_hunspell and hunspell_meta.get("status") != "ok":
        raise SystemExit("Required Polish Hunspell oracle is unavailable or failed.")
    if args.require_aosp and not args.aosp:
        raise SystemExit("Required AOSP snapshot was not supplied.")

    diacritic_words = [w for w in ranked if any(c in "ąęćłńóśźż" for c in w)]
    aosp_overlap = set(ranked) & aosp

    top_examples = [
        {"word": word, "zipf": round(float(zipf_frequency(word, "pl")), 2)}
        for word in ranked[:100]
    ]

    result = {
        "mode": "report-only",
        "wordfreq": {
            "expected_source_commit": EXPECTED_WORDFREQ_COMMIT,
            "expected_polish_data_blob_sha": EXPECTED_WORDFREQ_DATA_SHA,
            "installed_package_version": wf_version,
            "candidate_count": len(ranked),
        },
        "candidate_filter": {
            "min_length": 2,
            "max_length": 25,
            "alphabet": "".join(sorted(POLISH_ALPHABET)),
            "non_polish_tokens_seen": rejected_script,
        },
        "oracles": {
            "aosp": {
                "supplied": bool(args.aosp),
                "path": str(args.aosp) if args.aosp else None,
                "overlap": len(aosp_overlap),
                "coverage_basis": aosp_stats,
                "candidate_coverage": round(100 * len(aosp_overlap) / len(ranked), 2)
                if ranked else 0.0,
            },
            "hunspell": {
                **hunspell_meta,
                "candidate_coverage": round(100 * len(hunspell) / len(ranked), 2)
                if ranked else 0.0,
            },
        },
        "polish_diacritics": {
            "forms_with_diacritics": len(diacritic_words),
            "note": "Accent aliases are runtime lookup behaviour; canonical dictionary entries keep Polish diacritics.",
        },
        "top_examples": top_examples,
        "promotion": {
            "approved": False,
            "reason": "Report-only audit; no source promotion or dictionary generation.",
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
