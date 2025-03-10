import os

import boto3

s3_client = boto3.client('s3', region_name='us-east-1')
bucket_name = os.getenv("S3_BUCKET")


def upload(s3_key, file_content):
    return s3_client.put_object(Bucket=bucket_name, Key=s3_key, Body=file_content)


def download(s3_key, file_path):
    s3_client.download_file(bucket_name=bucket_name, key=s3_key, file_name=file_path)
    return file_path


def get_list():
    object_keys = []
    params = {'Bucket': bucket_name}
    try:
        response = s3_client.list_objects_v2(**params)

        objects = response.get('Contents', [])
        object_keys = [obj['Key'] for obj in objects]
    except Exception as e:
        print(f"Error listing objects: {e}")
    return object_keys
