"""Data models for the application.

Data models are used to define the structure of the data that is used in the application. They are used to validate the data that is passed to the application and to serialize the data that is returned by the application.

Pydantic is used to define the data models. Data models attributes are documented using a docstring under the attribute definition.
"""

from pydantic import BaseModel, ConfigDict


class Item(BaseModel):
    """Item model."""

    field: str
    """Docstring for field."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
