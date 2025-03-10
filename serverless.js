const stage = process.env.STAGE || 'dev';
const region = process.env.REGION || 'us-east-1';
const isAwsDevEnv = stage === 'dev';
const localEnv = process.env.LOCAL || process.env.IS_OFFLINE;
const runningLocal = localEnv === '1' || localEnv?.toLowerCase() === 'true';

const plugins = [
  'serverless-domain-manager',
  'serverless-offline'
];

if (isAwsDevEnv && runningLocal) {
  plugins.push('serverless-dotenv-plugin');
}

const APP_LOGS = {
    DEBUG: 0,
    LOG_EVENT: 1,
    LOG_DB_TRANSACTIONS: 0,
    AWS_LAMBDA_LOG_LEVEL: 'INFO',
    POWERTOOLS_LOG_LEVEL: 'INFO'
}

let API_SUBDOMAIN = 'api';
if (!['dev', 'production'].includes(stage)) {
     API_SUBDOMAIN = stage + '-api';
}


const SO = { httpPort: 4000 };

const APP_PARAMS = require('./infrastructure/serverless/config.js');
const DOMAIN_NAME = API_SUBDOMAIN + '.' + APP_PARAMS['HOSTED_ZONE_NAME'];
console.log('DOMAIN_NAME', DOMAIN_NAME);
const CORS= "https://" + API_SUBDOMAIN + '.' + APP_PARAMS['HOSTED_ZONE_NAME'] + ',https://open.' + stage + '.' + APP_PARAMS['HOSTED_ZONE_NAME'] + ',https://' + stage + '.' + APP_PARAMS['HOSTED_ZONE_NAME'];

const customDomain = {
    domainName: DOMAIN_NAME,
    certificateArn: APP_PARAMS['CERTIFICATE_ARN'],
    hostedZoneId: APP_PARAMS['HOSTED_ZONE_ID'],
    route53Region: 'us-east-1',
    securityPolicy: 'tls_1_2',
    autoDomain: true,
    autoDomainWaitFor: 120,
    endpointType: 'regional',
    stage: stage,
    createRoute53Record: true,
};

const serverlessOffline = {
    httpPort: "4000",
    websocketPort: "4001",
    lambdaPort: "4003",
    host: "localhost",
    port: "4000",
}

const custom = {
    LOGISTICSHUB: APP_PARAMS['LOGISTICSHUB'],
    S3_BUCKET: APP_PARAMS['S3_BUCKET'],
    IS_dev: stage === 'dev',
    SERVICE: APP_PARAMS['SERVICE'],
    APPLICATION: APP_PARAMS['APPLICATION'],
    API_SUBDOMAIN: API_SUBDOMAIN,
    DOMAIN_NAME: DOMAIN_NAME,
    API_GATEWAY_NAME: APP_PARAMS['API_GATEWAY_NAME'],
    EMAIL_SENDER: APP_PARAMS['EMAIL_SENDER'],
    PLATFORM_COGNITO_USER_POOL_ARN: APP_PARAMS['PLATFORM_COGNITO_USER_POOL_ARN'],
    USER_POOL_ARN: APP_PARAMS['USER_POOL_ARN'],
    VPC_SUBNETS: APP_PARAMS['VPC_SUBNETS'],
    VPC_SECURITY_GROUP: APP_PARAMS['VPC_SECURITY_GROUP'],
    EVENTS_BUS: APP_PARAMS['EVENTS_BUS'],
    LAMBDA_ROLE: APP_PARAMS['LAMBDA_ROLE'],
    DB_CREDENTIALS: APP_PARAMS['DB_CREDENTIALS'],
//    RDS_PROXY_CREDENTIALS: APP_PARAMS['RDS_PROXY_CREDENTIALS'],
    CORS: CORS,
    DEBUG: APP_LOGS['DEBUG'],
    LOG_EVENT: APP_LOGS['LOG_EVENT'],
    LOG_DB_TRANSACTIONS: APP_LOGS['LOG_DB_TRANSACTIONS'],
    AWS_LAMBDA_LOG_LEVEL: APP_LOGS['AWS_LAMBDA_LOG_LEVEL'],
    POWERTOOLS_LOG_LEVEL: APP_LOGS['POWERTOOLS_LOG_LEVEL'],
    ACTIVE_USER_SESSIONS_TABLE: APP_PARAMS['ACTIVE_USER_SESSIONS_TABLE'],
    serverlessOffline: serverlessOffline,
    httpPort: "4000",
    websocketPort: "4001",
    lambdaPort: "4003",
    host: "localhost",
    port: "4000",
    customDomain: customDomain,
};

const ENVIRONMENT_VARIABLES = {
    STAGE: stage,
    APPLICATION: '${self:custom.APPLICATION}',
    SERVICE: '${self:custom.SERVICE}',
    DEBUG: '${self:custom.DEBUG}',
    LOG_EVENT: '${self:custom.LOG_EVENT}',
    LOG_DB_TRANSACTIONS: '${self:custom.LOG_DB_TRANSACTIONS}',
    AWS_LAMBDA_LOG_LEVEL: '${self:custom.AWS_LAMBDA_LOG_LEVEL}',
    POWERTOOLS_LOG_LEVEL: '${self:custom.POWERTOOLS_LOG_LEVEL}',
    S3_BUCKET: '${self:custom.S3_BUCKET}',
    EMAIL_SENDER: '${self:custom.EMAIL_SENDER}',
    AWS_REGION_NAME: region,
    EVENTS_BUS: '${self:custom.EVENTS_BUS}',
    DB_CREDENTIALS: '${self:custom.DB_CREDENTIALS}',
//    RDS_PROXY_CREDENTIALS: '${self:custom.RDS_PROXY_CREDENTIALS}',
    ACTIVE_USER_SESSIONS_TABLE: '${self:custom.ACTIVE_USER_SESSIONS_TABLE}',
    CORS: '${self:custom.CORS}',
    USER_POOL_ARN: '${self:custom.USER_POOL_ARN}',
    PLATFORM_COGNITO_USER_POOL_ARN: '${self:custom.PLATFORM_COGNITO_USER_POOL_ARN}',
    API_GW_NAME: '${self:custom.API_GATEWAY_NAME}',
};

const provider = {
  ...require('./infrastructure/serverless/provider.js'),
  apiGateway: {
    restApiId: { Ref: 'AppServiceApiGateway' },
    restApiRootResourceId: { 'Fn::GetAtt': ['AppServiceApiGateway', 'RootResourceId'] },
  },
  environment: ENVIRONMENT_VARIABLES,
};

const functions = {
  ...require('./infrastructure/serverless/lambda_functions/platform.js'),
  ...require('./infrastructure/serverless/lambda_functions/muestras.js'),
  ...require('./infrastructure/serverless/lambda_functions/redlie-events.js'),
};

const resources = require('./infrastructure/serverless/resources.js');
const layers = require('./infrastructure/serverless/layers.js');

module.exports = {
  service: APP_PARAMS.APPLICATION,
  plugins: plugins,
  package: {
    individually: true,
    patterns: [
      "!**",
      "src/**"
    ]
  },
  custom: custom,
  provider: provider,
  functions: functions,
  layers: layers,
  resources: resources
};
