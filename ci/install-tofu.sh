#!/usr/bin/env bash
# Install OpenTofu binary directly (no node/JS actions required).
# Used by act and other container-based CI runners.
set -euo pipefail

TOFU_VERSION="${TOFU_VERSION:-1.10.6}"
OS="$(uname -s | tr '[:upper:]' '[:lower:]')"
ARCH="$(uname -m)"
case "$ARCH" in
  x86_64)  ARCH="amd64" ;;
  aarch64) ARCH="arm64" ;;
esac

URL="https://github.com/opentofu/opentofu/releases/download/v${TOFU_VERSION}/tofu_${TOFU_VERSION}_${OS}_${ARCH}.zip"

echo "Installing OpenTofu ${TOFU_VERSION} (${OS}/${ARCH})..."
curl -fsSL "$URL" -o /tmp/tofu.zip
unzip -o /tmp/tofu.zip -d /usr/local/bin tofu
chmod +x /usr/local/bin/tofu
rm /tmp/tofu.zip
tofu --version
