# ── Protocol 6.11: a list resource. ─────────────────────────────────────────
#
# `list` blocks live in a .tfquery.hcl file, not in main.tf, and they run under
# `terraform query` rather than plan or apply. Nothing here is created or
# destroyed — the command asks the provider what already exists.
#
# The terraform{} and provider{} blocks are *not* repeated here: a .tfquery.hcl
# file shares the configuration of the directory it sits in, and declaring them
# again is a duplicate-provider error.
#
# Before 6.11, showing a caller their existing infrastructure meant writing a
# data source per resource type and inventing a shape for the results. A list
# resource answers Terraform's ListResource RPC instead, and describes each
# result with the *identity* schema of a managed resource you already wrote —
# which is how Terraform ties a listed instance back to `mycloud_server`.
#
# Needs Terraform 1.14+. OpenTofu 1.12 rejects `list` with "Unsupported block
# type" and has no `query` subcommand.

# Every server the provider knows about.
list "mycloud_server" "all" {
  provider = mycloud

  config {}
}

# The same list resource, filtered. `status` is the one optional attribute in
# its schema; the provider validates it and rejects anything but running or
# stopped.
list "mycloud_server" "running_only" {
  provider = mycloud

  config {
    status = "running"
  }
}
