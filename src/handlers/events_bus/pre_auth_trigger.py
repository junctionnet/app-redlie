import json
import boto3
import datetime
from src import env_vars
from aws_lambda_powertools import Logger

logger = Logger(service="UserLogin", log_uncaught_exceptions=True, serialize_stacktrace=True)
logger.append_keys(application=env_vars.APPLICATION)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(env_vars.ACTIVE_USER_SESSIONS_TABLE)  # Table to track user sessions

from src.common.Events import EventBridge
event_bridge = EventBridge(
    event_bus_name=env_vars.EVENTS_BUS_NAME,
    client=boto3.client('events_bus', region_name='us-east-1'),
    logger=logger
)


def lambda_handler(event, context):
    print("####################### PRE-AUTH TRIGGER #######################")
    print(event)
    print("################################################################")
    username = event['userName']
    organization = "Redlie" #event['request']['userAttributes']['custom:organization']
    user_pool_id = event['userPoolId']

    # Check for an existing session
    active_session = table.get_item(Key={'username': username})
    if 'Item' in active_session:
        print(f"Active session found for user {username}, revoking first session.")

        # Revoke the previous session
        # revoke_previous_session(username, user_pool_id)

        # Delete the session record from DynamoDB
        delete_session(username)
        event_bridge.username = username
        event_bridge.organization = organization
        event_bridge.publish(
            source="user.auth",
            detail_type="User Logout Global",
            payload={
                'username': username,
                'timestamp': datetime.datetime.utcnow().isoformat(),
            }
        )

    print(f"No active session found or first session revoked for user {username}. Continuing login.")
    return event


def revoke_previous_session(username, user_pool_id):
    client = boto3.client('cognito-idp')
    try:
        client.admin_user_global_sign_out(UserPoolId=user_pool_id, Username=username)
        print(f"User {username} logged out globally.")
    except Exception as e:
        print(f"Error during global sign-out: {e}")
        raise


def delete_session(username):
    try:
        table.delete_item(Key={'username': username})
        print(f"Session for user {username} deleted from DynamoDB.")
    except Exception as e:
        print(f"Error deleting session for user {username}: {e}")
        raise
