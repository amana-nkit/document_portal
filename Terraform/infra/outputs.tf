output "active_workspace" {
  value = terraform.workspace
}

output "aws_service" {
  value       = try(module.aws[0].service_name, "")
  description = "AWS ECS service name (if deployed)"
  depends_on  = []
}

output "azure_container_group" {
  value       = try(module.azure[0].container_group_name, "")
  description = "Azure Container Group name (if deployed)"
}
