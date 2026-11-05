from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


# Ruta raíz del proyecto
BASE_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # DynamoDB
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_default_region: str = "us-east-1"

    dynamodb_endpoint_url: str = "http://localhost:8000"
    dynamodb_table_name: str = "Products"

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0

    # Cache
    cache_ttl_seconds: int = 300


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()