terraform {
  required_providers {
    mycloud = {
      source  = "local/providers/mycloud"
      version = "0.1.0"
    }
  }
}

provider "mycloud" {}

resource "mycloud_server" "web" {
  name = "web-01"
}

output "server_id"     { value = mycloud_server.web.id }
output "server_status" { value = mycloud_server.web.status }
