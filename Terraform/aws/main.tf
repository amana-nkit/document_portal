provider "aws" {
  region = var.aws_region
}

resource "aws_ecr_repository" "this" {
  name = var.ecr_repository
}

resource "aws_ecs_cluster" "this" {
  name = var.ecs_cluster
}

resource "aws_ecs_task_definition" "this" {
  family                   = "document-portal-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = var.execution_role_arn

  container_definitions = jsonencode([
    {
      name      = "document-portal-container"
      image     = var.image_uri
      essential = true
      portMappings = [
        {
          containerPort = 8080
          hostPort      = 8080
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "this" {
  name            = var.ecs_service
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.this.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    subnets         = var.subnets
    security_groups = [var.security_group]
    assign_public_ip = true
  }
}
