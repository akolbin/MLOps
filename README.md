# MLOps Showcase Project

A cost-effective MLOps pipeline demonstrating end-to-end machine learning lifecycle management on AWS.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Source   │───▶│  SageMaker       │───▶│   SageMaker     │
│   (S3 Bucket)   │    │  Training Job    │    │   Serverless    │
└─────────────────┘    └──────────────────┘    │   Inference     │
                                               └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Model Registry │    │   CloudWatch    │
                       │   (S3 + Metadata)│    │   Monitoring    │
                       └──────────────────┘    └─────────────────┘
```

## Quick Start

1. **Setup Infrastructure**
   ```bash
   cd terraform
   terraform init
   terraform plan
   terraform apply
   ```

2. **Train Model**
   ```bash
   python src/train.py
   ```

3. **Deploy Model**
   ```bash
   python src/deploy.py
   ```

4. **Test Inference**
   ```bash
   python src/test_inference.py
   ```

## Project Structure

```
├── .github/workflows/     # CI/CD pipelines
├── terraform/            # Infrastructure as Code
├── src/                 # Source code
│   ├── data/           # Data processing
│   ├── models/         # Model training
│   └── inference/      # Deployment code
├── tests/              # Unit tests
└── notebooks/          # Exploration notebooks
```

## Features Demonstrated

- ✅ Infrastructure as Code (Terraform)
- ✅ Model Training Pipeline
- ✅ Model Registry & Versioning
- ✅ Serverless Deployment
- ✅ Monitoring & Logging
- ✅ CI/CD with GitHub Actions
- ✅ Cost Optimization