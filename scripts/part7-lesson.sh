#!/usr/bin/env bash
# Part 7: author one provider lint rule, test it, package the provider, and
# verify the packaged executable through TofuSoup's direct lane and OpenTofu's
# experimental lint validation. Every command shown is the one the README
# tells the reader to run, from inside part7-provider-linting/.
# Usage: scripts/part7-lesson.sh
set -euo pipefail

repo_root=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
tutorial="$repo_root/part7-provider-linting"
cd "$tutorial"

show_command() {
    printf '\033[1;36m$ %s\033[0m\n' "$1"
}

printf '%s\n' 'Part 7: author and verify one provider lint rule.'
printf '%s\n' 'Every command below is runnable from this checked-in tutorial directory.'
printf '\n'
show_command 'uv sync --frozen'
uv sync --frozen --quiet
printf '\n'
show_command 'uv run pytest tests/test_linting.py -q'
uv run pytest tests/test_linting.py -q
printf '\n'
show_command 'uv run flavor pack --quiet --manifest pyproject.toml'
pack_log=$(mktemp "${TMPDIR:-/tmp}/pyvider-tutorial-pack.XXXXXX")
if ! uv run flavor pack --quiet --manifest pyproject.toml >"$pack_log" 2>&1; then
    cat "$pack_log" >&2
    rm -f "$pack_log"
    exit 1
fi
rm -f "$pack_log"
printf '%s\n' 'Built and verified dist/terraform-provider-mycloud.psp'
printf '\n'
show_command 'install -m 755 dist/terraform-provider-mycloud.psp dist/terraform-provider-mycloud'
install -m 755 dist/terraform-provider-mycloud.psp dist/terraform-provider-mycloud
printf '\n'
show_command 'uvx --from tofusoup==0.8.2 soup lint lint.soup.toml --provider "$PWD/dist/terraform-provider-mycloud" --lane direct'
uvx --from tofusoup==0.8.2 soup lint lint.soup.toml \
    --provider "$PWD/dist/terraform-provider-mycloud" --lane direct
printf '\n'
show_command './install-opentofu.sh 1.13.0-rc1'
./install-opentofu.sh 1.13.0-rc1
printf '\n'
show_command 'opentofu_rc1="$PWD/.cache/opentofu/1.13.0-rc1/tofu"'
opentofu_rc1="$PWD/.cache/opentofu/1.13.0-rc1/tofu"
printf '\n'
show_command '"$opentofu_rc1" version'
"$opentofu_rc1" version
printf '\n'
show_command 'uvx --from tofusoup==0.8.2 soup lint lint.soup.toml --provider "$PWD/dist/terraform-provider-mycloud" --opentofu "$opentofu_rc1" --lane opentofu'
uvx --from tofusoup==0.8.2 soup lint lint.soup.toml \
    --provider "$PWD/dist/terraform-provider-mycloud" \
    --opentofu "$opentofu_rc1" --lane opentofu
