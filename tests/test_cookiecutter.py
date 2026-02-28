"""Tests for the cookiecutter template generation.

These tests validate that the template generates correctly with various
combinations of parameters and that post-generation hooks work as expected.
"""

import os
import subprocess
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter


TEMPLATE_DIR = str(Path(__file__).parent.parent)


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Provide a temporary output directory."""
    return tmp_path


def bake(output_dir: Path, **extra_context: str) -> Path:
    """Run cookiecutter and return the generated project path."""
    defaults = {
        "project_name": "test-project",
        "github_org": "TestOrg",
        "license": "MIT",
        "python_version": "3.12",
        "development_environment": "strict",
        "with_fastapi_api": "1",
        "with_typer_cli": "1",
        "with_pytest_bdd": "0",
        "with_sentry": "0",
    }
    defaults.update(extra_context)
    cookiecutter(
        TEMPLATE_DIR,
        no_input=True,
        output_dir=str(output_dir),
        extra_context=defaults,
    )
    return output_dir / "test-project"


# ---------------------------------------------------------------------------
# Basic generation tests
# ---------------------------------------------------------------------------


class TestBasicGeneration:
    """Verify that the template generates without errors."""

    def test_default_options(self, output_dir: Path) -> None:
        """Template generates with default options."""
        project = bake(output_dir)
        assert project.is_dir()
        assert (project / "pyproject.toml").is_file()
        assert (project / "src" / "test_project" / "__init__.py").is_file()

    def test_project_name_slugified(self, output_dir: Path) -> None:
        """Project name is correctly slugified."""
        project = bake(output_dir, project_name="My Cool App")
        expected = output_dir / "my-cool-app"
        assert expected.is_dir()
        assert (expected / "src" / "my_cool_app" / "__init__.py").is_file()


# ---------------------------------------------------------------------------
# License tests
# ---------------------------------------------------------------------------


class TestLicense:
    """Verify license parameter behavior."""

    def test_mit_license(self, output_dir: Path) -> None:
        """MIT license generates a LICENSE file with MIT text."""
        project = bake(output_dir, license="MIT")
        license_file = project / "LICENSE"
        assert license_file.is_file()
        content = license_file.read_text()
        assert "MIT License" in content
        assert "John Smith" in content

    def test_apache_license(self, output_dir: Path) -> None:
        """Apache-2.0 license generates a LICENSE file with Apache text."""
        project = bake(output_dir, license="Apache-2.0")
        license_file = project / "LICENSE"
        assert license_file.is_file()
        content = license_file.read_text()
        assert "Apache License" in content

    def test_proprietary_no_license_file(self, output_dir: Path) -> None:
        """Proprietary license removes the LICENSE file."""
        project = bake(output_dir, license="Proprietary")
        assert not (project / "LICENSE").exists()

    def test_license_in_pyproject(self, output_dir: Path) -> None:
        """License value is set in pyproject.toml."""
        project = bake(output_dir, license="MIT")
        content = (project / "pyproject.toml").read_text()
        assert 'license = "MIT"' in content


# ---------------------------------------------------------------------------
# github_org tests
# ---------------------------------------------------------------------------


class TestGithubOrg:
    """Verify github_org parameter behavior."""

    def test_github_org_in_repository_url(self, output_dir: Path) -> None:
        """github_org is used in the repository URL."""
        project = bake(output_dir, github_org="MyOrg")
        content = (project / "pyproject.toml").read_text()
        assert "github.com/MyOrg/test-project" in content


# ---------------------------------------------------------------------------
# pytest-bdd tests
# ---------------------------------------------------------------------------


class TestPytestBdd:
    """Verify pytest-bdd optional behavior."""

    def test_bdd_off_no_features_dir(self, output_dir: Path) -> None:
        """When pytest-bdd is off, tests/features/ does not exist."""
        project = bake(output_dir, with_pytest_bdd="0")
        assert not (project / "tests" / "features").exists()

    def test_bdd_off_no_dep(self, output_dir: Path) -> None:
        """When pytest-bdd is off, pytest-bdd is not in dependencies."""
        project = bake(output_dir, with_pytest_bdd="0")
        content = (project / "pyproject.toml").read_text()
        assert "pytest-bdd" not in content

    def test_bdd_off_plain_tests(self, output_dir: Path) -> None:
        """When pytest-bdd is off, test files use plain pytest."""
        project = bake(output_dir, with_pytest_bdd="0")
        test_import = (project / "tests" / "test_import.py").read_text()
        assert "def test_import" in test_import
        assert "pytest_bdd" not in test_import

    def test_bdd_on_features_dir(self, output_dir: Path) -> None:
        """When pytest-bdd is on, tests/features/ exists."""
        project = bake(output_dir, with_pytest_bdd="1")
        assert (project / "tests" / "features").is_dir()
        assert (project / "tests" / "features" / "import.feature").is_file()

    def test_bdd_on_dep_present(self, output_dir: Path) -> None:
        """When pytest-bdd is on, pytest-bdd is in dependencies."""
        project = bake(output_dir, with_pytest_bdd="1")
        content = (project / "pyproject.toml").read_text()
        assert "pytest-bdd" in content

    def test_bdd_on_bdd_tests(self, output_dir: Path) -> None:
        """When pytest-bdd is on, test files use BDD style."""
        project = bake(output_dir, with_pytest_bdd="1")
        test_import = (project / "tests" / "test_import.py").read_text()
        assert "from pytest_bdd import" in test_import
        assert "scenarios(" in test_import


# ---------------------------------------------------------------------------
# FastAPI / Typer toggle tests
# ---------------------------------------------------------------------------


class TestFastapiToggle:
    """Verify with_fastapi_api parameter behavior."""

    def test_fastapi_on(self, output_dir: Path) -> None:
        """FastAPI files are present when enabled."""
        project = bake(output_dir, with_fastapi_api="1")
        assert (project / "src" / "test_project" / "api.py").is_file()
        assert (project / "src" / "test_project" / "models.py").is_file()
        assert (project / "src" / "test_project" / "services.py").is_file()
        assert (project / "tests" / "test_api.py").is_file()

    def test_fastapi_off(self, output_dir: Path) -> None:
        """FastAPI files are absent when disabled."""
        project = bake(output_dir, with_fastapi_api="0")
        assert not (project / "src" / "test_project" / "api.py").exists()
        assert not (project / "src" / "test_project" / "models.py").exists()
        assert not (project / "tests" / "test_api.py").exists()

    def test_fastapi_deps(self, output_dir: Path) -> None:
        """FastAPI dependency is in pyproject.toml when enabled."""
        project = bake(output_dir, with_fastapi_api="1")
        content = (project / "pyproject.toml").read_text()
        assert "fastapi" in content
        assert "uvicorn" in content
        assert "gunicorn" in content


class TestTyperToggle:
    """Verify with_typer_cli parameter behavior."""

    def test_typer_on(self, output_dir: Path) -> None:
        """Typer CLI files are present when enabled."""
        project = bake(output_dir, with_typer_cli="1")
        assert (project / "src" / "test_project" / "cli.py").is_file()
        assert (project / "tests" / "test_cli.py").is_file()

    def test_typer_off(self, output_dir: Path) -> None:
        """Typer CLI files are absent when disabled."""
        project = bake(output_dir, with_typer_cli="0")
        assert not (project / "src" / "test_project" / "cli.py").exists()
        assert not (project / "tests" / "test_cli.py").exists()


# ---------------------------------------------------------------------------
# Sentry tests
# ---------------------------------------------------------------------------


class TestSentry:
    """Verify with_sentry parameter behavior."""

    def test_sentry_on(self, output_dir: Path) -> None:
        """Sentry dependency is present when enabled."""
        project = bake(output_dir, with_sentry="1", with_fastapi_api="1")
        content = (project / "pyproject.toml").read_text()
        assert "sentry-sdk" in content

    def test_sentry_off(self, output_dir: Path) -> None:
        """Sentry dependency is absent when disabled."""
        project = bake(output_dir, with_sentry="0")
        content = (project / "pyproject.toml").read_text()
        assert "sentry-sdk" not in content


# ---------------------------------------------------------------------------
# Development environment tests
# ---------------------------------------------------------------------------


class TestDevelopmentEnvironment:
    """Verify strict vs simple mode."""

    def test_strict_has_dependabot(self, output_dir: Path) -> None:
        """Strict mode includes dependabot.yml."""
        project = bake(output_dir, development_environment="strict")
        assert (project / ".github" / "dependabot.yml").is_file()

    def test_simple_no_dependabot(self, output_dir: Path) -> None:
        """Simple mode removes dependabot.yml."""
        project = bake(output_dir, development_environment="simple")
        assert not (project / ".github" / "dependabot.yml").exists()

    def test_strict_has_safety(self, output_dir: Path) -> None:
        """Strict mode includes safety in dependencies."""
        project = bake(output_dir, development_environment="strict")
        content = (project / "pyproject.toml").read_text()
        assert "safety" in content

    def test_simple_no_safety(self, output_dir: Path) -> None:
        """Simple mode does not include safety."""
        project = bake(output_dir, development_environment="simple")
        content = (project / "pyproject.toml").read_text()
        assert "safety" not in content


# ---------------------------------------------------------------------------
# Dockerfile tests
# ---------------------------------------------------------------------------


class TestDockerfile:
    """Verify Dockerfile structure."""

    def test_three_stages(self, output_dir: Path) -> None:
        """Dockerfile has exactly 3 stages: base, dev, app."""
        project = bake(output_dir)
        content = (project / "Dockerfile").read_text()
        from_lines = [l.strip() for l in content.splitlines() if l.startswith("FROM")]
        assert len(from_lines) == 3
        assert "AS base" in from_lines[0]
        assert "AS dev" in from_lines[1]
        assert "AS app" in from_lines[2]

    def test_poetry_version(self, output_dir: Path) -> None:
        """Dockerfile uses Poetry 2.3.x."""
        project = bake(output_dir)
        content = (project / "Dockerfile").read_text()
        assert "POETRY_VERSION=2.3." in content

    def test_healthcheck_with_fastapi(self, output_dir: Path) -> None:
        """Dockerfile has HEALTHCHECK when FastAPI is enabled."""
        project = bake(output_dir, with_fastapi_api="1")
        content = (project / "Dockerfile").read_text()
        assert "HEALTHCHECK" in content

    def test_no_healthcheck_without_fastapi(self, output_dir: Path) -> None:
        """Dockerfile has no HEALTHCHECK when FastAPI is disabled."""
        project = bake(output_dir, with_fastapi_api="0")
        content = (project / "Dockerfile").read_text()
        assert "HEALTHCHECK" not in content


# ---------------------------------------------------------------------------
# CI workflow tests
# ---------------------------------------------------------------------------


class TestCIWorkflow:
    """Verify CI workflow structure."""

    def test_workflow_valid_yaml(self, output_dir: Path) -> None:
        """CI workflow is valid YAML."""
        import yaml

        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "test.yml").read_text()
        parsed = yaml.safe_load(content)
        assert parsed["name"] == "Test"
        assert "test" in parsed["jobs"]

    def test_docker_cache_step(self, output_dir: Path) -> None:
        """CI workflow has Docker layer caching."""
        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "test.yml").read_text()
        assert "actions/cache@v4" in content
        assert "setup-buildx-action" in content


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    """Verify CLI stub content."""

    def test_cli_has_info_command(self, output_dir: Path) -> None:
        """CLI has info command."""
        project = bake(output_dir, with_typer_cli="1")
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def info(" in content

    def test_cli_has_config_command(self, output_dir: Path) -> None:
        """CLI has config command."""
        project = bake(output_dir, with_typer_cli="1")
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def config(" in content

    def test_cli_has_health_with_fastapi(self, output_dir: Path) -> None:
        """CLI has health command when FastAPI is enabled."""
        project = bake(output_dir, with_typer_cli="1", with_fastapi_api="1")
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def health(" in content

    def test_cli_no_health_without_fastapi(self, output_dir: Path) -> None:
        """CLI has no health command when FastAPI is disabled."""
        project = bake(output_dir, with_typer_cli="1", with_fastapi_api="0")
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def health(" not in content

    def test_cli_no_greet_command(self, output_dir: Path) -> None:
        """CLI does not have the old greet command."""
        project = bake(output_dir, with_typer_cli="1")
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def greet(" not in content


# ---------------------------------------------------------------------------
# ADR / docs tests
# ---------------------------------------------------------------------------


class TestDocs:
    """Verify documentation files."""

    def test_adr_template_exists(self, output_dir: Path) -> None:
        """ADR template exists."""
        project = bake(output_dir)
        assert (project / "docs" / "decisions" / "adr_template.md").is_file()

    def test_first_adr_exists(self, output_dir: Path) -> None:
        """First ADR (0001) exists."""
        project = bake(output_dir)
        adr = project / "docs" / "decisions" / "0001-record-architecture-decisions.md"
        assert adr.is_file()
        assert "Record architecture decisions" in adr.read_text()

    def test_readme_has_docs_section(self, output_dir: Path) -> None:
        """Generated README has Documentation section."""
        project = bake(output_dir)
        content = (project / "README.md").read_text()
        assert "## Documentation" in content
        assert "Architecture Decision Records" in content


# ---------------------------------------------------------------------------
# Poe tasks tests
# ---------------------------------------------------------------------------


class TestPoeTasks:
    """Verify poe tasks in pyproject.toml."""

    def test_poe_update_task(self, output_dir: Path) -> None:
        """poe update task is present."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "[tool.poe.tasks.update]" in content
        assert "cruft update" in content

    def test_poe_lint_task(self, output_dir: Path) -> None:
        """poe lint task is present."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "[tool.poe.tasks.lint]" in content

    def test_poe_test_task(self, output_dir: Path) -> None:
        """poe test task is present."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "[tool.poe.tasks.test]" in content


