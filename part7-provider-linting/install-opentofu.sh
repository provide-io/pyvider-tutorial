#!/bin/sh

set -eu

PINNED_VERSION="1.13.0-rc1"
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
CACHE_DIR="$SCRIPT_DIR/.cache/opentofu"
VERSION=${1:-}

if [ "$VERSION" != "$PINNED_VERSION" ]; then
    printf 'usage: %s %s\n' "$0" "$PINNED_VERSION" >&2
    exit 2
fi

case "$(uname -s)" in
    Darwin) os=darwin ;;
    Linux) os=linux ;;
    *) printf 'error: unsupported operating system: %s\n' "$(uname -s)" >&2; exit 2 ;;
esac

case "$(uname -m)" in
    x86_64) arch=amd64 ;;
    arm64|aarch64) arch=arm64 ;;
    *) printf 'error: unsupported architecture: %s\n' "$(uname -m)" >&2; exit 2 ;;
esac

archive="tofu_${VERSION}_${os}_${arch}.zip"
sums="tofu_${VERSION}_SHA256SUMS"
release="https://github.com/opentofu/opentofu/releases/download/v${VERSION}"
install_dir="$CACHE_DIR/$VERSION"
binary="$install_dir/tofu"

work_dir=$(mktemp -d "${TMPDIR:-/tmp}/mycloud-opentofu.XXXXXX")
trap 'rm -rf "$work_dir"' EXIT HUP INT TERM

curl --fail --location --silent --show-error --output "$work_dir/$sums" "$release/$sums"
curl --fail --location --silent --show-error --output "$work_dir/$archive" "$release/$archive"
checksum_line=$(awk -v archive="$archive" '$2 == archive { print; found = 1; exit } END { if (!found) exit 1 }' "$work_dir/$sums")
printf '%s\n' "$checksum_line" > "$work_dir/$archive.sha256"
(
    cd "$work_dir"
    shasum -a 256 -c "$archive.sha256"
)

unzip -oq "$work_dir/$archive" tofu -d "$work_dir/extracted"
chmod +x "$work_dir/extracted/tofu"
mkdir -p "$install_dir"
mv -f "$work_dir/extracted/tofu" "$binary"
printf 'Installed OpenTofu %s (verified official SHA-256)\n' "$VERSION"
