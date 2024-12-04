# ================================================================
# Config
# ================================================================

terraform {
  required_version = "~> 1.9"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.72"
    }
  }

  backend "s3" {
    bucket         = null
    key            = null
    dynamodb_table = null
    region         = null
  }
}

# ================================================================
# Provider
# ================================================================

provider "aws" {
  region = var.REGION

  default_tags {
    tags = {
      SystemName = var.SYSTEM_NAME
    }
  }
}

# ================================================================
# Modules
# ================================================================

module "common" {
  source = "./terraform_modules/common"

  system_name = var.SYSTEM_NAME
  region      = var.REGION

  ssm_parameter_name_layer_arn_base = var.SSM_PARAMETER_NAME_LAYER_ARN_BASE
  s3_bucket_data                    = var.S3_BUCKET_DATA
  notion_database_id                = var.NOTION_DATABASE_ID
  notion_token                      = var.NOTION_TOKEN
  contentful_token                  = var.CONTENTFUL_TOKEN

  slack_incoming_webhook_error_notifier_01 = var.SLACK_INCOMING_WEBHOOK_ERROR_NOTIFIER_01
}

# ================================================================
# Variables
# ================================================================

variable "SYSTEM_NAME" {
  type     = string
  nullable = false
}

variable "REGION" {
  type     = string
  nullable = false
}

variable "SSM_PARAMETER_NAME_LAYER_ARN_BASE" {
  type     = string
  nullable = false
}

variable "SLACK_INCOMING_WEBHOOK_ERROR_NOTIFIER_01" {
  type     = string
  nullable = false
}

variable "S3_BUCKET_DATA" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "NOTION_DATABASE_ID" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "NOTION_TOKEN" {
  type      = string
  nullable  = false
  sensitive = true
}

variable "CONTENTFUL_TOKEN" {
  type      = string
  nullable  = false
  sensitive = true
}
