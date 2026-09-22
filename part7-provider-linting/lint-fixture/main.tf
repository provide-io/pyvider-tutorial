terraform {
  required_version = "= 1.13.0-rc1"

  required_providers {
    mycloud = {
      source  = "example/mycloud"
      version = "0.1.0"
    }
  }
}

provider "mycloud" {}

resource "mycloud_server" "web" {
  name = "web-prod"
}
