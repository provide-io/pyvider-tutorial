#!/usr/bin/env bash
# Run the full Terraform lifecycle for a tutorial part.
# Usage: ci/run-tutorial-part.sh <part-number>
# Example: ci/run-tutorial-part.sh 1
set -euo pipefail

PART_NUM="${1:?Usage: $0 <part-number>}"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

case "$PART_NUM" in
  1) PART_DIR="part1-resource" ;;
  2) PART_DIR="part2-data-source" ;;
  3) PART_DIR="part3-function" ;;
  4) PART_DIR="part4-ephemeral" ;;
  5) PART_DIR="part5-deploy" ;;
  # Part 7 is a lint-and-package walkthrough, not an apply lifecycle.
  7) exec "$REPO_ROOT/scripts/part7-lesson.sh" ;;
  *) echo "ERROR: Unknown part number: $PART_NUM (expected 1-5 or 7)" >&2; exit 1 ;;
esac

PROVIDER_DIR="$REPO_ROOT/$PART_DIR"

TF=""
for cmd in tofu terraform; do
  if command -v "$cmd" &>/dev/null; then TF="$cmd"; break; fi
done
if [ -z "$TF" ]; then echo "ERROR: neither tofu nor terraform on PATH." >&2; exit 1; fi

echo "=== Part $PART_NUM: $PART_DIR ==="
echo "  Using: $TF"

cd "$PROVIDER_DIR"

echo "  Installing dependencies..."
uv sync -q

if [ "$PART_NUM" = "5" ]; then
  # Part 5: build a distributable binary with flavorpack.
  echo "  Building provider binary..."
  uv run flavor pack --manifest pyproject.toml
  mv dist/terraform-provider-mycloud.psp dist/terraform-provider-mycloud
  chmod +x dist/terraform-provider-mycloud

  # Install the binary to the Terraform plugin directory.
  PLATFORM="$(uname -s | tr '[:upper:]' '[:lower:]')_$(uname -m | sed 's/x86_64/amd64/;s/aarch64/arm64/')"
  PLUGIN_DIR="$HOME/.terraform.d/plugins/local/providers/mycloud/0.1.0/$PLATFORM"
  mkdir -p "$PLUGIN_DIR"
  cp dist/terraform-provider-mycloud "$PLUGIN_DIR/terraform-provider-mycloud"
  chmod +x "$PLUGIN_DIR/terraform-provider-mycloud"
  echo "  Installed binary to $PLUGIN_DIR"
else
  echo "  Registering provider..."
  uv run pyvider install -q 2>/dev/null || uv run pyvider install
fi

echo "  Running $TF init..."
rm -rf .terraform .terraform.lock.hcl terraform.tfstate*
$TF init -upgrade -no-color -input=false >/dev/null

echo "  Running $TF apply..."
$TF apply -auto-approve -no-color

echo "  Running $TF output..."
$TF output -no-color

echo "  Part $PART_NUM passed."
