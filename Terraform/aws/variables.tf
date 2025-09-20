variable "aws_region" {}
variable "ecr_repository" {}
variable "ecs_cluster" {}
variable "ecs_service" {}
variable "execution_role_arn" {}
variable "subnets" { type = list(string) }
variable "security_group" {}
variable "image_uri" {}
