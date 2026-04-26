# Place the database exclusively in our isolated Private Subnets
resource "aws_db_subnet_group" "rds_subnet_group" {
  name       = "${var.project_name}-rds-subnet-group"
  subnet_ids = [aws_subnet.private_a.id, aws_subnet.private_b.id]

  tags = {
    Name = "Enterprise RAG DB Subnet Group"
  }
}

resource "aws_db_instance" "postgres" {
  identifier        = "${var.project_name}-db"
  engine            = "postgres"
  engine_version    = "16.3"
  instance_class    = "db.t4g.micro"
  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "knowledge_hub"
  username = "admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.rds_subnet_group.name
  vpc_security_group_ids = [aws_security_group.rds_sg.id]

  # Security constraint: No public IP
  publicly_accessible = false

  # FinOps Data Persistence Strategy: Create a snapshot when we run terraform destroy
  skip_final_snapshot       = false
  final_snapshot_identifier = "${var.project_name}-db-final-snapshot"

  # Note: When spinning the infra back up for an interview, uncomment this line:
  # snapshot_identifier     = "${var.project_name}-db-final-snapshot"

  tags = {
    Name = "Multi-Tenant Vector DB"
  }
}
