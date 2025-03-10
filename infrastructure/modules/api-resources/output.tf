output "role_name" {
  value = aws_iam_role.lambda_execution_role.name
}

output "role_arn" {
  value = aws_iam_role.lambda_execution_role.arn
}

output "parameter_names" {
  value = module.ssm_params.parameter_names
}

output "parameter_values" {
  value = module.ssm_params.parameter_values
  sensitive = true
}