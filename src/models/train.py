import os
import boto3
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import sagemaker
from sagemaker.sklearn.estimator import SKLearn

class ModelTrainer:
    def __init__(self, bucket_name, role_arn):
        self.bucket_name = bucket_name
        self.role_arn = role_arn
        self.sagemaker_session = sagemaker.Session()
        
    def train_local(self):
        """Train model locally for testing"""
        s3 = boto3.client('s3')
        
        # Download training data
        s3.download_file(self.bucket_name, 'data/train.csv', '/tmp/train.csv')
        s3.download_file(self.bucket_name, 'data/test.csv', '/tmp/test.csv')
        
        # Load data
        train_df = pd.read_csv('/tmp/train.csv')
        test_df = pd.read_csv('/tmp/test.csv')
        
        # Prepare features and target
        X_train = train_df.drop('target', axis=1)
        y_train = train_df['target']
        X_test = test_df.drop('target', axis=1)
        y_test = test_df['target']
        
        # Train model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"Model Accuracy: {accuracy:.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        # Save model
        joblib.dump(model, '/tmp/model.pkl')
        
        # Upload model to S3
        s3.upload_file('/tmp/model.pkl', self.bucket_name, 'models/model.pkl')
        print(f"Model uploaded to s3://{self.bucket_name}/models/model.pkl")
        
        return accuracy
    
    def train_sagemaker(self):
        """Train model using SageMaker Training Job"""
        sklearn_estimator = SKLearn(
            entry_point='train_script.py',
            source_dir='src/models',
            role=self.role_arn,
            instance_type='ml.m5.large',
            framework_version='1.2-1',
            py_version='py3',
            script_mode=True,
            hyperparameters={
                'n_estimators': 100,
                'random_state': 42
            }
        )
        
        # Set up data channels
        train_input = sagemaker.inputs.TrainingInput(
            s3_data=f's3://{self.bucket_name}/data/train.csv',
            content_type='text/csv'
        )
        
        test_input = sagemaker.inputs.TrainingInput(
            s3_data=f's3://{self.bucket_name}/data/test.csv',
            content_type='text/csv'
        )
        
        # Start training
        sklearn_estimator.fit({
            'train': train_input,
            'test': test_input
        })
        
        return sklearn_estimator

if __name__ == "__main__":
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    role_arn = os.environ.get('SAGEMAKER_ROLE_ARN')
    
    if not bucket_name or not role_arn:
        print("Please set S3_BUCKET_NAME and SAGEMAKER_ROLE_ARN environment variables")
        exit(1)
    
    trainer = ModelTrainer(bucket_name, role_arn)
    
    # Train locally first
    print("Training model locally...")
    accuracy = trainer.train_local()
    
    print(f"\nLocal training completed with accuracy: {accuracy:.4f}")