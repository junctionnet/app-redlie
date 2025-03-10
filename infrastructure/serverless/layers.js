module.exports = {
    baselayer: {
        name: `BaseLayer-${process.env.STAGE || 'dev'}-entrywriter`,
        package: {
          artifact: 'infrastructure/layers/base-layer.zip',
        },
        description: 'aws-lambda-powertools==2.14.1 pynamodb==5.4.1 pytz aws-xray-sdk==2.13.0 sentry-sdk==1.34.0 PyPDF2==3.0.1 requests',
        compatibleRuntimes: [
          'python3.10',
          'python3.8',
        ],
        retain: false,
      },
      sqlalchemy: {
        name: `Sqlalchemy-${process.env.STAGE || 'dev'}-entrywriter`,
        package: {
          artifact: 'infrastructure/layers/sqlalchemy-package.zip',
        },
        description: 'sqlalchemy==2.0.20 psycopg2-binary==2.9.7 alembic==1.12.1 sqlalchemy_continuum==1.4.2',
        compatibleRuntimes: [
          'python3.8',
          'python3.10',
        ],
        retain: false,
      },
      pandas: {
        name: `Pandas-${process.env.STAGE || 'dev'}-entrywriter`,
        package: {
          artifact: 'infrastructure/layers/pandas-standalone.zip',
        },
        description: 'pandas==2.0.3 wand',
        compatibleRuntimes: [
          'python3.10',
          'python3.8',
        ],
        retain: false,
      },
      pandasfull: {
        name: `Pandas-Full-${process.env.STAGE || 'dev'}-entrywriter`,
        package: {
          artifact: 'infrastructure/layers/pandas-full.zip',
        },
        description: 'pandas==2.0.3 openpyxl==3.1.2 numpy==1.26.4',
        compatibleRuntimes: [
          'python3.10',
          'python3.8',
        ],
        retain: false,
      },

};
