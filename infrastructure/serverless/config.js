const stage = process.env.STAGE || 'dev';

module.exports = {
    APPLICATION: 'Redlie',
    SERVICE: 'Redlie-IDL',
    FUNCTION_PREFIX: 'RedlieIDL',
    API_GATEWAY_NAME: `Redlie-${stage}`,
    CERTIFICATE_ARN:  '${ssm:/Redlie-IDL/acm_certificate_arn}',
    HOSTED_ZONE_ID:  '${ssm:/Redlie-IDL/hosted_zone_id}',
    HOSTED_ZONE_NAME: '${ssm:/Redlie-IDL/hosted_zone_name}',
    EMAIL_SENDER: "noreply@junctionnet.ai",
    EVENTS_BUS: 'Redlie-events-'+`${stage}`,
    USER_POOL_ARN: '${ssm:/platform/cognito_userpool_arn}',
    PLATFORM_COGNITO_USER_POOL_ARN: '${ssm:/RedlieIDL/cognito_userpool_arn}',
    VPC_SUBNETS: '${ssm:/platform/subnet_ids}',
    VPC_SECURITY_GROUP: '${ssm:/platform/security_group_id}',
    LAMBDA_ROLE: '${ssm:/Redlie-IDL/lambda_role}',
    S3_BUCKET: '${ssm:/Redlie-IDL/files_s3_bucket}',
    DB_CREDENTIALS: '${ssm(raw):/aws/reference/secretsmanager//Redlie-IDL/postgresql_db}',
//    RDS_PROXY_CREDENTIALS: '${ssm(raw):/aws/reference/secretsmanager//platform/rds_proxy_postgresql}',
	ACTIVE_USER_SESSIONS_TABLE: '${ssm:/Redlie-IDL/active_user_sessions_table}',
};
