import boto3
from botocore.exceptions import NoCredentialsError


class S3Repository:
    def __init__(self, s3_bucket: str):
        self.s3_bucket = s3_bucket
        self.s3 = boto3.client('s3',region_name='us-east-1')

    def upload(self, s3_key, file_content):
        try:
            self.s3.put_object(Bucket=self.s3_bucket, Key=s3_key, Body=file_content)
        except Exception as e:
            raise Exception("File content couldn't be parsed")
        return {"file_name": file_content, "message": "File uploaded successfully"}

    def download(self, file_path, file_name):
        self.s3.download_file(self.s3, file_name, file_path)
        return file_path

    def generate_presigned_url(self,s3_key, expiry_duration: int = 3600 * 2):

        try:
            url = self.s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': self.s3_bucket,
                    'Key': s3_key,
                },
                ExpiresIn=expiry_duration,
                HttpMethod='GET'
            )
            return url
        except NoCredentialsError:
            print("Credentials not available.")
            return None
        except Exception as e:
            print(f"Error generating presigned URL: {e}")
            return None