# ---------------------------------------------------------------------------
# Full combination matrix tests
# ---------------------------------------------------------------------------


class TestCombinations:
    """Test specific combinations that are likely to cause issues."""

    def test_minimal_no_api_no_cli_no_bdd(self, output_dir: Path) -> None:
        """Minimal project: no FastAPI, no Typer, no BDD."""
        project = bake(
            output_dir,
            with_fastapi_api="0",
            with_typer_cli="0",
            with_pytest_bdd="0",
            with_sentry="0",
            development_environment="simple",
        )
        assert project.is_dir()
        assert (project / "pyproject.toml").is_file()
        assert (project / "tests" / "test_import.py").is_file()
        # No feature files, no API/CLI tests
        assert not (project / "tests" / "features").exists()
        assert not (project / "tests" / "test_api.py").exists()
        assert not (project / "tests" / "test_cli.py").exists()

    def test_full_everything_enabled(self, output_dir: Path) -> None:
        """Full project: all options enabled."""
        project = bake(
            output_dir,
            license="MIT",
            with_fastapi_api="1",
            with_typer_cli="1",
            with_pytest_bdd="1",
            with_sentry="1",
            development_environment="strict",
        )
        assert project.is_dir()
        assert (project / "LICENSE").is_file()
        assert (project / "tests" / "features").is_dir()
        assert (project / "tests" / "test_api.py").is_file()
        assert (project / "tests" / "test_cli.py").is_file()
        content = (project / "pyproject.toml").read_text()
        assert "pytest-bdd" in content
        assert "sentry-sdk" in content
        assert "commitizen" in content

    def test_bdd_on_but_no_fastapi(self, output_dir: Path) -> None:
        """BDD on but no FastAPI: api.feature should not exist."""
        project = bake(
            output_dir,
            with_fastapi_api="0",
            with_typer_cli="1",
            with_pytest_bdd="1",
        )
        assert (project / "tests" / "features" / "import.feature").is_file()
        assert (project / "tests" / "features" / "cli.feature").is_file()
        assert not (project / "tests" / "features" / "api.feature").exists()

    def test_bdd_on_but_no_typer(self, output_dir: Path) -> None:
        """BDD on but no Typer: cli.feature should not exist."""
        project = bake(
            output_dir,
            with_fastapi_api="1",
            with_typer_cli="0",
            with_pytest_bdd="1",
        )
        assert (project / "tests" / "features" / "import.feature").is_file()
        assert (project / "tests" / "features" / "api.feature").is_file()
        assert not (project / "tests" / "features" / "cli.feature").exists()

    def test_pyproject_toml_valid_toml(self, output_dir: Path) -> None:
        """Generated pyproject.toml is valid TOML."""
        import tomllib

        project = bake(output_dir)
        content = (project / "pyproject.toml").read_bytes()
        parsed = tomllib.loads(content.decode())
        assert "tool" in parsed
        assert "poetry" in parsed["tool"]


