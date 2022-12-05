resource "kubernetes_namespace_v1" "turo" {
  metadata {
    name = var.kube_namespace
  }
}

locals {
  deploy_yaml = yamldecode(replace(file(var.deployment_yaml), "docker_image_replace", var.image_name))
}

resource "kubernetes_manifest" "turo-test-deployment" {

  manifest = local.deploy_yaml

  field_manager {
    # set the name of the field manager
    name = "edamsoft"
    # force field manager conflicts to be overridden
    force_conflicts = false
  }
}
