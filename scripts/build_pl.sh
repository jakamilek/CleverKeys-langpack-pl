#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build"

mkdir -p "$OUT"

cp "$ROOT/source/pl_PL.dic" "$OUT/"
cp "$ROOT/source/pl_PL.aff" "$OUT/"
cp "$ROOT/source/frequency.csv" "$OUT/"
cp "$ROOT/source/custom_words.csv" "$OUT/"

cd "$OUT"
zip -r ../cleverkeys-langpack-pl.zip .
sha256sum ../cleverkeys-langpack-pl.zip > ../cleverkeys-langpack-pl.sha256

echo "Build complete"
