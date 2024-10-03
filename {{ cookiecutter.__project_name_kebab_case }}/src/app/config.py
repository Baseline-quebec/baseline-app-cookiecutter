"""Config file for the app.

The config class is a pydantic model that defines the configuration for the app. The config should be used as a singleton and all values should be accessed as class attributes. Add a docstring under each attribute to describe its purpose.

The config stores constants or common values used to initialize a "specific" version of the app. The config should not be used to store values that are used across the app; these should go in a dedicated `constants.py` file alongside the service file.
"""

from typing import ClassVar

from pydantic import BaseModel, ConfigDict


class config(BaseModel):  # noqa: N801
    """Configuration for the app."""

    some_config: ClassVar[int] = 42
    """Docstring for some_config."""

    model_config = ConfigDict(extra="forbid", use_attribute_docstrings=True)
