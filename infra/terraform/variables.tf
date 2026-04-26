variable "aws_region" {
  description = "The AWS region to deploy resources into"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "The base name for all resources"
  type        = string
  default     = "knowledge-hub"
}

variable "vpc_cidr" {
  description = "The CIDR block for the VPC"
  type        = string
  default     = "10.0.0.0/16"
}

variable "db_password" {
  description = "The password for the RDS PostgreSQL database"
  type        = string
  sensitive   = true
}
