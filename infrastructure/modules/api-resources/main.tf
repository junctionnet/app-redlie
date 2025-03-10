locals {
  aws_account_id = data.aws_caller_identity.current.account_id
  files_bucket = lower("${var.application}-${var.service}-document-files-${var.env}")
}

module "active_user_sessions" {
  source = "git::https://github.com/terraform-aws-modules/terraform-aws-dynamodb-table.git//"
  name         = "RedlieActiveUserSessions"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "username"

  server_side_encryption_enabled = true
  deletion_protection_enabled    = true
  point_in_time_recovery_enabled = false

  attributes = [
    {
      name = "username"
      type = "S"
    }
  ]
}


resource "aws_iam_role" "lambda_execution_role" {
  depends_on = [module.files_bucket]
  name               = "${var.service}-lambda-execution-role"
  path               = "/"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role_policy.json
}

resource "aws_iam_role_policy" "policy" {
  name   = "${var.service}-lambda-policy"
  role   = aws_iam_role.lambda_execution_role.id
  policy = local.policy
}

module "files_bucket" {
  source                  = "git::https://github.com/terraform-aws-modules/terraform-aws-s3-bucket.git//?ref=v3.6.1"
  bucket                  = local.files_bucket
  block_public_acls       = "true"
  block_public_policy     = "true"
  ignore_public_acls      = "true"
  restrict_public_buckets = "true"
}

module "ssm_params" {
  source = "birkoff/ssm-params/aws"
  parameters = {
    lambda_role = {
      name  = "/${var.service}/lambda_role"
      value = aws_iam_role.lambda_execution_role.arn
    }
    files_s3_bucket = {
      name  = "/${var.service}/files_s3_bucket"
      value = module.files_bucket.s3_bucket_id
    }
    active_user_sessions_table = {
      name  = "/${var.service}/active_user_sessions_table"
      value = module.active_user_sessions.dynamodb_table_id
    }
  }
}

