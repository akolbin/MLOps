import os
import joblib
import pandas as pd
from io import StringIO

def model_fn(model_dir):
    """Load model for inference"""
    model = joblib.load(os.path.join(model_dir, "model.pkl"))
    return model

def input_fn(request_body, content_type):
    """Parse input data"""
    if content_type == 'text/csv':
        df = pd.read_csv(StringIO(request_body))
        return df
    else:
        raise ValueError(f"Unsupported content type: {content_type}")

def predict_fn(input_data, model):
    """Make predictions"""
    predictions = model.predict(input_data)
    probabilities = model.predict_proba(input_data)
    
    return {
        'predictions': predictions.tolist(),
        'probabilities': probabilities.tolist()
    }

def output_fn(prediction, accept):
    """Format output"""
    import json
    return json.dumps(prediction), 'application/json'