from typing import Optional

from boto3.dynamodb.types import (
    TypeSerializer,
    TypeDeserializer
)

from botocore.client import BaseClient
from botocore.exceptions import ClientError, BotoCoreError

from app.modules.products.models.model import Product
from app.modules.products.models.exceptions import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
    DynamoDBOperationError
)


class DynamoDBProductRepository:

    def __init__(
        self,
        dynamodb_client: BaseClient,
        table_name: str
    ):
        self.dynamodb = dynamodb_client
        self.table_name = table_name

        self.serializer = TypeSerializer()
        self.deserializer = TypeDeserializer()

    # CREATE
    def create(self, product: Product) -> Product:

        item = self._serialize_product(product)

        try:

            self.dynamodb.put_item(
                TableName=self.table_name,
                Item=item,
                ConditionExpression="attribute_not_exists(#pk)",
                ExpressionAttributeNames={
                    "#pk": "productId"
                }
            )

            return product

        except ClientError as exception:

            error_code = exception.response.get(
                "Error", {}
            ).get("Code")

            if error_code == "ConditionalCheckFailedException":
                raise ProductAlreadyExistsError(
                    product.product_id
                ) from exception

            raise DynamoDBOperationError(
                "No fue posible crear el producto en DynamoDB."
            ) from exception

        except BotoCoreError as exception:

            raise DynamoDBOperationError(
                "Error de comunicación con DynamoDB."
            ) from exception

    # READ
    def find_by_id(self,product_id: str) -> Optional[Product]:

        try:

            response = self.dynamodb.get_item(
                TableName=self.table_name,
                Key={
                    "productId": {
                        "S": product_id
                    }
                }
            )

            item = response.get("Item")

            if item is None:
                return None

            return self._deserialize_product(item)

        except (ClientError, BotoCoreError) as exception:

            raise DynamoDBOperationError(
                "No fue posible consultar el producto en DynamoDB."
            ) from exception

    # UPDATE
    def update(self, product: Product) -> Product:

        try:

            response = self.dynamodb.update_item(
                TableName=self.table_name,

                Key={
                    "productId": {
                        "S": product.product_id
                    }
                },

                UpdateExpression=(
                    "SET #name = :name, "
                    "#category = :category, "
                    "#price = :price, "
                    "#stock = :stock"
                ),

                ConditionExpression="attribute_exists(#pk)",

                ExpressionAttributeNames={
                    "#pk": "productId",
                    "#name": "name",
                    "#category": "category",
                    "#price": "price",
                    "#stock": "stock"
                },

                ExpressionAttributeValues={
                    ":name": self.serializer.serialize(product.name),
                    ":category": self.serializer.serialize(product.category),
                    ":price": self.serializer.serialize(product.price),
                    ":stock": self.serializer.serialize(product.stock)
                },

                ReturnValues="ALL_NEW"
            )

            return self._deserialize_product(
                response["Attributes"]
            )

        except ClientError as exception:

            error_code = exception.response.get(
                "Error", {}
            ).get("Code")

            if error_code == "ConditionalCheckFailedException":
                raise ProductNotFoundError(
                    product.product_id
                ) from exception

            raise DynamoDBOperationError(
                "No fue posible actualizar el producto."
            ) from exception

        except BotoCoreError as exception:

            raise DynamoDBOperationError(
                "Error de comunicación con DynamoDB."
            ) from exception

    # SERIALIZATION
    def _serialize_product(self, product: Product) -> dict:

        attributes = {
            "productId": product.product_id,
            "name": product.name,
            "category": product.category,
            "price": product.price,
            "stock": product.stock
        }

        return {
            key: self.serializer.serialize(value)
            for key, value in attributes.items()
        }

    # DESERIALIZATION
    def _deserialize_product(self, item: dict) -> Product:

        attributes = {
            key: self.deserializer.deserialize(value)
            for key, value in item.items()
        }

        return Product(
            product_id=attributes["productId"],
            name=attributes["name"],
            category=attributes["category"],
            price=int(attributes["price"]),
            stock=int(attributes["stock"])
        )