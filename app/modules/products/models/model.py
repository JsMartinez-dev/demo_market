from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Product:

    product_id: str
    name: str
    price: Decimal
    stock: int