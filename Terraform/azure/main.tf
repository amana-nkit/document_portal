provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "this" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_container_registry" "this" {
  name                = var.acr_name
  resource_group_name = azurerm_resource_group.this.name
  location            = azurerm_resource_group.this.location
  sku                 = "Basic"
  admin_enabled       = true
}

resource "azurerm_container_group" "this" {
  name                = "document-portal-cg"
  location            = azurerm_resource_group.this.location
  resource_group_name = azurerm_resource_group.this.name
  os_type             = "Linux"

  container {
    name   = "document-portal-container"
    image  = "${azurerm_container_registry.this.login_server}/${var.image_name}:${var.image_tag}"
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
