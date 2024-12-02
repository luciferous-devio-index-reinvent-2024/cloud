# ================================================================
# Slack Error Notifier
# ================================================================

resource "aws_cloudwatch_metric_alarm" "catch_error_lambda_error_processor" {
  alarm_name          = "catch-error-lambda-error-processor"
  alarm_actions       = [aws_sns_topic.catch_error_lambda_error_processor.arn]
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = 1
  datapoints_to_alarm = 1

  dimensions = {
    FunctionName = module.lambda_error_processor.function_name
  }

  metric_name        = "Errors"
  namespace          = "AWS/Lambda"
  period             = 60
  statistic          = "Sum"
  treat_missing_data = "notBreaching"
}
