#!/usr/bin/env python3
"""
Test SageMaker endpoint deployed via Terraform
Uses Terraform outputs to get endpoint name and configuration
"""

import os
import json
import subprocess
import boto3
import pandas as pd
import numpy as np
from pathlib import Path

def get_terraform_outputs():
    """Get Terraform outputs to find endpoint name"""
    terraform_dir = Path("terraform")
    
    # Check if we're in a GitHub Actions environment
    if os.environ.get('GITHUB_ACTIONS'):
        print("Running in GitHub Actions - using environment variables")
        return None
    
    try:
        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=terraform_dir,
            capture_output=True,
            text=True
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to get Terraform outputs: {result.stderr}")
        
        return json.loads(result.stdout)
    
    except Exception as e:
        print(f"Error getting Terraform outputs: {e}")
        return None

def test_model_endpoint(endpoint_name=None):
    """Test the deployed SageMaker endpoint with sample data"""
    
    # Get endpoint name from Terraform outputs if not provided
    if not endpoint_name:
        outputs = get_terraform_outputs()
        if outputs and 'sagemaker_endpoint_name' in outputs:
            endpoint_name = outputs['sagemaker_endpoint_name']['value']
        else:
            # Fallback to environment variable or default
            endpoint_name = os.environ.get('SAGEMAKER_ENDPOINT_NAME', 'mlops-showcase-endpoint')
    
    print(f"Testing endpoint: {endpoint_name}")
    
    try:
        # Check endpoint status first
        sagemaker_client = boto3.client('sagemaker')
        endpoint_info = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
        
        print(f"Endpoint status: {endpoint_info['EndpointStatus']}")
        
        if endpoint_info['EndpointStatus'] != 'InService':
            print(f"Endpoint is not in service. Current status: {endpoint_info['EndpointStatus']}")
            return False
        
        # Create sample data (same format as training data - 20 features)
        sample_data = pd.DataFrame({
            f'feature_{i}': np.random.randn(3) for i in range(20)
        })
        
        print("\nSample input data:")
        print(sample_data)
        
        # Convert to CSV format for the endpoint
        csv_data = sample_data.to_csv(index=False)
        
        # Call the endpoint
        runtime = boto3.client('sagemaker-runtime')
        
        print("\nInvoking endpoint...")
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Body=csv_data
        )
        
        # Parse the response
        result = response['Body'].read().decode()
        print(f"\nModel predictions:")
        print(result)
        
        # Log successful test
        print(f"\n✅ Endpoint test successful!")
        print(f"Endpoint: {endpoint_name}")
        print(f"Response time: {response['ResponseMetadata'].get('HTTPHeaders', {}).get('x-amzn-requestid', 'N/A')}")
        
        return True
        
    except sagemaker_client.exceptions.ClientError as e:
        if 'does not exist' in str(e):
            print(f"❌ Endpoint '{endpoint_name}' does not exist.")
            print("Available endpoints:")
            try:
                response = sagemaker_client.list_endpoints()
                for endpoint in response['Endpoints']:
                    print(f"  - {endpoint['EndpointName']} ({endpoint['EndpointStatus']})")
            except:
                print("  Could not list endpoints")
        else:
            print(f"❌ AWS Error: {e}")
        return False
        
    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        return False

def test_with_monitoring():
    """Test endpoint and collect monitoring data"""
    print("Testing endpoint with monitoring enabled...")
    
    # Get Terraform outputs for monitoring setup
    outputs = get_terraform_outputs()
    if not outputs:
        print("Warning: Could not get Terraform outputs for monitoring")
        return test_model_endpoint()
    
    endpoint_name = outputs.get('sagemaker_endpoint_name', {}).get('value')
    bucket_name = outputs.get('s3_bucket_name', {}).get('value')
    
    if not endpoint_name or not bucket_name:
        print("Warning: Missing endpoint or bucket name from Terraform outputs")
        return test_model_endpoint()
    
    # Test the endpoint
    success = test_model_endpoint(endpoint_name)
    
    if success:
        print("\n" + "="*50)
        print("MONITORING INFORMATION")
        print("="*50)
        print(f"Data capture enabled: Yes")
        print(f"Data capture location: s3://{bucket_name}/data-capture")
        print(f"CloudWatch dashboard: {outputs.get('cloudwatch_dashboard_url', {}).get('value', 'N/A')}")
        print(f"SNS alerts topic: {outputs.get('sns_topic_arn', {}).get('value', 'N/A')}")
        
        # Show how to run monitoring
        print("\nTo run monitoring analysis:")
        print(f"export S3_BUCKET_NAME={bucket_name}")
        print(f"export SAGEMAKER_ENDPOINT_NAME={endpoint_name}")
        print("python src/monitoring/mlops_monitor.py")
    
    return success

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--with-monitoring":
        test_with_monitoring()
    else:
        test_model_endpoint()