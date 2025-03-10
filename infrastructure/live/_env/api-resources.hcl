locals {
  env_vars = read_terragrunt_config(find_in_parent_folders("terragrunt.hcl"))
  env      = local.env_vars.locals.env
  application = local.env_vars.locals.application
  service = local.env_vars.locals.service
  component = local.env_vars.locals.component
  region = local.env_vars.locals.region
}

terraform {
  source = "../../..//modules/api-resources"
}

inputs = {
  lambda_role_name_prefix = "${local.service}"
  lambda_role_path        = "/${local.application}/"
  eventbridge_bus_name    = "${local.service}-events"
  application             = local.application
  service                 = local.service
  region                  = local.region
  env                     = local.env
}