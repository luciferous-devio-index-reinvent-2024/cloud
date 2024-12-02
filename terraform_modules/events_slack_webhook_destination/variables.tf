variable "event_bus_name" {
  type     = string
  nullable = false
}

variable "iam_role_arn" {
  type     = string
  nullable = false
}

variable "connection_arn_slack_dummy" {
  type     = string
  nullable = false
}

variable "slack_incoming_webhook_url" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "api_destination_name" {
  type     = string
  nullable = false
}
