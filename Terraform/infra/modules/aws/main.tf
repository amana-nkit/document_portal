# Create ECR repo (optional; if image is already pushed to ECR, this is idempotent)
resource "aws_ecr_repository" "repo" {
  name = split("/", var.image_uri)[0] == "" ? "documentregistry" : replace(split("/", var.image_uri)[0], "${data.aws_caller_identity.current.account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/", "")
  lifecycle {
    prevent_destroy = false
  }
}

data "aws_caller_identity" "current" {}

resource "aws_ecs_cluster" "this" {
  name = var.ecs_cluster_name
}

# Minimal task execution role (adjust trust / policies in production)
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.ecs_cluster_name}-exec-role"
  assume_role_policy = data.aws_iam_policy_document.ecs_task_assume.json
}

data "aws_iam_policy_document" "ecs_task_assume" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"]
    }
  }
}

resource "aws_iam_role_policy_attachment" "exec_attach" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}

resource "aws_ecs_task_definition" "task" {
  family                   = "${var.ecs_cluster_name}-task"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn

  container_definitions = jsonencode([
    {
      name      = "document-portal"
      image     = var.image_uri
      essential = true
      portMappings = [
        {
          containerPort = 8080
          protocol      = "tcp"
        }
      ]
    }
  ])
}

resource "aws_ecs_service" "service" {
  name            = var.ecs_service_name
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  network_configuration {
    assign_public_ip = true
    # You should replace these with real subnet ids and security group ids
    subnets         = [var.default_subnet_id]
    security_groups = [var.default_security_group_id]
  }
}

# Simple placeholder inputs for subnets & sg — expect these to be provided via vars or data sources in prod
variable "default_subnet_id" { type = string, default = "" }
variable "default_security_group_id" { type = string, default = "" }

output "cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "service_name" {
  value = aws_ecs_service.service.name
}
