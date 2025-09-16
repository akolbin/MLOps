# CloudWatch Log Group for SageMaker
resource "aws_cloudwatch_log_group" "sagemaker_logs" {
  name              = "/aws/sagemaker/${var.project_name}"
  retention_in_days = 7
  
  tags = var.tags
}

# SageMaker Model Package Group for model registry
resource "aws_sagemaker_model_package_group" "mlops_model_group" {
  model_package_group_name        = "${var.project_name}-model-group"
  model_package_group_description = "Model package group for ${var.project_name}"

  tags = var.tags
}

# Note: SageMaker Model and Endpoint are created by the deployment script
# after the model is trained and uploaded to S3