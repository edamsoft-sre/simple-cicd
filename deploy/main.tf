resource "kubernetes_namespace_v1" "turo" {
  metadata {
    name = "turo"
  }
}

resource "kubernetes_manifest" "turo-test-deployment" {

  manifest = yamldecode(file(var.deployment_yaml))

  field_manager {
    # set the name of the field manager
    name = "edamsoft"
    # force field manager conflicts to be overridden
    force_conflicts = false
  }
}