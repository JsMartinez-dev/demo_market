import json

from dataclasses import asdict
from typing import Optional

from redis import Redis

from app.modules.products.models.model import Product


class RedisProductRepository:

    def __init__(
        self,
        redis_client: Redis,
        ttl_seconds: int
    ):

        self.redis = redis_client
        self.ttl_seconds = ttl_seconds

    # READ CACHE
    def find_by_id(
        self,
        product_id: str
    ) -> Optional[Product]:

        key = self._build_key(product_id)

        cached_data = self.redis.get(key)

        if cached_data is None:
            return None

        try:

            attributes = json.loads(cached_data)

            product = Product(**attributes)

            if product.product_id != product_id:
                self.redis.delete(key)
                return None

            return product

        except (json.JSONDecodeError, TypeError, KeyError):

            # La información almacenada no es válida.
            self.redis.delete(key)

            return None

    # SAVE CACHE
    def save(self, product: Product) -> None:

        key = self._build_key(product.product_id)

        product_json = json.dumps(
            asdict(product),
            ensure_ascii=False
        )

        self.redis.set(
            key,
            product_json,
            ex=self.ttl_seconds
        )

    # DELETE CACHE
    def delete(self, product_id: str) -> None:

        key = self._build_key(product_id)

        self.redis.delete(key)

    # BUILD KEY
    def _build_key(self, product_id: str) -> str:

        return f"product:{product_id}"