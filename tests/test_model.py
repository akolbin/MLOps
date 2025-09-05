import pytest
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.data.generate_data import generate_synthetic_data

def test_data_generation():
    """Test synthetic data generation"""
    train_df, test_df = generate_synthetic_data(n_samples=1000, test_size=0.2)
    
    assert len(train_df) == 800
    assert len(test_df) == 200
    assert 'target' in train_df.columns
    assert 'target' in test_df.columns
    assert train_df['target'].nunique() == 2  # Binary classification

def test_model_training():
    """Test model training functionality"""
    train_df, test_df = generate_synthetic_data(n_samples=1000, test_size=0.2)
    
    X_train = train_df.drop('target', axis=1)
    y_train = train_df['target']
    X_test = test_df.drop('target', axis=1)
    y_test = test_df['target']
    
    # Train model
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X_train, y_train)
    
    # Test predictions
    predictions = model.predict(X_test)
    probabilities = model.predict_proba(X_test)
    
    assert len(predictions) == len(test_df)
    assert probabilities.shape == (len(test_df), 2)
    assert all(pred in [0, 1] for pred in predictions)

def test_feature_consistency():
    """Test that features are consistent between train and test"""
    train_df, test_df = generate_synthetic_data(n_samples=1000, test_size=0.2)
    
    train_features = set(train_df.columns) - {'target'}
    test_features = set(test_df.columns) - {'target'}
    
    assert train_features == test_features
    assert len(train_features) == 20  # Expected number of features