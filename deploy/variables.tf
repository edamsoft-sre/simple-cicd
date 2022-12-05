variable "kube_config_context" {
  type        = string
  description = "Name of Kube config context to deploy with from config at KUBE_CONFIG_PATH"
}

variable "deployment_yaml" {
  type        = string
  description = "Kubernetes Deploy Manifest"
}

variable "image_name" {
  type        = string
  description = "The image to be deployed"
}

variable "missing_var" {
  type        = string
  description = "Used just for testing tfvars auto-updates"
}
