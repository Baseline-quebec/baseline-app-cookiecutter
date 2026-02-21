"""{{ cookiecutter.project_name }} REST API."""

import sys
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from loguru import logger
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from {{ cookiecutter.__project_name_snake_case }}.models import HealthResponse, Item, ItemCreate
from {{ cookiecutter.__project_name_snake_case }}.services import ItemService
from {{ cookiecutter.__project_name_snake_case }}.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:  # noqa: ARG001
    """Handle FastAPI startup and shutdown events."""
    logger.remove()
    logger.add(sys.stderr, level=settings.log_level)
{%- if cookiecutter.with_sentry|int %}

    if settings.sentry_dsn:
        import sentry_sdk  # noqa: PLC0415

        sentry_sdk.init(
            dsn=settings.sentry_dsn,
            environment=settings.sentry_environment,
            traces_sample_rate=settings.sentry_traces_sample_rate,
        )
        logger.info("Sentry initialized for environment '{}'", settings.sentry_environment)
{%- endif %}

    yield


app = FastAPI(title=settings.app_name, lifespan=lifespan)


# --- Dependency injection --------------------------------------------------------


def get_item_service() -> ItemService:
    """Provide the shared ItemService instance."""
    return _item_service


_item_service = ItemService()

ItemServiceDep = Annotated[ItemService, Depends(get_item_service)]


# --- Middleware ------------------------------------------------------------------


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log method, path, status code, and duration for every request."""

    async def dispatch(self, request: Request, call_next: ...) -> Response:  # type: ignore[override]
        """Process request and log timing information."""
        start = time.perf_counter()
        response: Response = await call_next(request)
        duration_ms = (time.perf_counter() - start) * 1000
        logger.info(
            "{method} {path} {status} {duration:.1f}ms",
            method=request.method,
            path=request.url.path,
            status=response.status_code,
            duration=duration_ms,
        )
        return response


app.add_middleware(RequestLoggingMiddleware)


# --- Exception handlers ----------------------------------------------------------


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:  # noqa: ARG001
    """Return a structured JSON response for HTTP exceptions."""
    logger.warning("HTTP {status}: {detail}", status=exc.status_code, detail=exc.detail)
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    """Return a 500 JSON response for unhandled exceptions."""
    logger.exception("Unhandled exception: {exc}", exc=exc)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# --- Routes ----------------------------------------------------------------------


@app.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse()


@app.post("/items", response_model=Item, status_code=201)
async def create_item(data: ItemCreate, service: ItemServiceDep) -> Item:
    """Create a new item."""
    return service.create(data)


@app.get("/items", response_model=list[Item])
async def list_items(service: ItemServiceDep) -> list[Item]:
    """List all items."""
    return service.list_all()


@app.get("/items/{item_id}", response_model=Item)
async def get_item(item_id: int, service: ItemServiceDep) -> Item:
    """Get a single item by id."""
    item = service.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return item


if __name__ == "__main__":
    import uvicorn  # noqa: PLC0415

    uvicorn.run(app, host=settings.api_host, port=settings.api_port, log_level="info")
