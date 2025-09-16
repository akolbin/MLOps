variable "project_name" {
  description = "Name of the MLOps project"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket for SageMaker access"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
  default     = {}
}