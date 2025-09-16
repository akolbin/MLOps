#!/usr/bin/env python3
"""
MLOps Monitoring Script
Monitors model performance, data drift, and system health using Terraform-deployed infrastructure
"""

import boto3
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLOpsMonitor:
    def __init__(self, endpoint_name: str, bucket_name: str, region: str = 'us-east-1'):
        self.endpoint_name = endpoint_name
        self.bucket_name = bucket_name
        self.region = region
        
        # Initialize AWS clients
        self.cloudwatch = boto3.client('cloudwatch', region_name=region)
        self.sagemaker = boto3.client('sagemaker', region_name=region)
        self.s3 = boto3.client('s3', region_name=region)
        self.sns = boto3.client('sns', region_name=region)
        
    def get_endpoint_metrics(self, hours_back: int = 24) -> Dict:
        """Get CloudWatch metrics for the SageMaker endpoint"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(hours=hours_back)
        
        metrics = {}
        
        # Define metrics to collect
        metric_queries = [
            ('Invocations', 'Sum'),
            ('ModelLatency', 'Average'),
            ('ModelInvocation4XXErrors', 'Sum'),
            ('ModelInvocation5XXErrors', 'Sum'),
        ]
        
        for metric_name, statistic in metric_queries:
            try:
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/SageMaker',
                    MetricName=metric_name,
                    Dimensions=[
                        {'Name': 'EndpointName', 'Value': self.endpoint_name},
                        {'Name': 'VariantName', 'Value': 'primary'}
                    ],
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,  # 1 hour periods
                    Statistics=[statistic]
                )
                
                datapoints = response['Datapoints']
                if datapoints:
                    metrics[metric_name] = {
                        'latest_value': datapoints[-1][statistic],
                        'datapoints': len(datapoints),
                        'time_range': f"{start_time} to {end_time}"
                    }
                else:
                    metrics[metric_name] = {'latest_value': 0, 'datapoints': 0}
                    
            except Exception as e:
                logger.error(f"Error getting metric {metric_name}: {e}")
                metrics[metric_name] = {'error': str(e)}
        
        return metrics
    
    def check_endpoint_health(self) -> Dict:
        """Check the health status of the SageMaker endpoint"""
        try:
            response = self.sagemaker.describe_endpoint(EndpointName=self.endpoint_name)
            
            health_status = {
                'endpoint_name': self.endpoint_name,
                'status': response['EndpointStatus'],
                'creation_time': response['CreationTime'].isoformat(),
                'last_modified_time': response['LastModifiedTime'].isoformat(),
                'healthy': response['EndpointStatus'] == 'InService'
            }
            
            if 'FailureReason' in response:
                health_status['failure_reason'] = response['FailureReason']
            
            return health_status
            
        except Exception as e:
            logger.error(f"Error checking endpoint health: {e}")
            return {'endpoint_name': self.endpoint_name, 'healthy': False, 'error': str(e)}
    
    def analyze_data_capture(self, hours_back: int = 24) -> Dict:
        """Analyze captured inference data for drift detection"""
        try:
            # List objects in data capture prefix
            prefix = 'data-capture/'
            response = self.s3.list_objects_v2(
                Bucket=self.bucket_name,
                Prefix=prefix,
                MaxKeys=100
            )
            
            if 'Contents' not in response:
                return {'message': 'No data capture files found', 'files_analyzed': 0}
            
            # Filter files from the last N hours
            cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
            recent_files = [
                obj for obj in response['Contents']
                if obj['LastModified'].replace(tzinfo=None) > cutoff_time
            ]
            
            if not recent_files:
                return {'message': f'No data capture files from last {hours_back} hours', 'files_analyzed': 0}
            
            # Analyze a sample of recent files
            sample_size = min(10, len(recent_files))
            sample_files = recent_files[:sample_size]
            
            input_data = []
            output_data = []
            
            for file_obj in sample_files:
                try:
                    # Download and parse the JSONL file
                    obj = self.s3.get_object(Bucket=self.bucket_name, Key=file_obj['Key'])
                    content = obj['Body'].read().decode('utf-8')
                    
                    for line in content.strip().split('\n'):
                        if line:
                            record = json.loads(line)
                            if 'captureData' in record:
                                capture_data = record['captureData']
                                if capture_data.get('endpointInput'):
                                    input_data.append(capture_data['endpointInput']['data'])
                                if capture_data.get('endpointOutput'):
                                    output_data.append(capture_data['endpointOutput']['data'])
                                    
                except Exception as e:
                    logger.warning(f"Error processing file {file_obj['Key']}: {e}")
                    continue
            
            analysis = {
                'files_analyzed': len(sample_files),
                'total_recent_files': len(recent_files),
                'input_samples': len(input_data),
                'output_samples': len(output_data),
                'time_range': f"Last {hours_back} hours"
            }
            
            # Basic drift detection (simplified)
            if input_data:
                analysis['drift_indicators'] = self._detect_basic_drift(input_data)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing data capture: {e}")
            return {'error': str(e), 'files_analyzed': 0}
    
    def _detect_basic_drift(self, input_data: List[str]) -> Dict:
        """Basic drift detection on input data"""
        try:
            # Parse CSV input data
            parsed_data = []
            for data_str in input_data[:50]:  # Limit to 50 samples for performance
                try:
                    # Assuming CSV format
                    lines = data_str.strip().split('\n')
                    if len(lines) > 1:  # Skip header
                        values = [float(x) for x in lines[1].split(',')]
                        parsed_data.append(values)
                except:
                    continue
            
            if not parsed_data:
                return {'message': 'Could not parse input data for drift analysis'}
            
            # Convert to numpy array
            data_array = np.array(parsed_data)
            
            # Basic statistical analysis
            drift_indicators = {
                'samples_analyzed': len(parsed_data),
                'feature_count': data_array.shape[1] if len(data_array.shape) > 1 else 1,
                'mean_values': data_array.mean(axis=0).tolist() if len(data_array.shape) > 1 else [data_array.mean()],
                'std_values': data_array.std(axis=0).tolist() if len(data_array.shape) > 1 else [data_array.std()],
                'drift_score': 'low'  # Placeholder - would implement proper drift detection
            }
            
            return drift_indicators
            
        except Exception as e:
            return {'error': f'Drift analysis failed: {e}'}
    
    def send_alert(self, topic_arn: str, subject: str, message: str):
        """Send alert via SNS"""
        try:
            self.sns.publish(
                TopicArn=topic_arn,
                Subject=subject,
                Message=message
            )
            logger.info(f"Alert sent: {subject}")
        except Exception as e:
            logger.error(f"Failed to send alert: {e}")
    
    def generate_health_report(self) -> Dict:
        """Generate comprehensive health report"""
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'endpoint_health': self.check_endpoint_health(),
            'metrics': self.get_endpoint_metrics(),
            'data_capture_analysis': self.analyze_data_capture()
        }
        
        # Determine overall health
        endpoint_healthy = report['endpoint_health'].get('healthy', False)
        metrics_healthy = True
        
        # Check for high error rates
        if 'ModelInvocation4XXErrors' in report['metrics']:
            error_4xx = report['metrics']['ModelInvocation4XXErrors'].get('latest_value', 0)
            if error_4xx > 5:  # More than 5 4XX errors
                metrics_healthy = False
        
        if 'ModelInvocation5XXErrors' in report['metrics']:
            error_5xx = report['metrics']['ModelInvocation5XXErrors'].get('latest_value', 0)
            if error_5xx > 0:  # Any 5XX errors
                metrics_healthy = False
        
        # Check latency
        if 'ModelLatency' in report['metrics']:
            latency = report['metrics']['ModelLatency'].get('latest_value', 0)
            if latency > 5000:  # More than 5 seconds
                metrics_healthy = False
        
        report['overall_health'] = {
            'status': 'healthy' if endpoint_healthy and metrics_healthy else 'unhealthy',
            'endpoint_healthy': endpoint_healthy,
            'metrics_healthy': metrics_healthy
        }
        
        return report
    
    def save_report(self, report: Dict, s3_key: str = None):
        """Save monitoring report to S3"""
        if not s3_key:
            timestamp = datetime.utcnow().strftime('%Y/%m/%d/%H%M%S')
            s3_key = f"monitoring-reports/{timestamp}-health-report.json"
        
        try:
            self.s3.put_object(
                Bucket=self.bucket_name,
                Key=s3_key,
                Body=json.dumps(report, indent=2, default=str),
                ContentType='application/json'
            )
            logger.info(f"Report saved to s3://{self.bucket_name}/{s3_key}")
        except Exception as e:
            logger.error(f"Failed to save report: {e}")

def main():
    """Main monitoring function"""
    import os
    
    # Get configuration from environment or Terraform outputs
    endpoint_name = os.environ.get('SAGEMAKER_ENDPOINT_NAME', 'mlops-showcase-endpoint')
    bucket_name = os.environ.get('S3_BUCKET_NAME')
    region = os.environ.get('AWS_REGION', 'us-east-1')
    sns_topic_arn = os.environ.get('SNS_TOPIC_ARN')
    
    if not bucket_name:
        print("Error: S3_BUCKET_NAME environment variable not set")
        return
    
    # Initialize monitor
    monitor = MLOpsMonitor(endpoint_name, bucket_name, region)
    
    # Generate health report
    print("Generating MLOps health report...")
    report = monitor.generate_health_report()
    
    # Print report
    print("\n" + "="*60)
    print("MLOPS HEALTH REPORT")
    print("="*60)
    print(f"Timestamp: {report['timestamp']}")
    print(f"Overall Status: {report['overall_health']['status'].upper()}")
    print()
    
    # Endpoint health
    endpoint_health = report['endpoint_health']
    print(f"Endpoint Health:")
    print(f"  Name: {endpoint_health['endpoint_name']}")
    print(f"  Status: {endpoint_health['status']}")
    print(f"  Healthy: {endpoint_health['healthy']}")
    print()
    
    # Metrics
    print("Metrics (Last 24 hours):")
    for metric_name, metric_data in report['metrics'].items():
        if 'error' not in metric_data:
            print(f"  {metric_name}: {metric_data['latest_value']}")
    print()
    
    # Data capture
    data_analysis = report['data_capture_analysis']
    print("Data Capture Analysis:")
    print(f"  Files analyzed: {data_analysis.get('files_analyzed', 0)}")
    print(f"  Input samples: {data_analysis.get('input_samples', 0)}")
    print(f"  Output samples: {data_analysis.get('output_samples', 0)}")
    print()
    
    # Save report
    monitor.save_report(report)
    
    # Send alert if unhealthy
    if report['overall_health']['status'] == 'unhealthy' and sns_topic_arn:
        alert_message = f"""
MLOps Health Alert

Endpoint: {endpoint_name}
Status: UNHEALTHY
Timestamp: {report['timestamp']}

Issues detected:
- Endpoint Healthy: {report['overall_health']['endpoint_healthy']}
- Metrics Healthy: {report['overall_health']['metrics_healthy']}

Please check the CloudWatch dashboard for more details.
        """
        
        monitor.send_alert(
            sns_topic_arn,
            f"MLOps Alert: {endpoint_name} Unhealthy",
            alert_message.strip()
        )
    
    print("Monitoring complete!")

if __name__ == "__main__":
    main()