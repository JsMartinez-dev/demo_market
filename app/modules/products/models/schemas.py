from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):

    product_id: str
    name: str
    price: Decimal = Field(ge=0)
    stock: int = Field(ge=0)


class ProductResponse(BaseModel):

    product_id: str
    name: str
    price: Decimal
    stock: int