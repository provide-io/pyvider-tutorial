# pyvider-tutorial

Runnable provider code for the **Building a Provider from Scratch** tutorial
series at [pyvider.com/posts](https://pyvider.com/posts/building-your-first-provider/).

Each step adds exactly one new concept to a small `mycloud` provider:

| Step | Directory | Blog post | Adds |
|------|-----------|-----------|------|
| 1 | [`part1-resource/`](part1-resource) | [Building Your First Terraform Provider](https://pyvider.com/posts/building-your-first-provider/) | A `mycloud_server` resource with full CRUD. |
| 2 | [`part2-data-source/`](part2-data-source) | [Building Your First Data Source](https://pyvider.com/posts/building-your-first-data-source/) | A `mycloud_server_info` data source over the same server model. |
| 3 | [`part3-function/`](part3-function) | [Building Your First Provider Function](https://pyvider.com/posts/building-your-first-function/) | A `provider::mycloud::generate_name(...)` HCL-callable function. |
| 4 | [`part4-ephemeral/`](part4-ephemeral) | [Building Your First Ephemeral Resource](https://pyvider.com/posts/building-your-first-ephemeral-resource/) | A `mycloud_session_token` ephemeral with the `open → renew → close` lifecycle. |
| 5 | [`part5-deploy/`](part5-deploy) | [Deploying Your Provider as a Binary](https://pyvider.com/posts/deploying-your-provider/) | Package the provider as a single-file executable with Flavorpack — no Python, no venv, no install step on the consumer side. |

Parts 1–4 are each a self-contained, uv-managed Python package that provides
`terraform-provider-mycloud`, a fully functional local Terraform provider.
Each is a clean superset of the previous one so you can diff your way forward.
Part 5 takes the part-4 provider and packages it for binary distribution
via Flavorpack.

## Prerequisites

- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/)
- [`tofu`](https://opentofu.org) (or `terraform`)
- [`pyvider`](https://pypi.org/project/pyvider/) `>=0.3.33` (installed automatically via `uv sync`)

## Running a step

```bash
cd part1-resource
uv sync                        # install pyvider into a local venv
uv run pyvider install         # register terraform-provider-mycloud
tofu init -upgrade             # or: terraform init -upgrade
tofu apply -auto-approve       # or: terraform apply -auto-approve
```

Each part's `main.tf` shows the Terraform surface that step introduces.

## Recording the asciinema casts

The `scripts/` directory contains the same recording pipeline used to
produce the casts embedded in the blog posts. The outputs go to
`./casts/` by default (override with an explicit output directory).

```bash
./scripts/record-tutorial-part.sh 1         # record just part 1 → ./casts/
./scripts/record-tutorial-part.sh 5 /tmp    # record part 5 to /tmp
./scripts/record-all.sh                     # record all 5 parts in sequence
```

`record-tutorial-part.sh <N>` accepts 1–5 and is the same script CI uses
to produce the casts embedded in the blog posts. Part 5 uses a different
flow under the hood (`flavor pack` to build a binary, then `tofu apply`
against the binary) but the entry point is the same.

Requires `asciinema` and Python 3 on PATH.

## License

Apache 2.0. See [LICENSE](LICENSE).
