#!/usr/bin/env python3
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "source"

files = [
    "core_words.dic",
    "colloquial.dic",
    "tech.dic",
]

words = []
for name in files:
    path = SOURCE / name
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            word = line.strip()
            if word and not word.startswith("#"):
                words.append(word)

unique = sorted(set(words))
duplicates = len(words) - len(unique)

report = {
    "dictionary_files": files,
    "entries": len(words),
    "unique_entries": len(unique),
    "duplicates": duplicates,
}

(ROOT / "build_quality.json").write_text(
    json.dumps(report, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(json.dumps(report, ensure_ascii=False))
