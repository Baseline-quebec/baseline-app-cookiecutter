"""Config file for the app."""

from collections.abc import ClassVar

from pydantic import BaseModel, ConfigDict


class config(BaseModel):
    """Configuration for the app."""

    some_config: ClassVar[int] = 42
    """Docstring for some_config."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
