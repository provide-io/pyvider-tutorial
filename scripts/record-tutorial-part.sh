#!/usr/bin/env bash
# Record the Terraform lifecycle for a tutorial part as an asciinema cast.
# Usage: ci/record-tutorial-part.sh <part-number> [output-dir]
# Output: <output-dir>/tutorial-part<N>-<name>.cast
set -euo pipefail

PART_NUM="${1:?Usage: $0 <part-number> [output-dir]}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
# Resolve to absolute path so recording subprocess can find it.
OUT_DIR="${2:-$REPO_ROOT/casts}"
case "$OUT_DIR" in
  /*) ;;
  *)  OUT_DIR="$PWD/$OUT_DIR" ;;
esac

case "$PART_NUM" in
  1) PART_DIR="part1-resource";    CAST_BASE="tutorial-part1-resource"    TITLE="Building your first resource" ;;
  2) PART_DIR="part2-data-source"; CAST_BASE="tutorial-part2-data-source" TITLE="Building your first data source" ;;
  3) PART_DIR="part3-function";    CAST_BASE="tutorial-part3-function"    TITLE="Building your first function" ;;
  4) PART_DIR="part4-ephemeral";   CAST_BASE="tutorial-part4-ephemeral"   TITLE="Building your first ephemeral resource" ;;
  5) PART_DIR="part5-deploy";      CAST_BASE="tutorial-part5-deploy"      TITLE="Deploying your provider as a binary" ;;
  6) PART_DIR="part6-protocol-611"; CAST_BASE="tutorial-part6-protocol-611" TITLE="Protocol 6.11: actions and list resources" ;;
  7) PART_DIR="part7-provider-linting"; CAST_BASE="tutorial-part7-provider-linting" TITLE="Part 7 — author and verify a provider lint rule" ;;
  *) echo "ERROR: Unknown part number: $PART_NUM (expected 1-7)" >&2; exit 1 ;;
esac

PROVIDER_DIR="$REPO_ROOT/$PART_DIR"
RAW="$OUT_DIR/$CAST_BASE.raw.cast"
OUTPUT="$OUT_DIR/$CAST_BASE.cast"
RECORD_SCRIPT="$REPO_ROOT/scripts/lib/record-to-cast.py"
RETIME_SCRIPT="$REPO_ROOT/scripts/lib/retime-cast.py"

# Part 7 installs its own OpenTofu; every other part needs one on PATH.
TF=""
if [ "$PART_NUM" != "7" ]; then
  for cmd in tofu terraform; do
    if command -v "$cmd" &>/dev/null; then TF="$cmd"; break; fi
  done
  if [ -z "$TF" ]; then echo "ERROR: neither tofu nor terraform on PATH." >&2; exit 1; fi
fi

mkdir -p "$OUT_DIR"
cd "$PROVIDER_DIR"

if [ "$PART_NUM" = "7" ]; then
  # Part 7: record the whole lint walkthrough, then retime it to 38 seconds.
  echo "  Recording $CAST_BASE..."
  python3 "$RECORD_SCRIPT" \
    --split-lines --pause-end=3 --title="$TITLE" \
    "$RAW" \
    "$REPO_ROOT/scripts/part7-lesson.sh"
  RECORD_EXIT=$?

  python3 "$RETIME_SCRIPT" "$RAW" "$OUTPUT" 38
  rm -f "$RAW"
elif [ "$PART_NUM" = "5" ]; then
  # Part 5: record the full build-to-deploy flow.
  # The binary must already be built and installed by run-tutorial-part.sh.
  # We re-use that binary (not rebuild) because each flavor pack generates
  # fresh signing keys, and a new build would invalidate the PSPF cache.
  rm -rf .terraform .terraform.lock.hcl
  rm -f terraform.tfstate terraform.tfstate.backup

  # Verify the binary exists from the run step.
  if [ ! -f dist/terraform-provider-mycloud ]; then
    echo "ERROR: dist/terraform-provider-mycloud not found — run ci/run-tutorial-part.sh 5 first" >&2
    exit 1
  fi

  PLATFORM="$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')"
  PLUGIN_DIR="$HOME/.terraform.d/plugins/local/providers/mycloud/0.1.0/$PLATFORM"

  echo "  Recording $CAST_BASE..."
  python3 "$RECORD_SCRIPT" \
    --split-lines --pause-end=3 --title="$TITLE" \
    "$RAW" \
    bash -c "
      cd '$PROVIDER_DIR'

      printf '\n\033[1;32m\$\033[0m \033[1mflavor pack\033[0m\n'
      sleep 0.6
      uv run flavor pack --manifest pyproject.toml 2>&1
      sleep 1.2

      printf '\n\033[1;32m\$\033[0m \033[1mmkdir -p $PLUGIN_DIR && cp dist/terraform-provider-mycloud \$PLUGIN_DIR/\033[0m\n'
      sleep 0.4
      mkdir -p '$PLUGIN_DIR'
      cp dist/terraform-provider-mycloud '$PLUGIN_DIR/terraform-provider-mycloud'
      chmod +x '$PLUGIN_DIR/terraform-provider-mycloud'
      printf '  Installed to %s\n' '$PLUGIN_DIR'
      sleep 1.2

      printf '\n\033[1;32m\$\033[0m \033[1m$TF init\033[0m\n'
      sleep 0.4
      $TF init -upgrade -no-color -input=false
      sleep 1.2

      printf '\n\033[1;32m\$\033[0m \033[1m$TF apply -auto-approve\033[0m\n'
      sleep 0.6
      $TF apply -auto-approve -no-color
      sleep 1.2

      printf '\n\033[1;32m\$\033[0m \033[1m$TF output\033[0m\n'
      sleep 0.4
      $TF output -no-color
      sleep 3
    "
  RECORD_EXIT=$?

  # Part 5 is longer — retime to 30 seconds.
  python3 "$RETIME_SCRIPT" "$RAW" "$OUTPUT" 30
  rm -f "$RAW"
else
  # Parts 1-4: record just the apply/output lifecycle.
  # Provider must already be installed by run-tutorial-part.sh.
  # Clean Terraform state but keep .terraform/ so the provider binary is cached.
  # Run a plan to force provider extraction before recording starts.
  rm -f terraform.tfstate*
  $TF init -upgrade -no-color -input=false >/dev/null
  $TF plan -no-color -input=false >/dev/null 2>&1

  echo "  Recording $CAST_BASE..."
  python3 "$RECORD_SCRIPT" \
    --split-lines --pause-end=3 --title="$TITLE" \
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
  RECORD_EXIT=$?

  # Retime to 20 seconds for website playback.
  python3 "$RETIME_SCRIPT" "$RAW" "$OUTPUT" 20
  rm -f "$RAW"
fi

echo "  Cast written to $OUTPUT"
exit "$RECORD_EXIT"
