resource "aws_cloudwatch_event_rule" "slack_error_notifier" {
  event_bus_name = var.event_bus_name
  state          = "ENABLED"
  event_pattern = jsonencode({
    account = [data.aws_caller_identity.current.account_id]
  })
}

resource "aws_cloudwatch_event_api_destination" "slack" {
  connection_arn      = var.connection_arn_slack_dummy
  http_method         = "POST"
  invocation_endpoint = var.slack_incoming_webhook_url
  name                = var.api_destination_name
}

resource "aws_cloudwatch_event_target" "slack" {
  arn            = aws_cloudwatch_event_api_destination.slack.arn
  rule           = aws_cloudwatch_event_rule.slack_error_notifier.name
  event_bus_name = var.event_bus_name
  role_arn       = var.iam_role_arn

  input_transformer {
    input_template = "{\"blocks\": <blocks>}"
    input_paths = {
      blocks = "$.detail.blocks"
    }
  }
}