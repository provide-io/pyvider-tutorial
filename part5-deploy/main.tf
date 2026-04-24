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

resource "mycloud_server" "web" {
  name = local.server_name
}

ephemeral "mycloud_session_token" "web_access" {
  server_id   = mycloud_server.web.id
  ttl_seconds = 900
}

data "mycloud_server_info" "web" {
  server_id = mycloud_server.web.id
}

output "server_name"   { value = local.server_name }
output "server_id"     { value = mycloud_server.web.id }
output "server_status" { value = data.mycloud_server_info.web.status }

# Ephemeral values cannot be exposed through root-module outputs — that's
# the point of marking them ephemeral. The session token is used inside
# the apply phase and discarded after the run. Try `tofu apply -json` to
# see the open/renew/close events emitted by the provider.
