"""{{ cookiecutter.project_name }} data models."""

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = "ok"


class ItemCreate(BaseModel):
    """Schema for creating a new item."""

    name: str = Field(min_length=1, max_length=100, description="Item name")
    description: str = Field(default="", max_length=500, description="Item description")
    price: float = Field(gt=0, description="Item price (must be positive)")


class Item(ItemCreate):
    """Schema for a stored item."""

    id: int = Field(description="Unique item identifier")
