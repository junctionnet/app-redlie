const stage = process.env.STAGE || 'dev';
const APP_PARAMS = require('../config.js');

module.exports = {
 muestrasEvents: {
   handler: 'src/events/redlie.lambda_handler',
   name: `${APP_PARAMS.FUNCTION_PREFIX}-${stage}-muestras-events`,
   description: `[Events]  [${stage}]`,
   memorySize: 512,
   timeout: 500,
   maximumRetryAttempts: 0,
   
   events: [
     {
       eventBridge: {
         eventBus: APP_PARAMS.EVENTS_BUS,
         pattern: {
           source: [
            'redlie.idl.process'
          ]

         }
       }
     }
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
 },
};
