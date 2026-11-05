from functools import lru_cache

import redis
from redis import Redis

from app.core.config import get_settings


@lru_cache(maxsize=1)
def get_redis_client() -> Redis:

    settings = get_settings()

    redis_client = redis.Redis(
        host=settings.redis_host,

        port=settings.redis_port,

        db=settings.redis_db,

        decode_responses=True, #para que no nos mande el result como byte

        socket_connect_timeout=3,

        socket_timeout=5,

        health_check_interval=30
    )

    return redis_client