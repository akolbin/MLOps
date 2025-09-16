#!/usr/bin/env python3
"""
Check if model artifacts exist in S3 before deployment
"""

import os
import boto3
from botocore.exceptions import ClientError

def check_model_exists(bucket_name, model_key='models/model.tar.gz'):
    """Check if model artifacts exist in S3"""
    s3_client = boto3.client('s3')
    
    try:
        response = s3_client.head_object(Bucket=bucket_name, Key=model_key)
        size_mb = response['ContentLength'] / (1024 * 1024)
        last_modified = response['LastModified']
        
        print(f"✅ Model found in S3:")
        print(f"   Location: s3://{bucket_name}/{model_key}")
        print(f"   Size: {size_mb:.2f} MB")
        print(f"   Last Modified: {last_modified}")
        return True
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        if error_code == '404':
            print(f"❌ Model not found: s3://{bucket_name}/{model_key}")
            print("   Make sure to train the model first!")
        else:
            print(f"❌ Error checking model: {e}")
        return False

if __name__ == "__main__":
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    
    if not bucket_name:
        print("❌ Please set S3_BUCKET_NAME environment variable")
        exit(1)
    
    if check_model_exists(bucket_name):
        print("🚀 Ready for deployment!")
    else:
        print("⏳ Train model first before deployment")
        exit(1)