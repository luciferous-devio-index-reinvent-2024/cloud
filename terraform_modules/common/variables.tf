variable "system_name" {
  type     = string
  nullable = false
}

variable "region" {
  type     = string
  nullable = false
}

variable "ssm_parameter_name_layer_arn_base" {
  type     = string
  nullable = false
}

variable "s3_bucket_data" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "slack_incoming_webhook_error_notifier_01" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "notion_database_id" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "notion_token" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "contentful_token" {
  type      = string
  nullable  = false
  sensitive = true
}
