.PHONY: help setup test clean monitor test-endpoint validate-terraform

help:
	@echo "MLOps Showcase Project"
	@echo "====================="
	@echo "Available commands:"
	@echo "  setup           - Initialize project and install dependencies"
	@echo "  test            - Run unit tests"
	@echo "  validate-terraform - Validate Terraform configuration"
	@echo "  test-endpoint   - Test the deployed endpoint (requires deployed infrastructure)"
	@echo "  monitor         - Run MLOps monitoring analysis (requires deployed infrastructure)"
	@echo "  clean           - Clean up resources (destroys Terraform infrastructure)"
	@echo ""
	@echo "Deployment is handled via GitHub Actions:"
	@echo "  - Push to main branch triggers complete MLOps pipeline"
	@echo "  - Pull requests trigger infrastructure planning only"
	@echo "  - Use workflow_dispatch for manual runs with optional settings"

setup:
	@echo "Setting up project..."
	./scripts/setup.sh

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src

validate-terraform:
	@echo "Validating Terraform configuration..."
	cd terraform && terraform init -backend=false
	cd terraform && terraform validate
	@echo "✅ Terraform configuration is valid"

test-endpoint:
	@echo "Testing SageMaker endpoint..."
	@if [ -z "$$SAGEMAKER_ENDPOINT_NAME" ]; then \
		echo "Getting endpoint name from Terraform outputs..."; \
		export SAGEMAKER_ENDPOINT_NAME=$$(cd terraform && terraform output -raw sagemaker_endpoint_name 2>/dev/null || echo "mlops-showcase-endpoint"); \
	fi; \
	python src/test_endpoint.py --with-monitoring

monitor:
	@echo "Running MLOps monitoring analysis..."
	@if [ -z "$$S3_BUCKET_NAME" ]; then \
		echo "Getting configuration from Terraform outputs..."; \
		export S3_BUCKET_NAME=$$(cd terraform && terraform output -raw s3_bucket_name 2>/dev/null || echo ""); \
		export SAGEMAKER_ENDPOINT_NAME=$$(cd terraform && terraform output -raw sagemaker_endpoint_name 2>/dev/null || echo ""); \
		export SNS_TOPIC_ARN=$$(cd terraform && terraform output -raw sns_topic_arn 2>/dev/null || echo ""); \
		if [ -z "$$S3_BUCKET_NAME" ]; then \
			echo "❌ No Terraform outputs found. Please deploy infrastructure first via GitHub Actions."; \
			exit 1; \
		fi; \
	fi; \
	python src/monitoring/mlops_monitor.py

clean:
	@echo "⚠️  This will destroy all AWS resources created by Terraform!"
	@echo "This action should typically be done via GitHub Actions for production environments."
	@read -p "Are you sure you want to continue? (y/N): " confirm; \
	if [ "$$confirm" = "y" ] || [ "$$confirm" = "Y" ]; then \
		cd terraform && terraform destroy -auto-approve; \
		echo "✅ Cleanup complete!"; \
	else \
		echo "Cleanup cancelled."; \
	fi