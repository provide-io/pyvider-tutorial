# Part 7: provider linting

This self-contained `mycloud` provider adds one advisory lint rule, tests its
selector behavior, packages the provider, and verifies the same executable
through TofuSoup's direct provider lane and OpenTofu's experimental lint
validation.

```sh
uv sync --frozen
uv run pytest tests/test_linting.py -q
uv run flavor pack --quiet --manifest pyproject.toml
install -m 755 dist/terraform-provider-mycloud.psp dist/terraform-provider-mycloud

uvx --from tofusoup==0.8.2 soup lint lint.soup.toml \
  --provider "$PWD/dist/terraform-provider-mycloud" --lane direct

./install-opentofu.sh 1.13.0-rc1
opentofu_rc1="$PWD/.cache/opentofu/1.13.0-rc1/tofu"
"$opentofu_rc1" version
uvx --from tofusoup==0.8.2 soup lint lint.soup.toml \
  --provider "$PWD/dist/terraform-provider-mycloud" \
  --opentofu "$opentofu_rc1" --lane opentofu
```

The exact rule, groups, exclusions, and persistent `pyvider.toml` configuration
are explained in the matching Part 7 tutorial on pyvider.com.
