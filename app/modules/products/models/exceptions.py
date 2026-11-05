class ProductAlreadyExistsError(Exception):
    """El producto que se intenta crear ya existe."""


class ProductNotFoundError(Exception):
    """El producto solicitado no existe."""


class DynamoDBOperationError(Exception):
    """Error al ejecutar una operación en DynamoDB."""


class CacheSynchronizationError(Exception):
    """DynamoDB confirmó la escritura, pero Redis no se sincronizó."""

    def __init__(self, product_id: str):
        self.product_id = product_id

        super().__init__(
            f"El producto {product_id} se persistió en DynamoDB, "
            "pero no se pudo sincronizar Redis."
        )