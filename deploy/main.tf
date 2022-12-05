resource "kubernetes_namespace_v1" "turo" {
  metadata {
    name = var.kube_namespace
  }
}

locals {
  deploy_yaml      = replace(file(var.deployment_yaml), "kube_namespace", var.kube_namespace)
  ssl_service_yaml = replace(file(var.ssl_service_yaml), "kube_namespace", var.kube_namespace)
}

resource "kubernetes_manifest" "turo-test-deployment" {
  manifest = yamldecode(replace(local.deploy_yaml, "docker_image_replace", var.image_name))

  wait {
    rollout = true
  }

  field_manager {
    # set the name of the field manager
    name = "edamsoft"
    # force field manager conflicts to be overridden
    force_conflicts = false
  }
}

resource "kubernetes_manifest" "ssl_service" {
  manifest = yamldecode(replace(local.ssl_service_yaml, "acm_arn", var.acm_arn))
  field_manager {
    # set the name of the field manager
    name = "edamsoft"
    # force field manager conflicts to be overridden
    force_conflicts = false
  }

}
