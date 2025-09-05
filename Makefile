.PHONY: help setup test deploy clean

help:
	@echo "MLOps Showcase Project"
	@echo "====================="
	@echo "Available commands:"
	@echo "  setup     - Initialize project and install dependencies"
	@echo "  test      - Run unit tests"
	@echo "  deploy    - Deploy infrastructure and model"
	@echo "  clean     - Clean up resources"
	@echo "  data      - Generate and upload synthetic data"
	@echo "  train     - Train the model"
	@echo "  inference - Deploy model for inference"

setup:
	@echo "Setting up project..."
	./scripts/setup.sh

test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src

deploy:
	@echo "Deploying infrastructure..."
	cd terraform && terraform apply -auto-approve
	@echo "Setting environment variables..."
	$(eval S3_BUCKET := $(shell cd terraform && terraform output -raw s3_bucket_name))
	$(eval ROLE_ARN := $(shell cd terraform && terraform output -raw sagemaker_execution_role_arn))
	@echo "Generating data..."
	S3_BUCKET_NAME=$(S3_BUCKET) python src/data/generate_data.py
	@echo "Training model..."
	S3_BUCKET_NAME=$(S3_BUCKET) SAGEMAKER_ROLE_ARN=$(ROLE_ARN) python src/models/train.py

data:
	@echo "Generating synthetic data..."
	python src/data/generate_data.py

train:
	@echo "Training model..."
	python src/models/train.py

inference:
	@echo "Deploying model for inference..."
	python src/inference/deploy.py

clean:
	@echo "Cleaning up resources..."
	cd terraform && terraform destroy -auto-approve
	@echo "Cleanup complete!"