from dataclasses import dataclass


@dataclass(frozen=True)
class Product:
    product_id: str
    name: str
    category: str
    price: int
    stock: int