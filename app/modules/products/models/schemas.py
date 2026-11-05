from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    product_id: str = Field(
        min_length=3,
        max_length=64,
        pattern=r"^[A-Za-z0-9_-]+$"
    )

    name: str = Field(
        min_length=2,
        max_length=120
    )
    category: str = Field(
        min_length=5,
        max_length=120
    )

    price: int = Field(ge=0)

    stock: int = Field(ge=0)


class ProductUpdate(BaseModel):

    model_config = ConfigDict(
        str_strip_whitespace=True
    )

    name: str = Field(
        min_length=2,
        max_length=120
    )

    category: str = Field(
        min_length=5,
        max_length=120
    )

    price: int = Field(ge=0)

    stock: int = Field(ge=0)


class ProductResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    product_id: str
    name: str
    category: str
    price: int
    stock: int