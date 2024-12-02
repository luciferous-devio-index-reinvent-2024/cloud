output "function_name" {
  value = aws_lambda_function.function.function_name
}

output "function_arn" {
  value = aws_lambda_function.function.arn
}

output "function_alias_name" {
  value = aws_lambda_alias.function.name
}

output "function_alias_arn" {
  value = aws_lambda_alias.function.arn
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.function.name
}

output "log_group_arn" {
  value = aws_cloudwatch_log_group.function.arn
}
