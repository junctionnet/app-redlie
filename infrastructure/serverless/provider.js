subnetIds = '${ssm:/platform/subnet_ids}'.split(',');
module.exports = {
  stage: process.env.STAGE || 'dev',
  region: process.env.REGION || 'us-east-1',
  runtime: 'python3.10',
  name: 'aws',
  tracing: {
    lambda: true,
  },
  logRetentionInDays: 30,
  vpc: {
    securityGroupIds: ['${ssm:/platform/security_group_id}'],
    subnetIds: '${ssm:/platform/subnet_ids}',
  },
  iam: {
    role: '${self:custom.LAMBDA_ROLE}',
  },
};
