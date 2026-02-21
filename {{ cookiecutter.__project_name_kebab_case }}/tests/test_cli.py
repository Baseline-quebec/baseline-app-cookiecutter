"""BDD step definitions for CLI tests."""

from typer.testing import CliRunner, Result
from pytest_bdd import given, parsers, scenarios, then, when

from {{ cookiecutter.__project_name_snake_case }}.cli import app


scenarios("features/cli.feature")


@given("a CLI runner", target_fixture="runner")
def cli_runner() -> CliRunner:
    """Provide a CLI test runner."""
    return CliRunner()


@when(
    parsers.cfparse('I run the fire command with name "{name}"'),
    target_fixture="result",
)
def run_fire(runner: CliRunner, name: str) -> Result:
    """Execute the fire command with the given name."""
    return runner.invoke(app, ["--name", name])


@then(parsers.cfparse("the exit code should be {code:d}"))
def check_exit_code(result: Result, code: int) -> None:
    """Verify the CLI exit code."""
    assert result.exit_code == code


@then(parsers.cfparse('the output should contain "{text}"'))
def check_output_contains(result: Result, text: str) -> None:
    """Verify the CLI output contains expected text."""
    assert text in result.stdout
