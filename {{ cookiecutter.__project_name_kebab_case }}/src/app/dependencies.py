"""Build dependencies for the application."""

from {{ cookiecutter.__project_name_snake_case }}.services import Service
from .config import config


def get_service() -> Service:
    """Get the service."""
    return Service(config.some_config)
