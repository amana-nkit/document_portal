# AWS provider (used when workspace == "aws")
provider "aws" {
  region = var.aws_region
  # credentials via env, profile, or role assumed by CI runner
  # e.g. export AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
  skip_credentials_validation = false
  allowed_account_ids = var.aws_account_ids
  alias = "aws"
}

# Azure provider (used when workspace == "azure")
provider "azurerm" {
  features {}
  subscription_id = var.azure_subscription_id
  tenant_id       = var.azure_tenant_id
  client_id       = var.azure_client_id
  client_secret   = var.azure_client_secret
  alias = "azure"
}
