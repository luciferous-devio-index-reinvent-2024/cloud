# ================================================================
# Lambda Artifacts Bucket
# ================================================================

resource "aws_s3_bucket" "lambda_artifacts" {
  bucket_prefix = "lambda-artifacts-"
}