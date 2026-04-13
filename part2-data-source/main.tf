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

data "mycloud_server_info" "web" {
  server_id = mycloud_server.web.id
}

output "server_id"     { value = mycloud_server.web.id }
output "server_name"   { value = data.mycloud_server_info.web.name }
output "server_status" { value = data.mycloud_server_info.web.status }
