#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
OUT="$ROOT/build"
PACKAGE="$ROOT/cleverkeys-langpack-pl.zip"

rm -rf "$OUT"
mkdir -p "$OUT"

cat "$ROOT/source/core_words.dic" \
    "$ROOT/source/colloquial.dic" \
    "$ROOT/source/tech.dic" \
    > "$OUT/pl_PL.dic"

cp "$ROOT/source/pl_PL.aff" "$OUT/"
cp "$ROOT/source/frequency.csv" "$OUT/"
cp "$ROOT/source/custom_words.csv" "$OUT/"
cp "$ROOT/source/corrections.txt" "$OUT/"

VERSION=$(date +%Y.%m.%d)

cat > "$OUT/manifest.json" <<EOF
{
  "language": "pl-PL",
  "name": "CleverKeys Polish Language Pack",
  "version": "$VERSION",
  "encoding": "UTF-8"
}
EOF

cd "$OUT"
zip -r "$PACKAGE" .
sha256sum "$PACKAGE" > "$ROOT/cleverkeys-langpack-pl.sha256"

echo "Build complete: $PACKAGE"
