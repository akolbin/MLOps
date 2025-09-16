variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Name of the MLOps project"
  type        = string
  default     = "mlops-showcase"
}

variable "environment" {
  description = "Environment"
  type        = string
  default     = "personal"
}

variable "sklearn_image_uri" {
  description = "SageMaker SKLearn container image URI"
  type        = string
  default     = "246618743249.dkr.ecr.us-east-1.amazonaws.com/sagemaker-scikit-learn:1.2-1-cpu-py3"
}

variable "serverless_memory_size" {
  description = "Memory size for serverless endpoint in MB"
  type        = number
  default     = 2048
}

variable "serverless_max_concurrency" {
  description = "Maximum concurrency for serverless endpoint"
  type        = number
  default     = 1
}

variable "data_capture_sampling_percentage" {
  description = "Percentage of requests to capture for monitoring"
  type        = number
  default     = 100
}

variable "latency_threshold_ms" {
  description = "Latency threshold in milliseconds for CloudWatch alarm"
  type        = number
  default     = 5000
}

variable "error_rate_threshold" {
  description = "Error rate threshold for CloudWatch alarm"
  type        = number
  default     = 5
}

variable "alert_email" {
  description = "Email address for MLOps alerts"
  type        = string
  default     = ""
}

variable "drift_check_schedule" {
  description = "Schedule expression for model drift checks"
  type        = string
  default     = "rate(1 day)"
}