# ---------------------------------------------------------------------------
# Sprint 4: codespell tests
# ---------------------------------------------------------------------------


class TestCodespell:
    """Verify codespell hook and configuration."""

    def test_codespell_in_pre_commit(self, output_dir: Path) -> None:
        """codespell hook is present in pre-commit config."""
        project = bake(output_dir)
        content = (project / ".pre-commit-config.yaml").read_text()
        assert "id: codespell" in content
        assert "entry: codespell" in content

    def test_codespell_dep_in_pyproject(self, output_dir: Path) -> None:
        """codespell dependency is in test dependencies."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert 'codespell = ">=2.4.0"' in content

    def test_codespell_config_in_pyproject(self, output_dir: Path) -> None:
        """codespell configuration section exists in pyproject.toml."""
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert "codespell" in parsed["tool"]
        assert parsed["tool"]["codespell"]["check-filenames"] is True


# ---------------------------------------------------------------------------
# Sprint 4: PR title check workflow tests
# ---------------------------------------------------------------------------


class TestPRWorkflow:
    """Verify PR title conventional commit check workflow."""

    def test_pr_yml_exists_with_conventional_commits(self, output_dir: Path) -> None:
        """pr.yml exists when conventional commits is enabled."""
        project = bake(output_dir, development_environment="strict")
        assert (project / ".github" / "workflows" / "pr.yml").is_file()

    def test_pr_yml_absent_without_conventional_commits(self, output_dir: Path) -> None:
        """pr.yml does not exist when conventional commits is disabled."""
        project = bake(
            output_dir,
            development_environment="simple",
            with_conventional_commits="0",
        )
        assert not (project / ".github" / "workflows" / "pr.yml").exists()

    def test_pr_yml_has_commitizen(self, output_dir: Path) -> None:
        """pr.yml uses commitizen to check PR title."""
        project = bake(output_dir, development_environment="strict")
        content = (project / ".github" / "workflows" / "pr.yml").read_text()
        assert "commitizen" in content
        assert "cz check" in content

    def test_pr_yml_valid_yaml(self, output_dir: Path) -> None:
        """pr.yml is valid YAML."""
        import yaml

        project = bake(output_dir, development_environment="strict")
        content = (project / ".github" / "workflows" / "pr.yml").read_text()
        parsed = yaml.safe_load(content)
        assert parsed["name"] == "PR"
        assert "title" in parsed["jobs"]


# ---------------------------------------------------------------------------
# Sprint 4: actions/checkout v6 tests
# ---------------------------------------------------------------------------


class TestCheckoutVersion:
    """Verify actions/checkout version bump."""

    def test_checkout_v6(self, output_dir: Path) -> None:
        """test.yml uses actions/checkout@v6."""
        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "test.yml").read_text()
        assert "actions/checkout@v6" in content
        assert "actions/checkout@v5" not in content


# ---------------------------------------------------------------------------
# Sprint 4: MkDocs Material tests
# ---------------------------------------------------------------------------


class TestMkDocs:
    """Verify MkDocs Material replaces pdoc."""

    def test_mkdocs_yml_exists(self, output_dir: Path) -> None:
        """mkdocs.yml is generated."""
        project = bake(output_dir)
        assert (project / "mkdocs.yml").is_file()

    def test_mkdocs_yml_has_project_name(self, output_dir: Path) -> None:
        """mkdocs.yml contains the project name."""
        project = bake(output_dir)
        content = (project / "mkdocs.yml").read_text()
        assert "test-project" in content

    def test_mkdocs_material_dep(self, output_dir: Path) -> None:
        """mkdocs-material is in dev dependencies."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "mkdocs-material" in content

    def test_pdoc_absent(self, output_dir: Path) -> None:
        """pdoc is not in dependencies."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "pdoc" not in content

    def test_poe_docs_uses_mkdocs(self, output_dir: Path) -> None:
        """poe docs task uses mkdocs."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "mkdocs" in content
        assert "[tool.poe.tasks.docs]" in content
        assert "--serve" in content

    def test_docs_index_md_exists(self, output_dir: Path) -> None:
        """docs/index.md is generated."""
        project = bake(output_dir)
        assert (project / "docs" / "index.md").is_file()


