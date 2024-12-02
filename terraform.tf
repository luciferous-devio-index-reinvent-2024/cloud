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

  layer_arn_base                           = var.LAYER_ARN_BASE
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

variable "LAYER_ARN_BASE" {
  type     = string
  nullable = false
}

variable "SLACK_INCOMING_WEBHOOK_ERROR_NOTIFIER_01" {
  type     = string
  nullable = false
}
