{%- raw %}"""BDD step definitions for API tests."""{% endraw %}

from fastapi.testclient import TestClient
from httpx import Response
from pytest_bdd import given, parsers, scenarios, then, when

from {{ cookiecutter.__project_name_snake_case }}.api import app


scenarios("features/api.feature")


@given("the API test client", target_fixture="client")
def api_client() -> TestClient:
    """Provide a test client for the API."""
    return TestClient(app)


@when(
    parsers.cfparse("I request computation with n={n:d}"),
    target_fixture="response",
)
def request_compute(client: TestClient, n: int) -> Response:
    """Send a compute request to the API."""
    return client.get("/compute", params={"n": n})


@then("the response should be successful")
def check_success(response: Response) -> None:
    """Verify the response has a success status code."""
    assert response.is_success
