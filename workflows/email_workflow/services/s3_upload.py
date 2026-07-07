import boto3
import uuid

from django.conf import settings

s3_client = boto3.client(
    "s3",
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
    region_name=settings.AWS_S3_REGION_NAME,
)


def upload_attachment(content: bytes, filename: str, email_execution_id: str):

    extension = filename.split(".")[-1]

    key = f"emails/" f"{email_execution_id}/" f"{uuid.uuid4()}.{extension}"

    s3_client.put_object(
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=key,
        Body=content,
    )

    return key
