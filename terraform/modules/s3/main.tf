# S3 bucket for MLOps data and models
resource "aws_s3_bucket" "mlops_bucket" {
  bucket = "${var.project_name}-${var.suffix}"
  
  tags = var.tags
}

resource "aws_s3_bucket_versioning" "mlops_bucket_versioning" {
  bucket = aws_s3_bucket.mlops_bucket.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "mlops_bucket_encryption" {
  bucket = aws_s3_bucket.mlops_bucket.id
  
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "mlops_bucket_pab" {
  bucket = aws_s3_bucket.mlops_bucket.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Create folder structure
resource "aws_s3_object" "data_folder" {
  bucket = aws_s3_bucket.mlops_bucket.id
  key    = "data/"
  content = ""
}

resource "aws_s3_object" "models_folder" {
  bucket = aws_s3_bucket.mlops_bucket.id
  key    = "models/"
  content = ""
}

resource "aws_s3_object" "data_capture_folder" {
  bucket = aws_s3_bucket.mlops_bucket.id
  key    = "data-capture/"
  content = ""
}

resource "aws_s3_object" "monitoring_reports_folder" {
  bucket = aws_s3_bucket.mlops_bucket.id
  key    = "monitoring-reports/"
  content = ""
}