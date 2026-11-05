from app.core.config import get_settings
from app.core.dynamodb import get_dynamodb_client


def create_products_table():

    settings = get_settings()
    dynamodb = get_dynamodb_client()

    table_name = settings.dynamodb_table_name

    try:

        response = dynamodb.create_table(

            TableName=table_name,

            AttributeDefinitions=[
                {
                    "AttributeName": "productId",
                    "AttributeType": "S"
                }
            ],

            KeySchema=[
                {
                    "AttributeName": "productId",
                    "KeyType": "HASH"
                }
            ],

            ProvisionedThroughput={
                "ReadCapacityUnits": 5,
                "WriteCapacityUnits": 5
            }

        )

        print(f"Creando tabla: {table_name}")
        print(
            "Estado:",
            response["TableDescription"]["TableStatus"]
        )

    except dynamodb.exceptions.ResourceInUseException:

        print(f"La tabla {table_name} ya existe.")

        return

    # Esperar hasta que la tabla esté disponible.
    waiter = dynamodb.get_waiter("table_exists")

    waiter.wait(
        TableName=table_name,
        WaiterConfig={
            "Delay": 1,
            "MaxAttempts": 10
        }
    )

    print(f"Tabla {table_name} creada correctamente.")


if __name__ == "__main__":
    create_products_table()