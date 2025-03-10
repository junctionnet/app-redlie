const stage = process.env.STAGE || 'dev';
const APP_PARAMS = require('./config.js');

// Define the resources
module.exports = {
    Resources: {
      AppServiceApiGateway: {
        Type: 'AWS::ApiGateway::RestApi',
        Properties: {
          Name: APP_PARAMS.API_GATEWAY_NAME,
          Description: `API Gateway for Admin Service for ${stage} environment`,
          EndpointConfiguration: {
            Types: ['REGIONAL']
          },
          BinaryMediaTypes: [
            'application/pdf',
            'application/xml',
            'text/xml',
            'application/zip',
            'application/x-zip-compressed',
            'application/octet-stream',
            'multipart/x-zip',
            'application/x-compressed',
            'application/x-zip',
            'application/x-gzip',
            'application/x-tar',
            'application/x-gtar',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'application/vnd.ms-excel',
            '*/*',
          ],
        },
      },
    },
    Outputs: {
      SqlalchemyExport: {
        Value: { Ref: 'SqlalchemyLambdaLayer' },
        Export: {
          Name: `SqlalchemyLambdaLayer-${APP_PARAMS.SERVICE}-${stage}`,
        },
      },

      BaselayerExport: {
        Value: { Ref: 'BaselayerLambdaLayer' },
        Export: {
          Name: `BaselayerLambdaLayer-${APP_PARAMS.SERVICE}-${stage}`,
        },
      },

  },
};
