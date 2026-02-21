"""Shared fixtures for the test suite."""
{%- if cookiecutter.with_fastapi_api|int %}

from fastapi.testclient import TestClient

import pytest

from {{ cookiecutter.__project_name_snake_case }}.api import app


@pytest.fixture
def api_client() -> TestClient:
    """Provide a FastAPI test client."""
    return TestClient(app)
{%- endif %}
