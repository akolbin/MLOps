#!/bin/bash

# MLOps Project Setup Script

set -e

echo "🚀 Setting up MLOps Showcase Project..."

# Check if required tools are installed
check_tool() {
    if ! command -v $1 &> /dev/null; then
        echo "❌ $1 is not installed. Please install it first."
        exit 1
    fi
}

echo "📋 Checking prerequisites..."
check_tool "terraform"
check_tool "aws"
check_tool "python3"

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Initialize Terraform
echo "🏗️  Initializing Terraform..."
cd terraform
terraform init

# Plan infrastructure
echo "📋 Planning infrastructure..."
terraform plan

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Configure AWS credentials: aws configure"
echo "2. Deploy infrastructure: cd terraform && terraform apply"
echo "3. Set environment variables:"
echo "   export S3_BUCKET_NAME=\$(cd terraform && terraform output -raw s3_bucket_name)"
echo "   export SAGEMAKER_ROLE_ARN=\$(cd terraform && terraform output -raw sagemaker_execution_role_arn)"
echo "4. Generate data: python src/data/generate_data.py"
echo "5. Train model: python src/models/train.py"
echo "6. Deploy model: python src/inference/deploy.py"