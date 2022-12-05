locals {
  config_file = file("deploy.auto.tfvars")
}

resource "kubernetes_config_map_v1" "index_display" {
  metadata {
    name      = "index-display"
    namespace = var.kube_namespace
  }

  data = {
    display_value = var.display_value
  }
}

resource "kubernetes_config_map_v1" "config_page" {
  metadata {
    name      = "config-page"
    namespace = var.kube_namespace
  }

  data = {
    config_values = file("deploy.auto.tfvars")
  }
}
