import pandas as pd
import numpy as np
from sklearn.datasets import make_classification
import boto3
import os

def generate_synthetic_data(n_samples=10000, test_size=0.2):
    """Generate synthetic binary classification dataset"""
    X, y = make_classification(
        n_samples=n_samples,
        n_features=20,
        n_informative=15,
        n_redundant=5,
        n_clusters_per_class=1,
        random_state=42
    )
    
    # Create feature names
    feature_names = [f'feature_{i}' for i in range(X.shape[1])]
    
    # Create DataFrame
    df = pd.DataFrame(X, columns=feature_names)
    df['target'] = y
    
    # Split into train/test
    split_idx = int(len(df) * (1 - test_size))
    train_df = df[:split_idx]
    test_df = df[split_idx:]
    
    return train_df, test_df

def upload_to_s3(df, bucket_name, key):
    """Upload DataFrame to S3 as CSV"""
    s3 = boto3.client('s3')
    csv_buffer = df.to_csv(index=False)
    s3.put_object(Bucket=bucket_name, Key=key, Body=csv_buffer)
    print(f"Uploaded {key} to s3://{bucket_name}/{key}")

if __name__ == "__main__":
    # Generate data
    train_df, test_df = generate_synthetic_data()
    
    # Debug: Print all environment variables containing S3 or BUCKET
    print("Environment variables:")
    for key, value in os.environ.items():
        if 'S3' in key or 'BUCKET' in key:
            print(f"{key}={value}")
    
    # Get bucket name from environment
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    if not bucket_name:
        print("S3_BUCKET_NAME environment variable not found")
        print("Available environment variables:")
        for key in sorted(os.environ.keys()):
            print(f"  {key}")
        exit(1)
    
    print(f"Using bucket: {bucket_name}")
    
    # Upload to S3
    upload_to_s3(train_df, bucket_name, 'data/train.csv')
    upload_to_s3(test_df, bucket_name, 'data/test.csv')
    
    print(f"Generated {len(train_df)} training samples and {len(test_df)} test samples")