const stage = process.env.STAGE || 'dev';
const APP_PARAMS = require('../config.js');

module.exports = {
  muestras: {
    handler: 'src/api/muestras.proxy_handler',
    name: `${APP_PARAMS.FUNCTION_PREFIX}-${stage}-muestras`,
    description: 'User Muestras',
    memorySize: 512,
    timeout: 30,
    events: [
      {
        http: {
          path: '/user/muestras',
          method: 'ANY',
          cors: true,
          integration: 'lambda-proxy',
          // authorizer: {
          //   type: 'COGNITO_USER_POOLS',
          //   arn: APP_PARAMS.USER_POOL_ARN
          // }
        },
      },
      {
        http: {
          path: '/user/muestra',
          method: 'ANY',
          cors: true,
          integration: 'lambda-proxy',
           authorizer: {
             type: 'COGNITO_USER_POOLS',
             arn: APP_PARAMS.USER_POOL_ARN
           }
        },
      },
      {
        http: {
          path: '/muestra',
          method: 'ANY',
          cors: true,
          integration: 'lambda-proxy',
          authorizer: {
            type: 'COGNITO_USER_POOLS',
            arn: APP_PARAMS.USER_POOL_ARN
          }
        },
      },
      {
        http: {
          path: '/muestras',
          method: 'ANY',
          cors: true,
          integration: 'lambda-proxy',
          authorizer: {
            type: 'COGNITO_USER_POOLS',
            arn: APP_PARAMS.USER_POOL_ARN
          }
        },
      },
      {
        http: {
          path: '/muestrassz-estas',
          method: 'ANY',
          cors: true,
          integration: 'lambda-proxy',
          authorizer: {
            type: 'COGNITO_USER_POOLS',
            arn: APP_PARAMS.USER_POOL_ARN
          }
        },
      },
    ],
    package: {
      patterns: [
        'src/**'
      ]
    },
    layers: [
      { Ref: 'BaselayerLambdaLayer' },
      { Ref: 'SqlalchemyLambdaLayer' },
      { Ref: 'PandasfullLambdaLayer' },
    ]
  }
};
