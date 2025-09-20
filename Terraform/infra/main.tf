locals {
  # determine cloud from workspace unless variable override provided
  workspace = terraform.workspace
  cloud = length(var.cloud) > 0 ? var.cloud : terraform.workspace
}

# AWS module invoked only when workspace==aws (count trick)
module "aws" {
  source = "./modules/aws"
  count  = local.cloud == "aws" ? 1 : 0

  image_uri        = var.image_uri
  aws_region       = var.aws_region
  ecs_cluster_name = var.ecs_cluster_name
  ecs_service_name = var.ecs_service_name
}

# Azure module invoked only when workspace==azure
module "azure" {
  source = "./modules/azure"
  count  = local.cloud == "azure" ? 1 : 0

  image_uri            = var.image_uri
  location             = var.azure_location
  acr_name             = var.acr_name
  subscription_id      = var.azure_subscription_id
  client_id            = var.azure_client_id
  client_secret        = var.azure_client_secret
  tenant_id            = var.azure_tenant_id
}
