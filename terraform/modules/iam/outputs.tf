output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  value       = aws_iam_role.sagemaker_execution_role.arn
}

output "lambda_monitoring_role_arn" {
  description = "ARN of the Lambda monitoring role"
  value       = aws_iam_role.lambda_monitoring_role.arn
}