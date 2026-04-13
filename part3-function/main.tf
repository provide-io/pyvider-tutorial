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

data "mycloud_server_info" "web" {
  server_id = mycloud_server.web.id
}

output "server_name"   { value = local.server_name }
output "server_id"     { value = mycloud_server.web.id }
output "server_status" { value = data.mycloud_server_info.web.status }
