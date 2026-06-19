import uuid

import boto3
from botocore.config import Config

from app.config import settings


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=settings.r2_endpoint,
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=Config(signature_version="s3v4"),
    )


def upload_receipt_image(image_bytes: bytes, content_type: str) -> str:
    """Upload receipt image to R2 and return public URL."""
    ext = content_type.split("/")[-1]
    if ext == "jpeg":
        ext = "jpg"
    key = f"receipts/{uuid.uuid4().hex}.{ext}"

    client = get_s3_client()
    client.put_object(
        Bucket=settings.r2_bucket,
        Key=key,
        Body=image_bytes,
        ContentType=content_type,
    )

    return f"{settings.r2_endpoint}/{settings.r2_bucket}/{key}"
