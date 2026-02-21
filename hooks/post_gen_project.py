"""Post-generation hook: remove files based on cookiecutter options."""

import os
import shutil

# Read Cookiecutter configuration.
project_name = "{{ cookiecutter.__project_name_snake_case }}"
development_environment = "{{ cookiecutter.development_environment }}"
with_conventional_commits = int("{{ cookiecutter.with_conventional_commits }}")
with_fastapi_api = int("{{ cookiecutter.with_fastapi_api }}")
with_typer_cli = int("{{ cookiecutter.with_typer_cli }}")
with_pytest_bdd = int("{{ cookiecutter.with_pytest_bdd }}")
license_choice = "{{ cookiecutter.license }}"

# Remove PR title check workflow if conventional commits is disabled.
if not with_conventional_commits:
    os.remove(".github/workflows/pr.yml")

# Remove py.typed and Dependabot if not in strict mode.
if development_environment != "strict":
    os.remove(f"src/{project_name}/py.typed")
    os.remove(".github/dependabot.yml")

# Remove FastAPI if not selected.
if not with_fastapi_api:
    os.remove(f"src/{project_name}/api.py")
    os.remove(f"src/{project_name}/models.py")
    os.remove(f"src/{project_name}/services.py")
    os.remove("tests/test_api.py")
    if with_pytest_bdd:
        os.remove("tests/features/api.feature")

# Remove Typer if not selected.
if not with_typer_cli:
    os.remove(f"src/{project_name}/cli.py")
    os.remove("tests/test_cli.py")
    if with_pytest_bdd:
        os.remove("tests/features/cli.feature")

# Remove .vscode/ directory if not using FastAPI (no launch.json needed).
if not with_fastapi_api and not with_typer_cli:
    shutil.rmtree(".vscode", ignore_errors=True)

# Remove BDD test infrastructure when pytest-bdd is not selected.
if not with_pytest_bdd:
    shutil.rmtree("tests/features", ignore_errors=True)

# Remove LICENSE file for proprietary projects.
if license_choice == "Proprietary":
    os.remove("LICENSE")
