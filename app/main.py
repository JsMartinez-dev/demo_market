import logging
import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.modules.products.controller.controller import router as product_router
from app.core.request_context import start_request_tracking

from app.modules.products.models.exceptions import (
    ProductAlreadyExistsError,
    ProductNotFoundError,
    DynamoDBOperationError,
    CacheSynchronizationError
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("market")


app = FastAPI(
    title="Market-Redis",
    description="API REST que demuestra Write-through Cache con DynamoDB y Redis en un supermercado.",
    version="1.0.0"
)


@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    tracking = start_request_tracking()

    response = await call_next(request)

    ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{ms:.2f}"
    response.headers["X-Cache"] = tracking["cache"]

    logger.info(
        "%s %s -> %s en %.2f ms [cache=%s]",
        request.method, request.url.path, response.status_code, ms, tracking["cache"]
    )
    return response

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Cache", "X-Process-Time-Ms"],
)


app.include_router(
    product_router,
    prefix="/api"
)


# PRODUCT ALREADY EXISTS
@app.exception_handler(ProductAlreadyExistsError)
async def product_already_exists_handler(
    request: Request,
    exception: ProductAlreadyExistsError
):
    return JSONResponse(
        status_code=409,
        content={
            "detail": f"El producto {exception} ya existe."
        }
    )


# PRODUCT NOT FOUND
@app.exception_handler(ProductNotFoundError)
async def product_not_found_handler(
    request: Request,
    exception: ProductNotFoundError
):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exception),
            "message": "El producto no se encuentra registrado"
        }
    )


# DYNAMODB ERROR
@app.exception_handler(DynamoDBOperationError)
async def dynamodb_error_handler(
    request: Request,
    exception: DynamoDBOperationError
):
    logging.getLogger(__name__).error(
        "Error de DynamoDB",
        exc_info=exception
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exception)
        }
    )


# CACHE SYNCHRONIZATION ERROR
@app.exception_handler(CacheSynchronizationError)
async def cache_sync_error_handler(
    request: Request,
    exception: CacheSynchronizationError
):
    logging.getLogger(__name__).error(
        "Error sincronizando Redis",
        exc_info=exception
    )
    return JSONResponse(
        status_code=503,
        content={
            "detail": str(exception),
            "product_id": exception.product_id,
            "persisted_in_dynamodb": True,
            "cache_synchronized": False
        }
    )


@app.get("/", tags=["General"])
def root():
    return {
        "message": "Welcome to Write-through Cache API",
        "documentation": "/docs"
    }


@app.get("/health", tags=["Health"])
def health_check():
    return {
        "status": "ok",
        "application": "write-through-cache"
    }