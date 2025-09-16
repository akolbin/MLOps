# SNS Topic for MLOps alerts
resource "aws_sns_topic" "mlops_alerts" {
  name = "${var.project_name}-alerts"
  
  tags = var.tags
}

resource "aws_sns_topic_subscription" "email_alerts" {
  count     = var.alert_email != "" ? 1 : 0
  topic_arn = aws_sns_topic.mlops_alerts.arn
  protocol  = "email"
  endpoint  = var.alert_email
}

# CloudWatch Alarms for Model Monitoring
resource "aws_cloudwatch_metric_alarm" "model_latency_alarm" {
  alarm_name          = "${var.project_name}-model-latency"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ModelLatency"
  namespace           = "AWS/SageMaker"
  period              = "300"
  statistic           = "Average"
  threshold           = var.latency_threshold_ms
  alarm_description   = "This metric monitors model inference latency"
  alarm_actions       = [aws_sns_topic.mlops_alerts.arn]

  dimensions = {
    EndpointName = var.endpoint_name
    VariantName  = "primary"
  }

  tags = var.tags
}

resource "aws_cloudwatch_metric_alarm" "model_error_rate_alarm" {
  alarm_name          = "${var.project_name}-model-error-rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ModelInvocation4XXErrors"
  namespace           = "AWS/SageMaker"
  period              = "300"
  statistic           = "Sum"
  threshold           = var.error_rate_threshold
  alarm_description   = "This metric monitors model error rate"
  alarm_actions       = [aws_sns_topic.mlops_alerts.arn]

  dimensions = {
    EndpointName = var.endpoint_name
    VariantName  = "primary"
  }

  tags = var.tags
}

# CloudWatch Dashboard for MLOps Monitoring
resource "aws_cloudwatch_dashboard" "mlops_dashboard" {
  dashboard_name = "${var.project_name}-mlops-dashboard"

  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        x      = 0
        y      = 0
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/SageMaker", "Invocations", "EndpointName", var.endpoint_name, "VariantName", "primary"],
            [".", "ModelLatency", ".", ".", ".", "."],
            [".", "ModelInvocation4XXErrors", ".", ".", ".", "."],
            [".", "ModelInvocation5XXErrors", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "SageMaker Endpoint Metrics"
          period  = 300
        }
      },
      {
        type   = "metric"
        x      = 0
        y      = 6
        width  = 12
        height = 6

        properties = {
          metrics = [
            ["AWS/SageMaker", "CPUUtilization", "EndpointName", var.endpoint_name, "VariantName", "primary"],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
          view    = "timeSeries"
          stacked = false
          region  = var.aws_region
          title   = "Resource Utilization"
          period  = 300
        }
      }
    ]
  })
}

# EventBridge Rule for Model Drift Detection
resource "aws_cloudwatch_event_rule" "model_drift_check" {
  name                = "${var.project_name}-model-drift-check"
  description         = "Trigger model drift detection"
  schedule_expression = var.drift_check_schedule

  tags = var.tags
}