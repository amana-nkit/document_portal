provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "docportal-rg-${random_string.suffix.result}"
  location = var.location
}

resource "random_string" "suffix" {
  length  = 4
  upper   = false
  special = false
}

# Create ACR (if you want)
resource "azurerm_container_registry" "acr" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
  sku                 = "Basic"
  admin_enabled       = true
}

# Deploy to Azure Container Instances (ACI)
resource "azurerm_container_group" "cg" {
  name                = "docportal-cg-${random_string.suffix.result}"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  os_type             = "Linux"

  container {
    name   = "document-portal"
    image  = var.image_uri
    cpu    = "0.5"
    memory = "1.5"

    ports {
      port     = 8080
      protocol = "TCP"
    }
  }

  ip_address {
    type = "Public"

    ports {
      port     = 8080
      protocol = "TCP"
    }
  }
}

output "container_group_name" {
  value = azurerm_container_group.cg.name
}
