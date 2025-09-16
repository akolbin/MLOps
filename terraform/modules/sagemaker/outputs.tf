# Endpoint and model outputs removed - these are created by deployment script

output "model_package_group_name" {
  description = "Name of the SageMaker model package group"
  value       = aws_sagemaker_model_package_group.mlops_model_group.model_package_group_name
}

output "log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.sagemaker_logs.name
}