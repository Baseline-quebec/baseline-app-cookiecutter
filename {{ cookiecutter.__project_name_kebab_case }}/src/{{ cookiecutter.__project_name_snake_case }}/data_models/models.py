"""Data models for the application."""

from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    """Item model."""

    field: str
    """Docstring for field."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
