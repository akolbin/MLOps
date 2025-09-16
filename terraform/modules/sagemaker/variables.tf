variable "project_name" {
  description = "Name of the MLOps project"
  type        = string
}



variable "suffix" {
  description = "Random suffix for unique naming"
  type        = string
}

variable "execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  type        = string
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket for model artifacts"
  type        = string
}

# SageMaker deployment variables removed - handled by deployment script

variable "tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
  default     = {}
}