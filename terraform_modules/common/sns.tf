# ================================================================
# Topic Catch Error ErrorProcessor
# ================================================================

resource "aws_sns_topic" "catch_error_lambda_error_processor" {}

# ================================================================
# Topic Notification Insert
# ================================================================

resource "aws_sns_topic" "notification_insert" {
  name_prefix = "notification-insert-"
}
