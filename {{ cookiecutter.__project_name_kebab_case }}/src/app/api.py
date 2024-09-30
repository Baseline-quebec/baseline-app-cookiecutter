"""{{ cookiecutter.project_name }} REST API."""

import logging
from contextlib import asynccontextmanager
from collections.abc import AsyncIterator

import coloredlogs
from fastapi import FastAPI, Depends

from {{ cookiecutter.__project_name_snake_case }}.dependencies import get_service


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:  # noqa: ARG001
    """Handle FastAPI startup and shutdown events."""
    # Startup events:
    # - Remove all handlers associated with the root logger object.
    for handler in logging.root.handlers:
        logging.root.removeHandler(handler)
    # Add coloredlogs' coloured StreamHandler to the root logger.
    # - Add coloredlogs' colored StreamHandler to the root logger.
    coloredlogs.install()

    # Call dependencies' setup functions here

    yield

    # Call dependencies' teardown functions here


app = FastAPI(lifespan=lifespan)


@app.get("/my-endpoint")
async def my_endpoint(service: Depends[get_service]) -> None:
    """Handle my endpoint."""
    service.my_endpoint_handler()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000, log_level="info")
