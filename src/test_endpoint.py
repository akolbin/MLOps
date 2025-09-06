import boto3
import pandas as pd
import numpy as np

def test_model_endpoint():
    """Test the deployed SageMaker endpoint with sample data"""
    
    # Find the endpoint (assuming it starts with our prefix)
    sagemaker_client = boto3.client('sagemaker')
    
    try:
        # List endpoints to find ours
        response = sagemaker_client.list_endpoints()
        endpoint_name = "mlops-showcase-endpoint-5ccdd2f9"
        
        # for endpoint in response['Endpoints']:
        #     if endpoint['EndpointName'].startswith('mlops-showcase-endpoint'):
        #         endpoint_name = endpoint['EndpointName']
        #         break
        
        # if not endpoint_name:
        #     print("No MLOps endpoint found!")
        #     return
        
        # print(f"Found endpoint: {endpoint_name}")
        
        # Create sample data (same format as training data - 20 features)
        sample_data = pd.DataFrame({
            f'feature_{i}': np.random.randn(3) for i in range(20)
        })
        
        print("Sample input data:")
        print(sample_data)
        
        # Convert to CSV format for the endpoint
        csv_data = sample_data.to_csv(index=False)
        
        # Call the endpoint
        runtime = boto3.client('sagemaker-runtime')
        
        response = runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='text/csv',
            Body=csv_data
        )
        
        # Parse the response
        result = response['Body'].read().decode()
        print(f"\nModel predictions:")
        print(result)
        
    except Exception as e:
        print(f"Error testing endpoint: {e}")

if __name__ == "__main__":
    test_model_endpoint()