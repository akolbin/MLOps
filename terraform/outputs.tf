output "s3_bucket_name" {
  description = "Name of the S3 bucket"
  value       = aws_s3_bucket.mlops_bucket.bucket
}

output "sagemaker_execution_role_arn" {
  description = "ARN of the SageMaker execution role"
  value       = aws_iam_role.sagemaker_execution_role.arn
}

output "cloudwatch_log_group_name" {
  description = "Name of the CloudWatch log group"
  value       = aws_cloudwatch_log_group.mlops_logs.name
}