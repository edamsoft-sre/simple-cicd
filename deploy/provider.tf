terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = ">=2.16.0"
    }
  }
}

provider "kubernetes" {
  # Requires KUBE_CONFIG_PATH be set
  config_context = var.kube_config_context
}
