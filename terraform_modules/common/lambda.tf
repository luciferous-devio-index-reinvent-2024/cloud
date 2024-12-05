locals {
  lambda = {
    runtime = "python3.13"
  }
}

# ================================================================
# Lambda Deploy Package
# ================================================================

data "archive_file" "lambda_deploy_package" {
  type        = "zip"
  output_path = "lambda_deploy_package.zip"
  source_dir  = "${path.root}/src"
}

resource "aws_s3_object" "lambda_deploy_package" {
  bucket = var.s3_bucket_data
  key    = "artifacts/cloud/lambda_deploy_package.zip"
  source = data.archive_file.lambda_deploy_package.output_path
  etag   = data.archive_file.lambda_deploy_package.output_md5
}

# ================================================================
# Lambda Error Processor
# ================================================================

module "lambda_error_processor" {
  source = "../lambda_function_basic"

  identifier = "error_processor"
  handler    = "handlers/error_processor/error_processor.handler"
  role_arn   = aws_iam_role.lambda_error_processor.arn
  layers     = [data.aws_ssm_parameter.layer_arn_base.value]

  environment_variables = {
    SYSTEM_NAME    = var.system_name
    EVENT_BUS_NAME = aws_cloudwatch_event_bus.slack_error_notifier.name
  }

  s3_bucket_deploy_package = aws_s3_object.lambda_deploy_package.bucket
  s3_key_deploy_package    = aws_s3_object.lambda_deploy_package.key
  source_code_hash         = data.archive_file.lambda_deploy_package.output_base64sha256
  system_name              = var.system_name
  runtime                  = local.lambda.runtime
  region                   = var.region
}

resource "aws_lambda_permission" "error_processor" {
  action        = "lambda:InvokeFunction"
  function_name = module.lambda_error_processor.function_arn
  principal     = "logs.amazonaws.com"
}

# ================================================================
# Lambda Inserter
# ================================================================

module "lambda_inserter" {
  source = "../lambda_function"

  identifier  = "inserter"
  handler     = "handlers/inserter/inserter.handler"
  role_arn    = aws_iam_role.lambda_inserter.arn
  layers      = [data.aws_ssm_parameter.layer_arn_base.value]
  memory_size = 256
  timeout     = 900

  environment_variables = {
    SSM_PARAMETER_NAME_TOKEN_CONTENTFUL   = aws_ssm_parameter.contentful_token.name
    SSM_PARAMETER_NAME_NOTION_DATABASE_ID = aws_ssm_parameter.notion_database_id.name
    SSM_PARAMETER_NAME_NOTION_TOKEN       = aws_ssm_parameter.notion_token.name
    BUCKET_NAME_DATA                      = var.s3_bucket_data
  }

  s3_bucket_deploy_package = aws_s3_object.lambda_deploy_package.bucket
  s3_key_deploy_package    = aws_s3_object.lambda_deploy_package.key
  source_code_hash         = data.archive_file.lambda_deploy_package.output_base64sha256
  system_name              = var.system_name
  runtime                  = local.lambda.runtime
  region                   = var.region

  subscription_destination_lambda_arn = module.lambda_error_processor.function_arn
}
