#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

required=(
  "source/pl_PL.aff"
  "source/core_words.dic"
  "source/colloquial.dic"
  "source/tech.dic"
  "source/corrections.txt"
)

for file in "${required[@]}"; do
  if [ ! -s "$ROOT/$file" ]; then
    echo "Missing or empty file: $file"
    exit 1
  fi
done

for file in "$ROOT"/source/*.dic; do
  if grep -q $'\r' "$file"; then
    echo "CRLF detected: $file"
    exit 1
  fi
done

if grep -R "[^[:print:]\t]" "$ROOT/source" >/dev/null 2>&1; then
  echo "Unexpected control characters found"
  exit 1
fi

echo "Dictionary validation passed"
