#!/usr/bin/env bash
# Record the Part 3 tutorial demo.
# Outputs: $OUT_DIR/tutorial-part3-function.cast (default: <repo>/casts/)
#
# Usage: ./scripts/record-part3.sh [output-dir]
# Requires: uv, tofu (or terraform), pyvider>=0.3.33

set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
PART_NAME="part3-function"
CAST_BASE="tutorial-part3-function"
PROVIDER_DIR="$REPO_ROOT/$PART_NAME"
OUT_DIR="${1:-$REPO_ROOT/casts}"
RAW="$OUT_DIR/$CAST_BASE.raw.cast"
OUTPUT="$OUT_DIR/$CAST_BASE.cast"

TF=""
for cmd in tofu terraform; do
  if command -v "$cmd" &>/dev/null; then TF="$cmd"; break; fi
done
if [ -z "$TF" ]; then echo "ERROR: neither tofu nor terraform on PATH." >&2; exit 1; fi

echo "→ Using: $TF"
echo "→ Provider: $PROVIDER_DIR"
echo "→ Output:   $OUTPUT"
mkdir -p "$OUT_DIR"

cd "$PROVIDER_DIR"
echo "→ Installing dependencies..."
uv sync -q

echo "→ Registering provider with Terraform..."
uv run pyvider install -q 2>/dev/null || uv run pyvider install

echo "→ Running terraform init..."
rm -rf .terraform .terraform.lock.hcl terraform.tfstate*
$TF init -upgrade -no-color -input=false >/dev/null

echo "→ Recording..."
python3 "$SCRIPT_DIR/lib/record-to-cast.py" \
  --split-lines --pause-end=3 \
  "$RAW" \
  bash -c "
    cd '$PROVIDER_DIR'
    printf '\n\033[1;32m\$\033[0m \033[1m$TF apply -auto-approve\033[0m\n'
    sleep 0.6
    $TF apply -auto-approve -no-color
    sleep 1.2
    printf '\n\033[1;32m\$\033[0m \033[1m$TF output\033[0m\n'
    sleep 0.4
    $TF output -no-color
    sleep 3
  "

python3 "$SCRIPT_DIR/lib/retime-cast.py" "$RAW" "$OUTPUT" 20
rm -f "$RAW"
echo "✅ Cast written to $OUTPUT"
