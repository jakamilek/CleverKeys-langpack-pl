#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPORT="$ROOT/build/report.json"

mkdir -p "$ROOT/build"

WORDS=$(cat "$ROOT"/source/*.dic 2>/dev/null | grep -v '^#' | grep -v '^$' | wc -l)
FILES=$(find "$ROOT/source" -type f | wc -l)

cat > "$REPORT" <<EOF
{
  "language": "pl-PL",
  "dictionary_files": $FILES,
  "estimated_entries": $WORDS
}
EOF

echo "Report generated: $REPORT"