# ---------------------------------------------------------------------------
# CLAUDE.md tests
# ---------------------------------------------------------------------------


class TestClaudeMd:
    """Verify CLAUDE.md is generated with correct content."""

    def test_claude_md_exists(self, output_dir: Path) -> None:
        """CLAUDE.md is generated."""
        project = bake(output_dir)
        assert (project / "CLAUDE.md").is_file()

    def test_claude_md_has_project_name(self, output_dir: Path) -> None:
        """CLAUDE.md contains the project name."""
        project = bake(output_dir)
        content = (project / "CLAUDE.md").read_text()
        assert "test-project" in content

    def test_claude_md_has_snake_case_import(self, output_dir: Path) -> None:
        """CLAUDE.md references the correct import path."""
        project = bake(output_dir)
        content = (project / "CLAUDE.md").read_text()
        assert "test_project" in content

    def test_claude_md_has_fastapi_when_enabled(self, output_dir: Path) -> None:
        """CLAUDE.md mentions FastAPI when enabled."""
        project = bake(output_dir, with_fastapi_api="1")
        content = (project / "CLAUDE.md").read_text()
        assert "FastAPI" in content
        assert "poe api" in content

    def test_claude_md_no_fastapi_when_disabled(self, output_dir: Path) -> None:
        """CLAUDE.md does not mention poe api when FastAPI is disabled."""
        project = bake(output_dir, with_fastapi_api="0")
        content = (project / "CLAUDE.md").read_text()
        assert "poe api" not in content


