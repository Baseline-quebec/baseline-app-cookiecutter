"""Service class for {{ cookiecutter.__project_name_kebab_case }}.

The service defines the main entry points for the application. It is responsible for handling the business logic of the application.
"""


class Service:
    """Service class for {{ cookiecutter.__project_name_kebab_case }}."""

    def __init__(self, some_config: int) -> None:
        """Initialize the service.

        Args:
            some_config: Some configuration value.
        """
        self.some_config = some_config

    def my_endpoint_handler(self) -> None:
        """Handle my endpoint."""
