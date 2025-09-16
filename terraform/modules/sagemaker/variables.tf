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

variable "sklearn_image_uri" {
  description = "SageMaker SKLearn container image URI"
  type        = string
}

variable "serverless_memory_size" {
  description = "Memory size for serverless endpoint in MB"
  type        = number
}

variable "serverless_max_concurrency" {
  description = "Maximum concurrency for serverless endpoint"
  type        = number
}

variable "data_capture_sampling_percentage" {
  description = "Percentage of requests to capture for monitoring"
  type        = number
}

variable "tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
  default     = {}
}