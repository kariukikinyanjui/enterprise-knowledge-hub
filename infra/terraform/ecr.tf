# Amazon ECR Repository for the Django Application
resource "aws_ecr_repository" "backend" {
  name                 = "${var.project_name}-backend"
  image_tag_mutability = "MUTABLE"

  # DevSecOps: Automatically scan the Docker image for CVEs upon push
  image_scanning_configuration {
    scan_on_push = true
  }

  # FinOps/Portfolio Strategy: Allows terraform destroy to delete the repo even if images exist
  force_delete = true

  tags = {
    Name = "Backend Container Registry"
  }
}
