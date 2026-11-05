import logging

from redis.exceptions import RedisError

from app.modules.products.models.model import Product
from app.core.request_context import mark_cache

from app.modules.products.models.exceptions import (
    ProductNotFoundError,
    CacheSynchronizationError
)


logger = logging.getLogger(__name__)


class ProductService:

    def __init__( self, dynamodb_repository, redis_repository):

        self.dynamodb_repository = dynamodb_repository
        self.redis_repository = redis_repository

    
    def create(self, product: Product) -> Product:

        # 1. Persistir primero en DynamoDB.
        saved_product = self.dynamodb_repository.create(product)

        # 2. Actualizar Redis.
        self._synchronize_cache(saved_product) 

        return saved_product


    

    # READ - CACHE ASIDE
    def find_by_id(self, product_id: str) -> Product:

        try:

            cached_product = self.redis_repository.find_by_id(
                product_id
            )

            if cached_product is not None:
                mark_cache("HIT")
                logger.info(
                    
                    "CACHE HIT: %s",
                    product_id
                )

                return cached_product

            mark_cache("MISS")
            logger.info(
                "CACHE MISS: %s",
                product_id
            )

        except RedisError:
            mark_cache("BYPASS")
            logger.warning(
                "Redis no está disponible. Se consultará DynamoDB.",
                exc_info=True
            )

        product = self.dynamodb_repository.find_by_id(
            product_id
        )

        if product is None:

            raise ProductNotFoundError(product_id)

        # 3. Poblar nuevamente la caché.
        try:

            self.redis_repository.save(product)

        except RedisError:

            logger.warning(
                "No fue posible poblar Redis para %s.",
                product_id,
                exc_info=True
            )

        return product

    # UPDATE - WRITE THROUGH
    def update(self, product: Product) -> Product:

        updated_product = self.dynamodb_repository.update(
            product
        )

        self._synchronize_cache(updated_product)

        return updated_product

    def _synchronize_cache(self, product: Product) -> None:

        try:

            self.redis_repository.save(product)

            logger.info(
                "WRITE THROUGH COMPLETED: %s",
                product.product_id
            )

        except RedisError as exception:

            logger.error(
                "No fue posible sincronizar Redis para %s.",
                product.product_id,
                exc_info=True
            )

            # Intentar eliminar una posible copia anterior.
            try:

                self.redis_repository.delete(
                    product.product_id
                )

            except RedisError:

                logger.error(
                    "Tampoco fue posible invalidar la caché de %s.",
                    product.product_id,
                    exc_info=True
                )

            raise CacheSynchronizationError(
                product.product_id
            ) from exception