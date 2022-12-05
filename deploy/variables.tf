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

variable "kube_namespace" {
  type        = string
  description = "Kube namespace to create and deploy app to"
}

variable "ssl_service_yaml" {
  type = string
  description = "Kubernetes SSL Service Manifest"
}

variable "acm_arn" {
  type = string
  description = "AWS ACM arn value for SSL service"
}