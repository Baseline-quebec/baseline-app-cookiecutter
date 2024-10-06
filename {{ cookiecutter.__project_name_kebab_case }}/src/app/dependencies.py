# ruff: noqa: DOC201
"""Build dependencies for the application."""

from src.persistance.vectorstore import WeaviateVectorstore
from {{ cookiecutter.__project_name_snake_case }}.service import Service

from .config import config  # noqa: TID252


def get_vectorstore() -> WeaviateVectorstore:
    """Get the vectorstore."""
    client = ...
    return WeaviateVectorstore(client=client)


def get_service() -> Service:
    """Get the service."""
    return Service(config.some_config)
