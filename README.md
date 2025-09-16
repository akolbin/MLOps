# MLOps Showcase Project

A comprehensive MLOps pipeline demonstrating end-to-end machine learning lifecycle management on AWS with Infrastructure as Code and advanced monitoring.

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Data Source   │───▶│  SageMaker       │───▶│   SageMaker     │
│   (S3 Bucket)   │    │  Training Job    │    │   Serverless    │
└─────────────────┘    └──────────────────┘    │   Endpoint      │
                                               └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌──────────────────┐    ┌─────────────────┐
                       │   Model Package  │    │   Data Capture  │
                       │   Group Registry │    │   & Monitoring  │
                       └──────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   SNS Alerts   │◀───│   CloudWatch     │◀───│   Drift         │
│   & Dashboard  │    │   Alarms         │    │   Detection     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## Quick Start

### GitHub Actions Deployment (Recommended)

1. **Setup AWS OIDC Authentication**
   Ensure your AWS account has:
   - GitHub OIDC provider configured
   - IAM role `GitHub_Actions_Runner` with appropriate permissions
   - Trust policy allowing your GitHub repository

2. **Deploy Complete MLOps Pipeline**
   - Push changes to `main` branch (full pipeline), or
   - Create Pull Request (infrastructure planning only), or
   - Use GitHub Actions "MLOps Pipeline" workflow manually
   - Optionally provide alert email and skip infrastructure if needed

3. **Local Testing** (after deployment)
   ```bash
   make test-endpoint  # Test the deployed endpoint
   make monitor        # Run monitoring analysis
   ```

### Local Development

1. **Validate Terraform**
   ```bash
   make validate-terraform
   ```

2. **Run Tests**
   ```bash
   make test
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

### Core MLOps Features
- ✅ **Infrastructure as Code** - Complete Terraform configuration
- ✅ **Model Training Pipeline** - Automated training with SageMaker
- ✅ **Model Registry & Versioning** - SageMaker Model Package Groups
- ✅ **Serverless Deployment** - Cost-effective SageMaker Serverless Inference
- ✅ **CI/CD Integration** - GitHub Actions workflows

### Advanced Monitoring & Observability
- ✅ **Real-time Monitoring** - CloudWatch metrics and alarms
- ✅ **Data Capture** - Automatic input/output logging for analysis
- ✅ **Drift Detection** - Basic statistical drift monitoring
- ✅ **Alert System** - SNS notifications for model issues
- ✅ **Performance Dashboard** - CloudWatch dashboard for visualization
- ✅ **Health Reporting** - Automated health checks and reports

### Cost Optimization
- ✅ **Serverless Inference** - Pay-per-request pricing
- ✅ **Resource Tagging** - Cost tracking and management
- ✅ **Automated Cleanup** - Easy resource destruction

## MLOps Monitoring

The project includes comprehensive monitoring capabilities:

### Metrics Tracked
- **Invocation Count** - Number of inference requests
- **Model Latency** - Response time per request
- **Error Rates** - 4XX and 5XX error tracking
- **Resource Utilization** - CPU and memory usage

### Alerting
- **Latency Alerts** - Triggered when response time > 5 seconds
- **Error Rate Alerts** - Triggered when error rate > 5%
- **Email Notifications** - Configurable via SNS

### Data Capture & Drift Detection
- **Input/Output Logging** - All requests captured to S3
- **Statistical Analysis** - Basic drift detection on input features
- **Historical Reporting** - Trend analysis over time

## Configuration

### GitHub Actions Setup
This project uses OpenID Connect (OIDC) for secure AWS authentication without storing long-lived credentials.

**Prerequisites:**
1. **AWS IAM Role**: The workflows assume an IAM role `arn:aws:iam::836072596305:role/GitHub_Actions_Runner` exists
2. **OIDC Provider**: GitHub OIDC provider must be configured in your AWS account
3. **Trust Policy**: The IAM role must trust your GitHub repository

**Optional workflow inputs:**
- `ALERT_EMAIL` - Email for alerts (can be provided during manual workflow dispatch)

**No secrets required** - Authentication uses OIDC role assumption

### Terraform Variables
Key variables in `terraform/variables.tf`:
- `serverless_memory_size` - Memory allocation for endpoint (default: 2048MB)
- `serverless_max_concurrency` - Max concurrent requests (default: 1)
- `data_capture_sampling_percentage` - % of requests to capture (default: 100%)
- `latency_threshold_ms` - Latency alarm threshold (default: 5000ms)

## Project Structure

```
├── .github/workflows/          # GitHub Actions CI/CD
│   ├── deploy-infrastructure.yml
│   └── deploy-model.yml
├── terraform/                  # Infrastructure as Code
│   ├── modules/               # Terraform modules
│   │   ├── s3/               # S3 bucket configuration
│   │   ├── iam/              # IAM roles and policies
│   │   ├── sagemaker/        # SageMaker resources
│   │   └── monitoring/       # CloudWatch and SNS
│   ├── main.tf               # Main Terraform configuration
│   ├── variables.tf          # Input variables
│   └── outputs.tf            # Output values
├── src/                      # Source code
│   ├── data/                # Data processing
│   ├── models/              # Model training
│   ├── inference/           # Model inference
│   ├── monitoring/          # MLOps monitoring
│   └── test_endpoint.py     # Endpoint testing
└── tests/                   # Unit tests
```

## Monitoring Commands

```bash
# Run comprehensive health check (requires deployed infrastructure)
make monitor

# Test endpoint with monitoring data
make test-endpoint

# Validate Terraform configuration
make validate-terraform

# View CloudWatch dashboard
# URL provided in GitHub Actions deployment summary

# Check data capture files
aws s3 ls s3://your-bucket-name/data-capture/ --recursive
```

## GitHub Actions Pipeline

### Single MLOps Pipeline
- **Trigger**: Push to main, PR, or manual dispatch
- **Stages**: 
  1. **Infrastructure** - Deploy/update AWS resources with Terraform
  2. **Model Training** - Generate data and train model
  3. **Endpoint Testing** - Wait for endpoint and test inference
  4. **Monitoring** - Run health checks and performance analysis
  5. **Summary** - Comprehensive pipeline results
- **Outputs**: Complete deployment summary with all resource details

## Personal Project Setup

Since this is configured as a personal project, it uses simplified settings:
- Single environment (no dev/staging/prod complexity)
- Streamlined variable configuration
- Direct deployment to main AWS account
- Optional email alerts via workflow dispatch
- OIDC authentication (no long-lived AWS credentials)

## AWS OIDC Setup

This project uses OpenID Connect for secure authentication. You'll need to set up:

### 1. GitHub OIDC Provider in AWS
```bash
# Create OIDC provider (one-time setup)
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

### 2. IAM Role with Trust Policy
Create role `GitHub_Actions_Runner` with this trust policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::836072596305:oidc-provider/token.actions.githubusercontent.com"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
          "token.actions.githubusercontent.com:sub": "repo:YOUR_GITHUB_USERNAME/YOUR_REPO_NAME:ref:refs/heads/main"
        }
      }
    }
  ]
}
```

### 3. Required Permissions
Attach these policies to the role:
- `AmazonS3FullAccess`
- `AmazonSageMakerFullAccess`
- `CloudWatchFullAccess`
- `AmazonSNSFullAccess`
- `IAMReadOnlyAccess`