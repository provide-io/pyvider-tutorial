#!/usr/bin/env bash
# Record all five tutorial parts in sequence.
# Usage: ./scripts/record-all.sh [output-dir]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUT_DIR="${1:-$(dirname "$SCRIPT_DIR")/casts}"
for n in 1 2 3 4 5; do
  echo "=== Recording part $n ==="
  "$SCRIPT_DIR/record-tutorial-part.sh" "$n" "$OUT_DIR"
done
