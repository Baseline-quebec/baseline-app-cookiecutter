"""Shared fixtures for the test suite."""
{%- if cookiecutter.with_fastapi_api|int %}

import pytest
from fastapi.testclient import TestClient

from {{ cookiecutter.__project_name_snake_case }}.api import app


@pytest.fixture
def api_client() -> TestClient:
    """Provide a FastAPI test client."""
    return TestClient(app)
{%- endif %}
