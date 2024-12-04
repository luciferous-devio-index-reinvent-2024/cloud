data "aws_ssm_parameter" "layer_arn_base" {
  name = var.ssm_parameter_name_layer_arn_base
}

resource "aws_ssm_parameter" "notion_token" {
  name  = "NotionToken"
  type  = "SecureString"
  value = var.notion_token
}

resource "aws_ssm_parameter" "notion_database_id" {
  name  = "NotionDatabaseId"
  type  = "SecureString"
  value = var.notion_database_id
}

resource "aws_ssm_parameter" "contentful_token" {
  name  = "ContentfulToken"
  type  = "SecureString"
  value = var.contentful_token
}