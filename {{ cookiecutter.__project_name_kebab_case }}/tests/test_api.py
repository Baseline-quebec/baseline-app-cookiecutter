{%- if cookiecutter.with_pytest_bdd|int -%}
{%- raw %}"""BDD step definitions for API tests."""{% endraw %}

from fastapi.testclient import TestClient
from httpx import Response
from pytest_bdd import given, parsers, scenarios, then, when

from {{ cookiecutter.__project_name_snake_case }}.api import app


scenarios("api.feature")


@given("the API test client", target_fixture="client")
def api_client() -> TestClient:
    """Provide a test client for the API."""
    return TestClient(app)


@when(
    parsers.cfparse("I request GET {path}"),
    target_fixture="response",
)
def request_get(client: TestClient, path: str) -> Response:
    """Send a GET request to the given path."""
    return client.get(path)


@when(
    parsers.cfparse('I create an item with name "{name}" and price {price:f}'),
    target_fixture="response",
)
def create_item(client: TestClient, name: str, price: float) -> Response:
    """Send a POST request to create an item."""
    return client.post("/items", json={"name": name, "price": price})


@then(parsers.cfparse("the response status code should be {code:d}"))
def check_status_code(response: Response, code: int) -> None:
    """Verify the response status code."""
    assert response.status_code == code


@then(parsers.cfparse('the response JSON should contain "{key}" = "{value}"'))
def check_json_field(response: Response, key: str, value: str) -> None:
    """Verify a field in the response JSON."""
    assert response.json()[key] == value
{%- else -%}
"""Tests for the REST API."""

from fastapi.testclient import TestClient

from {{ cookiecutter.__project_name_snake_case }}.api import app


client = TestClient(app)


def test_health_endpoint() -> None:
    """Health endpoint returns ok status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_create_item() -> None:
    """Create an item via POST."""
    response = client.post("/items", json={"name": "Widget", "price": 9.99})
    assert response.status_code == 201
    assert response.json()["name"] == "Widget"


def test_get_nonexistent_item() -> None:
    """GET a non-existent item returns 404."""
    response = client.get("/items/999")
    assert response.status_code == 404
{%- endif %}
