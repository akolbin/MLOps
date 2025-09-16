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

# SageMaker Model
resource "aws_sagemaker_model" "mlops_model" {
  name               = "${var.project_name}-model-${var.suffix}"
  execution_role_arn = var.execution_role_arn

  primary_container {
    image          = var.sklearn_image_uri
    model_data_url = "s3://${var.s3_bucket_name}/models/model.tar.gz"
    environment = {
      SAGEMAKER_PROGRAM         = "inference.py"
      SAGEMAKER_SUBMIT_DIRECTORY = "/opt/ml/code"
    }
  }

  tags = var.tags
}

# SageMaker Endpoint Configuration
resource "aws_sagemaker_endpoint_configuration" "mlops_endpoint_config" {
  name = "${var.project_name}-endpoint-config-${var.suffix}"

  production_variants {
    variant_name           = "primary"
    model_name            = aws_sagemaker_model.mlops_model.name
    initial_instance_count = 0
    
    serverless_config {
      memory_size_in_mb = var.serverless_memory_size
      max_concurrency   = var.serverless_max_concurrency
    }
  }

  data_capture_config {
    enable_capture              = true
    initial_sampling_percentage = var.data_capture_sampling_percentage
    destination_s3_uri          = "s3://${var.s3_bucket_name}/data-capture"
    
    capture_options {
      capture_mode = "Input"
    }
    
    capture_options {
      capture_mode = "Output"
    }
    
    capture_content_type_header {
      csv_content_types  = ["text/csv"]
      json_content_types = ["application/json"]
    }
  }

  tags = var.tags
}

# SageMaker Endpoint
resource "aws_sagemaker_endpoint" "mlops_endpoint" {
  name                 = "${var.project_name}-endpoint"
  endpoint_config_name = aws_sagemaker_endpoint_configuration.mlops_endpoint_config.name

  tags = var.tags
}