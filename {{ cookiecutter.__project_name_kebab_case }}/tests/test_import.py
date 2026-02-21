{%- if cookiecutter.with_pytest_bdd|int -%}
"""BDD step definitions for package import tests."""

from types import ModuleType

from pytest_bdd import given, scenarios, then

import {{ cookiecutter.__project_name_snake_case }}


scenarios("import.feature")


@given("the package is installed", target_fixture="package")
def installed_package() -> ModuleType:
    """Return the installed package module."""
    return {{ cookiecutter.__project_name_snake_case }}


@then("the package name should be a string")
def check_package_name(package: ModuleType) -> None:
    """Verify the package has a valid name."""
    assert isinstance(package.__name__, str)
{%- else -%}
"""Tests for package import."""

import {{ cookiecutter.__project_name_snake_case }}


def test_import() -> None:
    """Verify the package can be imported and has a valid name."""
    assert isinstance({{ cookiecutter.__project_name_snake_case }}.__name__, str)
{%- endif %}
