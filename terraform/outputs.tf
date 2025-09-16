output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = module.s3.bucket_name
}

output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  value       = module.iam.sagemaker_execution_role_arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = module.sagemaker.log_group_name
}

# SageMaker endpoint and model outputs removed - created by deployment script

output "model_package_group_name" {
  description = "Name of the SageMaker model package group"
  value       = module.sagemaker.model_package_group_name
}

# Monitoring outputs removed - created by deployment script

output "data_capture_s3_path" {
  description = "S3 path where model data capture is stored"
  value       = "s3://${module.s3.bucket_name}/data-capture"
}