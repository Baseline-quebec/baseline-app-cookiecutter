{%- if cookiecutter.with_pytest_bdd|int -%}
"""BDD step definitions for CLI tests."""

from pytest_bdd import given, parsers, scenarios, then, when
from typer.testing import CliRunner, Result

from {{ cookiecutter.__project_name_snake_case }}.cli import app


scenarios("cli.feature")


@given("a CLI runner", target_fixture="runner")
def cli_runner() -> CliRunner:
    """Provide a CLI test runner."""
    return CliRunner()


@when("I run the info command", target_fixture="result")
def run_info(runner: CliRunner) -> Result:
    """Execute the info command."""
    return runner.invoke(app, ["info"])


@when("I run the config command", target_fixture="result")
def run_config(runner: CliRunner) -> Result:
    """Execute the config command."""
    return runner.invoke(app, ["config"])
{%- if cookiecutter.with_fastapi_api|int %}


@when("I run the health command", target_fixture="result")
def run_health(runner: CliRunner) -> Result:
    """Execute the health command."""
    return runner.invoke(app, ["health"])
{%- endif %}


@when("I run the info command with verbose", target_fixture="result")
def run_info_verbose(runner: CliRunner) -> Result:
    """Execute the info command with verbose flag."""
    return runner.invoke(app, ["--verbose", "info"])


@then(parsers.cfparse("the exit code should be {code:d}"))
def check_exit_code(result: Result, code: int) -> None:
    """Verify the CLI exit code."""
    assert result.exit_code == code


@then(parsers.cfparse('the output should contain "{text}"'))
def check_output_contains(result: Result, text: str) -> None:
    """Verify the CLI output contains expected text."""
    assert text in result.stdout
{%- else -%}
"""Tests for the CLI."""

from typer.testing import CliRunner

from {{ cookiecutter.__project_name_snake_case }}.cli import app


runner = CliRunner()


def test_info_command() -> None:
    """Info command displays project metadata."""
    result = runner.invoke(app, ["info"])
    assert result.exit_code == 0
    assert "{{ cookiecutter.project_name }}" in result.stdout


def test_config_command() -> None:
    """Config command displays current settings."""
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0
    assert "app_name" in result.stdout
{%- if cookiecutter.with_fastapi_api|int %}


def test_health_command() -> None:
    """Health command runs without error (no server to check)."""
    result = runner.invoke(app, ["health"])
    # Exit code 1 is expected when no server is running.
    assert result.exit_code in {0, 1}
{%- endif %}


def test_verbose_flag() -> None:
    """Verbose flag is accepted."""
    result = runner.invoke(app, ["--verbose", "info"])
    assert result.exit_code == 0
{%- endif %}
