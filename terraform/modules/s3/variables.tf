variable "project_name" {
  description = "Name of the MLOps project"
  type        = string
}

variable "suffix" {
  description = "Random suffix for unique naming"
  type        = string
}

variable "tags" {
  description = "Common tags to apply to resources"
  type        = map(string)
  default     = {}
}