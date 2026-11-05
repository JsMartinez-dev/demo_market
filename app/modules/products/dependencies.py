from typing import Annotated

from fastapi import Depends
from botocore.client import BaseClient
from redis import Redis

from app.core.config import Settings, get_settings
from app.core.dynamodb import get_dynamodb_client
from app.core.redis import get_redis_client

from app.modules.products.repositories.dynamodb_repository import (
    DynamoDBProductRepository
)

from app.modules.products.repositories.redis_repository import (
    RedisProductRepository
)

from app.modules.products.services.service import ProductService


def get_product_service(

    dynamodb_client: Annotated[
        BaseClient,
        Depends(get_dynamodb_client)
    ],

    redis_client: Annotated[
        Redis,
        Depends(get_redis_client)
    ],

    settings: Annotated[
        Settings,
        Depends(get_settings)
    ]

) -> ProductService:

    dynamodb_repository = DynamoDBProductRepository(
        dynamodb_client,
        settings.dynamodb_table_name
    )

    redis_repository = RedisProductRepository(
        redis_client,
        settings.cache_ttl_seconds
    )

    return ProductService(
        dynamodb_repository,
        redis_repository
    )