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
        
        endpoint_name = 'mlops-showcase-endpoint'
        sagemaker_client = boto3.client('sagemaker')
        
        # Check if endpoint exists
        try:
            sagemaker_client.describe_endpoint(EndpointName=endpoint_name)
            print(f"Endpoint {endpoint_name} exists, deleting and recreating...")
            self._delete_endpoint(endpoint_name)
            return self._create_endpoint(model_s3_path, endpoint_name)
        except sagemaker_client.exceptions.ClientError:
            print(f"Creating new endpoint {endpoint_name}...")
            return self._create_endpoint(model_s3_path, endpoint_name)
    
    def _create_endpoint(self, model_s3_path, endpoint_name):
        """Create new endpoint"""
        sklearn_model = SKLearnModel(
            model_data=model_s3_path,
            role=self.role_arn,
            entry_point='inference.py',
            source_dir='src/inference',
            framework_version='1.2-1',
            py_version='py3'
        )
        
        serverless_config = ServerlessInferenceConfig(
            memory_size_in_mb=2048,
            max_concurrency=1
        )
        
        predictor = sklearn_model.deploy(
            serverless_inference_config=serverless_config,
            endpoint_name=endpoint_name
        )
        
        print(f"Model deployed to new endpoint: {predictor.endpoint_name}")
        return predictor
    
    def _delete_endpoint(self, endpoint_name):
        """Delete existing endpoint and its configuration"""
        sagemaker_client = boto3.client('sagemaker')
        
        try:
            # Delete endpoint
            sagemaker_client.delete_endpoint(EndpointName=endpoint_name)
            print(f"Deleted endpoint: {endpoint_name}")
            
            # Wait for deletion to complete
            waiter = sagemaker_client.get_waiter('endpoint_deleted')
            waiter.wait(EndpointName=endpoint_name)
            
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