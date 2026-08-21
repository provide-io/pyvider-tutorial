terraform {
  required_providers {
    mycloud = {
      source  = "local/providers/mycloud"
      version = "0.1.0"
    }
  }
}

provider "mycloud" {}

locals {
  server_name = provider::mycloud::generate_name("web", "prod")
}

# ── Everything below the action block is protocol 6.0 and runs anywhere. ──────

resource "mycloud_server" "web" {
  name = local.server_name

  # An action is attached to a resource through its lifecycle, not called like a
  # function. `events` decides when it runs; `after_create` fires once, right
  # after this server is created.
  #
  # This is the part that needs Terraform 1.14+. OpenTofu 1.12 rejects the
  # `action` block outright with "Unsupported block type".
  lifecycle {
    action_trigger {
      events  = [after_create]
      actions = [action.mycloud_restart_server.smoke_test]
    }
  }
}

# ── Protocol 6.11: an action. ────────────────────────────────────────────────
#
# An action is the imperative operation that is not "make reality match this
# configuration" — restart a node, rotate a credential, trigger a run. Before
# 6.11 these were modelled as resources with a trigger attribute, which put an
# imperative verb in a declarative graph and left state describing something
# that had already finished.
#
# It has no state and produces no diff. What it does produce is progress: our
# implementation streams three `ActionProgress` messages, which Terraform prints
# as the action runs.
action "mycloud_restart_server" "smoke_test" {
  config {
    server_id = mycloud_server.web.id
  }
}

data "mycloud_server_info" "web" {
  server_id = mycloud_server.web.id
}

output "server_name"   { value = local.server_name }
output "server_id"     { value = mycloud_server.web.id }
output "server_status" { value = data.mycloud_server_info.web.status }
