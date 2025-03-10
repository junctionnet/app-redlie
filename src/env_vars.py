import json
import os

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

LOCAL = bool(True if os.getenv('LOCAL', 0) in ['1', 1, 'true'] else False)

APPLICATION = "Redlie"
DB_CREDENTIALS_SECRET = "/Redlie-IDL/postgresql_db"
if LOCAL is True:
    from dotenv import load_dotenv
    load_dotenv()
    # from src.common.repositories.aws_secrets_manager import get_secret
    # DB_CREDENTIALS = get_secret('/Redlie-IDL/postgresql_db')
# else:
    # DB_CREDENTIALS = os.getenv('DB_CREDENTIALS')

# DB = json.loads(DB_CREDENTIALS)

# RDS_PROXY_CREDENTIALS = os.getenv('RDS_PROXY_CREDENTIALS', None)
# if RDS_PROXY_CREDENTIALS:
#     RDS_PROXY_CREDENTIALS = json.loads(RDS_PROXY_CREDENTIALS)

PLATFORM_USER_GROUPS = {
    'PLATFORM_ADMIN': os.getenv('PLATFORM_ADMIN', 'PlatformAdmin'),
    'ORGANIZATION_ADMIN': os.getenv('MEMBER', 'OrganizationAdmin'),
    'JNET_ADMIN': os.getenv('MEMBER', 'JunctionNetAdmin'),
    'MEMBER': os.getenv('MEMBER', 'Member'),
    'CUSTOMER': os.getenv('MEMBER', 'Customer'),
    'SELLER': os.getenv('MEMBER', 'Seller'),
    'ISSUER': os.getenv('MEMBER', 'Issuer'),
}

LAMBDA_LOCAL_DIR = os.getenv('LAMBDA_LOCAL_DIR', '/tmp')
LOG_LEVEL = os.getenv('POWERTOOLS_LOG_LEVEL', 'INFO')
LOG_EVENT = os.getenv('LOG_EVENT', 0) == '1'

REDLIE_INDICES_RESULTADOS_TABLE = "RedlieResultadosIndices"
ACTIVE_USER_SESSIONS_TABLE = os.getenv('ACTIVE_USER_SESSIONS_TABLE', 'RedlieActiveUserSessions')
S3_BUCKET = os.getenv('S3_BUCKET', 'redlie-redlie-idl-document-files-dev')
COGNITO_USER_POOL=os.getenv('COGNITO_USER_POOL', 'us-east-1_g56cKTbnT')
USER_POOL_ID = os.environ.get('USER_POOL_ID', 'us-east-1_g56cKTbnT')
STAGE = os.environ.get('STAGE', 'dev')
ENV = STAGE

if STAGE == 'production':
    IS_PRODUCTION = True
else:
    IS_PRODUCTION = False

CORS_ALLOW_ORIGIN = os.getenv('CORS_ALLOW_ORIGIN', '*')
EVENTS_BUS_NAME = os.environ.get('EVENTS_BUS', 'Redlie-events_bus')
LOG_DB_TRANSACTIONS = False  # os.getenv('LOG_DB_TRANSACTIONS', 1)

FACTORIES_MAP = {
    "Muestras": "src.factories.MuestrasServiceFactory",
}

ELASTICSEARCH_HOST = os.getenv('ELASTICSEARCH_HOST')
ELASTICSEARCH_API_TOKEN = os.getenv('ELASTICSEARCH_API_TOKEN')
ELASTICSEARCH_INDEX = os.getenv('ELASTICSEARCH_INDEX')


PLATFORM_ADMIN = os.getenv('PLATFORM_ADMIN', 'JunctionNet')
ORGANIZATION_ADMIN = os.getenv('ORGANIZATION_ADMIN', 'OrganizationAdmin')
MEMBER = os.getenv('MEMBER', 'Member')
BRANCH = os.getenv('BRANCH', 'Branch')
COMPANY = os.getenv('COMPANY', 'Company')
ISSUER = os.getenv('ISSUER', 'Issuer')
USER_POOL_ID = os.getenv("USER_POOL_ID", "us-east-1_g56cKTbnT")
STAGE = os.environ.get('STAGE', 'dev')
ENV = os.environ.get('STAGE', 'dev')