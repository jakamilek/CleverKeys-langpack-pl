#!/usr/bin/env python3
"""
Report-only audit of the controlled Polish CleverKeys source stack.

This script never writes source/ dictionary data and never promotes anything.
It measures the pinned wordfreq candidate stream against optional AOSP and
Hunspell evidence. The generated JSON is an audit artifact, not a production
dictionary.

Expected build-time dependencies:
  pip install "git+https://github.com/rspeer/wordfreq@912caf64b657478d1dff1138efdc078947d54bb1"

Optional external oracle:
  hunspell with the pl_PL dictionary installed.

Optional AOSP snapshot:
  the controlled, transformed AOSP file recorded in CleverKeys provenance:
  headword<TAB>flags, gzip-compressed or plain UTF-8.
"""

from __future__ import annotations

import argparse
import gzip
import importlib.metadata
import json
import re
import shutil
import subprocess
import sys
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


def load_aosp(path: Path) -> set[str]:
    opener = gzip.open if path.suffix == ".gz" else open
    words: set[str] = set()
    with opener(path, "rt", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            head = line.split("\t", 1)[0].strip().lower()
            if is_polish_candidate(head):
                words.add(head)
    return words


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
        w = word.lower()
        if w in seen:
            continue
        if is_polish_candidate(w):
            seen.add(w)
            ranked.append(w)
            if len(ranked) >= args.top:
                break
        else:
            rejected_script += 1

    aosp = load_aosp(args.aosp) if args.aosp else set()
    hunspell, hunspell_meta = hunspell_accepts(ranked)

    if args.require_hunspell and hunspell_meta.get("status") != "ok":
        raise SystemExit("Required Polish Hunspell oracle is unavailable or failed.")
    if args.require_aosp and not args.aosp:
        raise SystemExit("Required AOSP snapshot was not supplied.")

    diacritic_words = [w for w in ranked if any(c in "ąęćłńóśźż" for c in w)]
    ascii_aliases = sum(
        1
        for w in diacritic_words
        if all(ord(c) < 128 for c in w.translate(str.maketrans("ąęćłńóśźż", "a e c l n o s z z".replace(" ", ""))))
    )

    top_examples = [
        {"word": w, "zipf": round(float(zipf_frequency(w, "pl")), 2)}
        for w in ranked[:100]
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
                "overlap": len(set(ranked) & aosp),
                "candidate_coverage": round(100 * len(set(ranked) & aosp) / len(ranked), 2)
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
