variable "cloud" {
  description = "Cloud target; auto derived from workspace, optional override."
  type        = string
  default     = ""
}

variable "image_uri" {
  description = "Docker image URI (ECR or ACR) including tag, e.g. <registry>/<repo>:<tag>"
  type        = string
}

# AWS-specific
variable "aws_region" {
  type    = string
  default = "us-east-1"
}
variable "aws_account_ids" {
  type    = list(string)
  default = []
}
variable "ecs_cluster_name" {
  type    = string
  default = "document-portal-cluster"
}
variable "ecs_service_name" {
  type    = string
  default = "document-portal-service"
}

# Azure-specific
variable "azure_subscription_id" { type = string, default = "" }
variable "azure_tenant_id"       { type = string, default = "" }
variable "azure_client_id"       { type = string, default = "" }
variable "azure_client_secret"   { type = string, default = "" }
variable "azure_location"        { type = string, default = "eastus" }
variable "acr_name"              { type = string, default = "docportalacr" }
