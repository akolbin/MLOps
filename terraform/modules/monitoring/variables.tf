variable "project_name" {
  description = "Name of the MLOps project"
  type        = string
}



variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "endpoint_name" {
  description = "Name of the SageMaker endpoint to monitor"
  type        = string
}

variable "latency_threshold_ms" {
  description = "Latency threshold in milliseconds for CloudWatch alarm"
  type        = number
}

variable "error_rate_threshold" {
  description = "Error rate threshold for CloudWatch alarm"
  type        = number
}

variable "alert_email" {
  description = "Email address for MLOps alerts"
  type        = string
}

variable "drift_check_schedule" {
  description = "Schedule expression for model drift checks"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
  default     = {}
}