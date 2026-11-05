from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.modules.products.dependencies import get_product_service

from app.modules.products.models.model import Product

from app.modules.products.models.schemas import (
    ProductCreate,
    ProductUpdate,
    ProductResponse
)

from app.modules.products.services.service import ProductService


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post(
    "",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED
)
def create_product(request: ProductCreate,service: Annotated[ProductService,Depends(get_product_service)]):

    product = Product(
        product_id=request.product_id,
        name=request.name,
        category=request.category,
        price=request.price,
        stock=request.stock
    )

    saved_product = service.create(product)

    return ProductResponse.model_validate(saved_product) #Mapeamos el producto 


# READ
@router.get("/{product_id}",response_model=ProductResponse)
def find_product(product_id: str,service: Annotated[ProductService,Depends(get_product_service)]):

    product = service.find_by_id(product_id)

    return ProductResponse.model_validate(product)



# UPDATE
@router.put(
    "/{product_id}",
    response_model=ProductResponse
)
def update_product(

    product_id: str,

    request: ProductUpdate,

    service: Annotated[
        ProductService,
        Depends(get_product_service)
    ]

):

    product = Product(
        product_id=product_id,
        name=request.name,
        category=request.category,
        price=request.price,
        stock=request.stock
    )

    updated_product = service.update(product)

    return ProductResponse.model_validate(updated_product)