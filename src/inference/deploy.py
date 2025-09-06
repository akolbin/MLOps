import os
import boto3
import sagemaker
from sagemaker.sklearn.model import SKLearnModel
from sagemaker.serverless import ServerlessInferenceConfig

class ModelDeployer:
    def __init__(self, bucket_name, role_arn):
        self.bucket_name = bucket_name
        self.role_arn = role_arn
        self.sagemaker_session = sagemaker.Session()
        
    def deploy_serverless(self, model_s3_path=None):
        """Deploy model using SageMaker Serverless Inference"""
        
        if not model_s3_path:
            model_s3_path = f's3://{self.bucket_name}/models/model.tar.gz'
        
        endpoint_prefix = 'mlops-showcase-endpoint'
        sagemaker_client = boto3.client('sagemaker')
        
        # Delete any existing endpoints with our prefix
        self._cleanup_existing_endpoints(endpoint_prefix)
        
        # Create new endpoint with UUID
        import uuid
        endpoint_name = f"{endpoint_prefix}-{str(uuid.uuid4())[:8]}"
        print(f"Creating new endpoint {endpoint_name}...")
        return self._create_endpoint(model_s3_path, endpoint_name)
    
    def _create_endpoint(self, model_s3_path, endpoint_name):
        """Create new endpoint"""
        sklearn_model = SKLearnModel(
            model_data=model_s3_path,
            role=self.role_arn,
            entry_point='inference.py',
            source_dir='src/inference',
            framework_version='0.23-1',
            py_version='py3'
        )
        
        predictor = sklearn_model.deploy(
            initial_instance_count=1,
            instance_type='ml.t2.medium',
            endpoint_name=endpoint_name
        )
        
        print(f"Model deployed to new endpoint: {predictor.endpoint_name}")
        return predictor
    
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
            # Get endpoint config name before deleting endpoint
            endpoint_info = sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            config_name = endpoint_info['EndpointConfigName']
            
            # Delete endpoint
            sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            print(f"Deleted endpoint: {endpoint_name}")
            
            # Wait for endpoint deletion to complete
            waiter = sagemaker_client.get_waiter('endpoint_deleted')
            waiter.wait(EndpointName=endpoint_name)
            
            # Delete endpoint configuration
            sagemaker_client.delete_endpoint_config(EndpointConfigName=config_name)
            print(f"Deleted endpoint config: {config_name}")
            
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
    
    if not bucket_name or not role_arn:
        print("Please set S3_BUCKET_NAME and SAGEMAKER_ROLE_ARN environment variables")
        exit(1)
    
    deployer = ModelDeployer(bucket_name, role_arn)
    
    print("Deploying model to serverless endpoint...")
    predictor = deployer.deploy_serverless()
    
    print(f"Deployment completed. Endpoint: {predictor.endpoint_name}")