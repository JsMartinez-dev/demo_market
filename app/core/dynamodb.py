from functools import lru_cache

import boto3
from botocore.client import BaseClient
from botocore.config import Config as BotoConfig

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_dynamodb_client() -> BaseClient:

    settings = get_settings()

    dynamodb_client = boto3.client(
        "dynamodb",

        endpoint_url=settings.dynamodb_endpoint_url,

        region_name=settings.aws_default_region,

        aws_access_key_id=settings.aws_access_key_id,

        aws_secret_access_key=settings.aws_secret_access_key,

        config=BotoConfig(
            connect_timeout=3,
            read_timeout=5,
            retries={
                "max_attempts": 3,
                "mode": "standard"
            }
        )
    )

    return dynamodb_client