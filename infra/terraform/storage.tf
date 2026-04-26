# Fetch the current AWS account ID dynamically to ensure globally unique bucket names
data "aws_caller_identity" "current" {}

# The Multi-Tenant Document Bucket
resource "aws_s3_bucket" "document" {
  bucket = "${var.project_name}-docs-${data.aws_caller_identity.current.account_id}"

  # FinOps/Portfolio Strategy: Allows terraform destroy to work even if the bucket has files
  force_destroy = true

  tags = {
    Name = "Enterprise Knowledge Hub Documents"
  }
}

# Security Boundary: Block all public access
resource "aws_s3_bucket_public_access_block" "documents_public_access" {
  bucket                  = aws_s3_bucket.document.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Security Boundary: Enforce Encryption at Rest
resource "aws_s3_bucket_server_side_encryption_configuration" "documents_encryption" {
  bucket = aws_s3_bucket.document.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}
