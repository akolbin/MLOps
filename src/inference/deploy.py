import os
import boto3
import time
from datetime import datetime
from sagemaker import image_uris

class ModelDeployer:
    def __init__(self, bucket_name, role_arn, region_name='us-east-1'):
        self.bucket_name = bucket_name
        self.role_arn = role_arn
        self.region_name = region_name
        self.sagemaker_client = boto3.client('sagemaker', region_name=region_name)
        
    def deploy_serverless(self, model_s3_path=None):
        """Deploy model using SageMaker Serverless Inference with boto3 client"""
        
        if not model_s3_path:
            model_s3_path = f's3://{self.bucket_name}/models/model.tar.gz'
        
        endpoint_name = 'mlops-endpoint'
        
        # Check if endpoint exists
        try:
            self.sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            print(f"Endpoint {endpoint_name} exists, updating with new model...")
            return self._update_endpoint(model_s3_path, endpoint_name)
        except self.sagemaker_client.exceptions.ClientError as e:
            if 'does not exist' in str(e):
                print(f"Creating new serverless endpoint {endpoint_name}...")
                return self._create_endpoint(model_s3_path, endpoint_name)
            else:
                raise e
    
    def _create_endpoint(self, model_s3_path, endpoint_name):
        """Create new serverless endpoint using boto3 client"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        model_name = f'mlops-model-{timestamp}'
        config_name = f'mlops-endpoint-config-{timestamp}'
        
        # 1. Create SageMaker Model
        print(f"Creating SageMaker model: {model_name}")
        
        # Get the correct SageMaker-managed sklearn container image for the region
        sklearn_image_uri = image_uris.retrieve(
            framework="sklearn",
            region=self.region_name,
            version="1.2-1",
            py_version="py3",
            instance_type="ml.m5.large"  # Required parameter, but not used for serverless
        )
        print(f"Using container image: {sklearn_image_uri}")
        
        self.sagemaker_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': sklearn_image_uri,
                'ModelDataUrl': model_s3_path,
                'Environment': {
                    'SAGEMAKER_PROGRAM': 'inference.py',
                    'SAGEMAKER_SUBMIT_DIRECTORY': '/opt/ml/code'
                }
            },
            ExecutionRoleArn=self.role_arn,
            Tags=[
                {'Key': 'Project', 'Value': 'mlops-showcase'},
                {'Key': 'ManagedBy', 'Value': 'python-deployment'}
            ]
        )
        
        # 2. Create Endpoint Configuration with Serverless
        print(f"Creating endpoint configuration: {config_name}")
        print("Note: Data capture is not supported for serverless endpoints")
        
        self.sagemaker_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    'VariantName': 'primary',
                    'ModelName': model_name,
                    'ServerlessConfig': {
                        'MemorySizeInMB': 2048,
                        'MaxConcurrency': 1
                    }
                }
            ],
            Tags=[
                {'Key': 'Project', 'Value': 'mlops-showcase'},
                {'Key': 'ManagedBy', 'Value': 'python-deployment'}
            ]
        )
        
        # 3. Create Endpoint
        print(f"Creating endpoint: {endpoint_name}")
        
        self.sagemaker_client.create_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name,
            Tags=[
                {'Key': 'Project', 'Value': 'mlops-showcase'},
                {'Key': 'ManagedBy', 'Value': 'python-deployment'}
            ]
        )
        
        print(f"Endpoint creation initiated. Endpoint: {endpoint_name}")
        return endpoint_name
    
    def _update_endpoint(self, model_s3_path, endpoint_name):
        """Update existing endpoint with new model"""
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        model_name = f'mlops-model-{timestamp}'
        config_name = f'mlops-endpoint-config-{timestamp}'
        
        # Create new model
        print(f"Creating new model for update: {model_name}")
        
        # Get the correct SageMaker-managed sklearn container image for the region
        sklearn_image_uri = image_uris.retrieve(
            framework="sklearn",
            region=self.region_name,
            version="1.2-1",
            py_version="py3",
            instance_type="ml.m5.large"  # Required parameter, but not used for serverless
        )
        print(f"Using container image: {sklearn_image_uri}")
        
        self.sagemaker_client.create_model(
            ModelName=model_name,
            PrimaryContainer={
                'Image': sklearn_image_uri,
                'ModelDataUrl': model_s3_path,
                'Environment': {
                    'SAGEMAKER_PROGRAM': 'inference.py',
                    'SAGEMAKER_SUBMIT_DIRECTORY': '/opt/ml/code'
                }
            },
            ExecutionRoleArn=self.role_arn,
            Tags=[
                {'Key': 'Project', 'Value': 'mlops-showcase'},
                {'Key': 'ManagedBy', 'Value': 'python-deployment'}
            ]
        )
        
        # Create new endpoint configuration
        print(f"Creating new endpoint configuration: {config_name}")
        
        self.sagemaker_client.create_endpoint_config(
            EndpointConfigName=config_name,
            ProductionVariants=[
                {
                    'VariantName': 'primary',
                    'ModelName': model_name,
                    'ServerlessConfig': {
                        'MemorySizeInMB': 2048,
                        'MaxConcurrency': 1
                    }
                }
            ],
            DataCaptureConfig={
                'EnableCapture': True,
                'InitialSamplingPercentage': 100,
                'DestinationS3Uri': f's3://{self.bucket_name}/data-capture',
                'CaptureOptions': [
                    {'CaptureMode': 'Input'},
                    {'CaptureMode': 'Output'}
                ],
                'CaptureContentTypeHeader': {
                    'CsvContentTypes': ['text/csv'],
                    'JsonContentTypes': ['application/json']
                }
            },
            Tags=[
                {'Key': 'Project', 'Value': 'mlops-showcase'},
                {'Key': 'ManagedBy', 'Value': 'python-deployment'}
            ]
        )
        
        # Update endpoint
        print(f"Updating endpoint: {endpoint_name}")
        
        self.sagemaker_client.update_endpoint(
            EndpointName=endpoint_name,
            EndpointConfigName=config_name
        )
        
        print(f"Endpoint update initiated. Endpoint: {endpoint_name}")
        return endpoint_name
    
    def _cleanup_existing_endpoints(self, endpoint_prefix):
        """Delete all endpoints and models matching the prefix"""
        sagemaker_client = boto3.client('sagemaker')
        
        try:
            # List all endpoints
            response = sagemaker_client.list_endpoints()
            
            # Find endpoints with our prefix
            matching_endpoints = [
                ep['EndpointName'] for ep in response['Endpoints']
                if ep['EndpointName'].startswith(endpoint_prefix)
            ]
            
            # Delete each matching endpoint
            for endpoint_name in matching_endpoints:
                print(f"Deleting existing endpoint: {endpoint_name}")
                self._delete_endpoint(endpoint_name)
            
            # Also cleanup old models
            self._cleanup_old_models(endpoint_prefix)
                
        except Exception as e:
            print(f"Error during cleanup: {e}")
    
    def _cleanup_old_models(self, model_prefix):
        """Delete old SageMaker models"""
        sagemaker_client = boto3.client('sagemaker')
        
        try:
            # List all models
            response = sagemaker_client.list_models()
            
            # Find models with our prefix
            matching_models = [
                model['ModelName'] for model in response['Models']
                if model['ModelName'].startswith(model_prefix)
            ]
            
            # Delete each matching model
            for model_name in matching_models:
                try:
                    sagemaker_client.delete_model(ModelName=model_name)
                    print(f"Deleted model: {model_name}")
                except Exception as e:
                    print(f"Error deleting model {model_name}: {e}")
                    
        except Exception as e:
            print(f"Error during model cleanup: {e}")
    
    def _delete_endpoint(self, endpoint_name):
        """Delete existing endpoint and its configuration"""
        sagemaker_client = boto3.client('sagemaker')
        
        try:
            # Get endpoint config name and model names before deleting endpoint
            endpoint_info = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            config_name = endpoint_info['EndpointConfigName']
            
            # Get model names from endpoint config
            config_info = sagemaker_client.describe_endpoint_config(EndpointConfigName=config_name)
            model_names = [variant['ModelName'] for variant in config_info['ProductionVariants']]
            
            # Delete endpoint
            sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            print(f"Deleted endpoint: {endpoint_name}")
            
            # Wait for endpoint deletion to complete
            waiter = sagemaker_client.get_waiter('endpoint_deleted')
            waiter.wait(EndpointName=endpoint_name)
            
            # Delete endpoint configuration
            sagemaker_client.delete_endpoint_config(EndpointConfigName=config_name)
            print(f"Deleted endpoint config: {config_name}")
            
            # Delete associated models
            for model_name in model_names:
                try:
                    sagemaker_client.delete_model(ModelName=model_name)
                    print(f"Deleted model: {model_name}")
                except Exception as e:
                    print(f"Error deleting model {model_name}: {e}")
            
            # Small wait to ensure cleanup is complete
            import time
            time.sleep(5)
            
        except Exception as e:
            print(f"Error deleting endpoint: {e}")
    
    def test_endpoint(self, endpoint_name, test_data):
        """Test the deployed endpoint"""
        runtime = boto3.client('sagemaker-runtime')
        
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Body=test_data
        )
        
        result = response['Body'].read().decode()
        return result

if __name__ == "__main__":
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    role_arn = os.environ.get('SAGEMAKER_ROLE_ARN')
    region_name = os.environ.get('AWS_REGION', 'us-east-1')
    
    if not bucket_name or not role_arn:
        print("❌ Please set S3_BUCKET_NAME and SAGEMAKER_ROLE_ARN environment variables")
        exit(1)
    
    print(f"🚀 Starting deployment...")
    print(f"   S3 Bucket: {bucket_name}")
    print(f"   IAM Role: {role_arn}")
    print(f"   Region: {region_name}")
    
    deployer = ModelDeployer(bucket_name, role_arn, region_name)
    
    try:
        print("📦 Deploying model to serverless endpoint...")
        endpoint_name = deployer.deploy_serverless()
        print(f"✅ Deployment initiated successfully!")
        print(f"   Endpoint: {endpoint_name}")
        print(f"   Note: Endpoint will take a few minutes to become InService")
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        exit(1)