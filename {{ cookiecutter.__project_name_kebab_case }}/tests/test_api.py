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