# ---------------------------------------------------------------------------
# README conditionalization tests
# ---------------------------------------------------------------------------


class TestReadmeConditional:
    """Verify README sections are conditionalized correctly."""

    def test_readme_has_api_section_with_fastapi(self, output_dir: Path) -> None:
        """README has API section when FastAPI is enabled."""
        project = bake(output_dir, with_fastapi_api="1")
        content = (project / "README.md").read_text()
        assert "poe api" in content

    def test_readme_no_api_section_without_fastapi(self, output_dir: Path) -> None:
        """README has no API section when FastAPI is disabled."""
        project = bake(output_dir, with_fastapi_api="0")
        content = (project / "README.md").read_text()
        assert "poe api" not in content

    def test_readme_has_cli_section_with_typer(self, output_dir: Path) -> None:
        """README has CLI section when Typer is enabled."""
        project = bake(output_dir, with_typer_cli="1")
        content = (project / "README.md").read_text()
        assert "### CLI" in content

    def test_readme_no_cli_section_without_typer(self, output_dir: Path) -> None:
        """README has no CLI section when Typer is disabled."""
        project = bake(output_dir, with_typer_cli="0")
        content = (project / "README.md").read_text()
        assert "### CLI" not in content

    def test_readme_has_env_example(self, output_dir: Path) -> None:
        """README references .env.example (not .env.sample)."""
        project = bake(output_dir)
        content = (project / "README.md").read_text()
        assert ".env.example" in content
        assert ".env.sample" not in content

    def test_readme_has_mkdocs(self, output_dir: Path) -> None:
        """README references MkDocs."""
        project = bake(output_dir)
        content = (project / "README.md").read_text()
        assert "poe docs" in content


