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


# def revoke_previous_session(username, user_pool_id):
#     client = boto3.client('cognito-idp')
#     client.admin_user_global_sign_out(
#         UserPoolId=user_pool_id,
#         Username=username,
#     )


def lambda_handler(event, context):
    print("####################### POST-AUTH TRIGGER #######################")
    print(event)
    username = event['userName']
    organization = "Redlie"
    # organization = event['request']['userAttributes']['custom:organization']
    user_pool_id = event['userPoolId']
    current_time = datetime.datetime.utcnow().isoformat()

    active_session = table.get_item(Key={'username': username})
    print(json.dumps(active_session, indent=2))

    if active_session:
        print("Active session found for user:", username)

    else:
        active_session = {}
        print("No active session for user:", username)
    # Check active session

    # Store new session
    new_session = {
        'timestamp': current_time,
        'username': username,
        'organization': organization,
        'application': 'Admin',
        'token': event['request']['userAttributes']['sub'],  # Use Cognito User ID
    }
    table.put_item(Item=new_session)

    event_bridge.organization = organization
    event_bridge.username = username
    event_bridge.publish(
        source="user.auth",
        detail_type="User Login",
        payload={
            "username": username,
            "organization": organization,
            "timestamp": current_time,
            "user_pool_id": user_pool_id,
            "active_session": new_session['token'],
            "prev_session": active_session.get('Item', {}),
        }
    )
    print("################################################################")
    return event
