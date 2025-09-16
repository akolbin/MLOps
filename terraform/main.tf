terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.1"
    }
  }

  backend "s3" {
    bucket = "akolbin-mlops-tfstate"
    key    = "terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# Random suffix for unique resource names
resource "random_string" "suffix" {
  length  = 8
  special = false
  upper   = false
}

# Local values for common tags
locals {
  common_tags = {
    Project   = var.project_name
    ManagedBy = "terraform"
  }
}

# S3 Module
module "s3" {
  source = "./modules/s3"

  project_name = var.project_name
  suffix       = random_string.suffix.result
  tags         = local.common_tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  project_name  = var.project_name
  s3_bucket_arn = module.s3.bucket_arn
  tags          = local.common_tags
}

# SageMaker Module
module "sagemaker" {
  source = "./modules/sagemaker"

  project_name       = var.project_name
  suffix            = random_string.suffix.result
  execution_role_arn = module.iam.sagemaker_execution_role_arn
  s3_bucket_name    = module.s3.bucket_name
  tags              = local.common_tags
}

# Monitoring resources will be created by the deployment script
# after the endpoint is deployed