# ---------------------------------------------------------------------------
# Claude Code configuration tests
# ---------------------------------------------------------------------------


class TestClaudeCodeConfig:
    """Verify Claude Code configuration files."""

    def test_mcp_json_exists(self, output_dir: Path) -> None:
        """.mcp.json is generated."""
        project = bake(output_dir)
        assert (project / ".mcp.json").is_file()

    def test_mcp_json_has_context7(self, output_dir: Path) -> None:
        """.mcp.json contains context7 server."""
        import json

        project = bake(output_dir)
        content = json.loads((project / ".mcp.json").read_text())
        assert "context7" in content["mcpServers"]
        assert content["mcpServers"]["context7"]["command"] == "npx"

    def test_mcp_json_has_playwright(self, output_dir: Path) -> None:
        """.mcp.json contains playwright server."""
        import json

        project = bake(output_dir)
        content = json.loads((project / ".mcp.json").read_text())
        assert "playwright" in content["mcpServers"]
        assert content["mcpServers"]["playwright"]["command"] == "npx"

    def test_claude_settings_local_exists(self, output_dir: Path) -> None:
        """.claude/settings.local.json is generated."""
        project = bake(output_dir)
        assert (project / ".claude" / "settings.local.json").is_file()

    def test_claude_settings_local_enables_servers(self, output_dir: Path) -> None:
        """.claude/settings.local.json enables MCP servers."""
        import json

        project = bake(output_dir)
        content = json.loads(
            (project / ".claude" / "settings.local.json").read_text()
        )
        assert "context7" in content["enabledMcpjsonServers"]
        assert "playwright" in content["enabledMcpjsonServers"]

    def test_gitignore_has_claude_settings(self, output_dir: Path) -> None:
        """.gitignore contains .claude/settings.local.json."""
        project = bake(output_dir)
        content = (project / ".gitignore").read_text()
        assert ".claude/settings.local.json" in content

    def test_gitignore_does_not_exclude_mcp_json(self, output_dir: Path) -> None:
        """.gitignore does not exclude .mcp.json."""
        project = bake(output_dir)
        content = (project / ".gitignore").read_text()
        assert ".mcp.json" not in content

    def test_claude_settings_json_exists(self, output_dir: Path) -> None:
        """.claude/settings.json is generated."""
        project = bake(output_dir)
        assert (project / ".claude" / "settings.json").is_file()

    def test_claude_settings_has_permissions(self, output_dir: Path) -> None:
        """.claude/settings.json has Dev Flow permission profile."""
        import json

        project = bake(output_dir)
        content = json.loads((project / ".claude" / "settings.json").read_text())
        allow = content["permissions"]["allow"]
        deny = content["permissions"]["deny"]
        assert "Bash(poetry *)" in allow
        assert "Bash(git *)" in allow
        assert "Bash(gh pr *)" in allow
        assert "Edit" in allow
        assert "Write" in allow
        assert "mcp__context7__query-docs" in allow
        assert "mcp__playwright__browser_snapshot" in allow
        assert "Bash(git reset --hard *)" in deny
        assert "Bash(rm *)" in deny

    def test_claude_settings_has_plugins(self, output_dir: Path) -> None:
        """.claude/settings.json enables superpowers and code-review plugins."""
        import json

        project = bake(output_dir)
        content = json.loads((project / ".claude" / "settings.json").read_text())
        plugins = content["enabledPlugins"]
        assert plugins["superpowers@claude-plugins-official"] is True
        assert plugins["code-review@claude-plugins-official"] is True

    def test_claude_md_has_agents_ia_section(self, output_dir: Path) -> None:
        """CLAUDE.md contains the Agents IA section."""
        project = bake(output_dir)
        content = (project / "CLAUDE.md").read_text()
        assert "## Agents IA" in content
        assert "contremaitre" in content.lower()
        assert "context7" in content
        assert "playwright" in content
