terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "5.54.1"
    }
  }
}
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
