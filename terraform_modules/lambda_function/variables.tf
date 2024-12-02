variable "s3_bucket_deploy_package" {
  type     = string
  nullable = false
}

variable "s3_key_deploy_package" {
  type     = string
  nullable = false
}

variable "source_code_hash" {
  type     = string
  nullable = false
}

variable "identifier" {
  type     = string
  nullable = false
}

variable "system_name" {
  type     = string
  nullable = false
}

variable "role_arn" {
  type     = string
  nullable = false
}

variable "runtime" {
  type     = string
  nullable = false
  default  = "python3.12"
}

variable "handler" {
  type     = string
  nullable = false
}

variable "memory_size" {
  type     = number
  nullable = false
  default  = 256
}

variable "timeout" {
  type     = number
  nullable = false
  default  = 120
}

variable "layers" {
  type     = list(string)
  nullable = false
  default  = []
}

variable "reserved_concurrent_executions" {
  type     = number
  nullable = true
  default  = null
}

variable "region" {
  type     = string
  nullable = false
}

variable "environment_variables" {
  type     = map(string)
  nullable = false
  default  = {}
}

variable "alias" {
  type     = string
  nullable = false
  default  = "alias"
}

variable "subscription_destination_lambda_arn" {
  type     = string
  nullable = false
}