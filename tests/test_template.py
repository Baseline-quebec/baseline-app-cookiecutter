"""Tests for the Copier template generation.

These tests validate that the template generates correctly with various
combinations of answers, and that conditional file paths include and exclude
the right files.
"""

import re
import warnings
from pathlib import Path
from typing import Any

import pytest
from copier import run_copy
from copier.errors import DirtyLocalWarning


TEMPLATE_DIR = str(Path(__file__).parent.parent)


@pytest.fixture
def output_dir(tmp_path: Path) -> Path:
    """Provide a temporary output directory."""
    return tmp_path


def kebab_case(project_name: str) -> str:
    """Slugify a project name the same way the template does."""
    return re.sub(r"[^a-z0-9]+", "-", project_name.lower()).strip("-")


def bake(output_dir: Path, **answers: Any) -> Path:
    """Render the template with Copier and return the generated project path."""
    data: dict[str, Any] = {
        "project_name": "test-project",
        "github_org": "TestOrg",
        "license": "MIT",
        "python_version": "3.12",
        "development_environment": "strict",
        "with_fastapi_api": True,
        "with_typer_cli": True,
        "with_pytest_bdd": False,
        "with_sentry": False,
    }
    data.update(answers)
    project = output_dir / kebab_case(str(data["project_name"]))
    with warnings.catch_warnings():
        # Rendering the working tree is exactly what we want here.
        warnings.simplefilter("ignore", DirtyLocalWarning)
        # `vcs_ref="HEAD"` renders the working tree: without it, Copier resolves
        # a local git template to its newest tag, not the checked-out revision.
        run_copy(
            TEMPLATE_DIR,
            str(project),
            data=data,
            defaults=True,
            quiet=True,
            overwrite=True,
            vcs_ref="HEAD",
        )
    return project


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
        bake(output_dir, project_name="My Cool App")
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
        project = bake(output_dir, with_pytest_bdd=False)
        assert not (project / "tests" / "features").exists()

    def test_bdd_off_no_dep(self, output_dir: Path) -> None:
        """When pytest-bdd is off, pytest-bdd is not in dependencies."""
        project = bake(output_dir, with_pytest_bdd=False)
        content = (project / "pyproject.toml").read_text()
        assert "pytest-bdd" not in content

    def test_bdd_off_plain_tests(self, output_dir: Path) -> None:
        """When pytest-bdd is off, test files use plain pytest."""
        project = bake(output_dir, with_pytest_bdd=False)
        test_import = (project / "tests" / "test_import.py").read_text()
        assert "def test_import" in test_import
        assert "pytest_bdd" not in test_import

    def test_bdd_on_features_dir(self, output_dir: Path) -> None:
        """When pytest-bdd is on, tests/features/ exists."""
        project = bake(output_dir, with_pytest_bdd=True)
        assert (project / "tests" / "features").is_dir()
        assert (project / "tests" / "features" / "import.feature").is_file()

    def test_bdd_on_dep_present(self, output_dir: Path) -> None:
        """When pytest-bdd is on, pytest-bdd is in dependencies."""
        project = bake(output_dir, with_pytest_bdd=True)
        content = (project / "pyproject.toml").read_text()
        assert "pytest-bdd" in content

    def test_bdd_on_bdd_tests(self, output_dir: Path) -> None:
        """When pytest-bdd is on, test files use BDD style."""
        project = bake(output_dir, with_pytest_bdd=True)
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
        project = bake(output_dir, with_fastapi_api=True)
        assert (project / "src" / "test_project" / "api.py").is_file()
        assert (project / "src" / "test_project" / "models.py").is_file()
        assert (project / "src" / "test_project" / "services.py").is_file()
        assert (project / "tests" / "test_api.py").is_file()

    def test_fastapi_off(self, output_dir: Path) -> None:
        """FastAPI files are absent when disabled."""
        project = bake(output_dir, with_fastapi_api=False)
        assert not (project / "src" / "test_project" / "api.py").exists()
        assert not (project / "src" / "test_project" / "models.py").exists()
        assert not (project / "tests" / "test_api.py").exists()

    def test_fastapi_deps(self, output_dir: Path) -> None:
        """FastAPI dependency is in pyproject.toml when enabled."""
        project = bake(output_dir, with_fastapi_api=True)
        content = (project / "pyproject.toml").read_text()
        assert "fastapi" in content
        assert "uvicorn" in content
        assert "gunicorn" in content


class TestTyperToggle:
    """Verify with_typer_cli parameter behavior."""

    def test_typer_on(self, output_dir: Path) -> None:
        """Typer CLI files are present when enabled."""
        project = bake(output_dir, with_typer_cli=True)
        assert (project / "src" / "test_project" / "cli.py").is_file()
        assert (project / "tests" / "test_cli.py").is_file()

    def test_typer_off(self, output_dir: Path) -> None:
        """Typer CLI files are absent when disabled."""
        project = bake(output_dir, with_typer_cli=False)
        assert not (project / "src" / "test_project" / "cli.py").exists()
        assert not (project / "tests" / "test_cli.py").exists()


# ---------------------------------------------------------------------------
# Sentry tests
# ---------------------------------------------------------------------------


class TestSentry:
    """Verify with_sentry parameter behavior."""

    def test_sentry_on(self, output_dir: Path) -> None:
        """Sentry dependency is present when enabled."""
        project = bake(output_dir, with_sentry=True, with_fastapi_api=True)
        content = (project / "pyproject.toml").read_text()
        assert "sentry-sdk" in content

    def test_sentry_off(self, output_dir: Path) -> None:
        """Sentry dependency is absent when disabled."""
        project = bake(output_dir, with_sentry=False)
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

    def test_uv_install(self, output_dir: Path) -> None:
        """Dockerfile installs uv and uses `uv sync`."""
        project = bake(output_dir)
        content = (project / "Dockerfile").read_text()
        assert "ghcr.io/astral-sh/uv" in content
        assert "uv sync" in content
        assert "poetry" not in content.lower()

    def test_healthcheck_with_fastapi(self, output_dir: Path) -> None:
        """Dockerfile has HEALTHCHECK when FastAPI is enabled."""
        project = bake(output_dir, with_fastapi_api=True)
        content = (project / "Dockerfile").read_text()
        assert "HEALTHCHECK" in content

    def test_no_healthcheck_without_fastapi(self, output_dir: Path) -> None:
        """Dockerfile has no HEALTHCHECK when FastAPI is disabled."""
        project = bake(output_dir, with_fastapi_api=False)
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
        assert "actions/cache@" in content
        assert "setup-buildx-action" in content


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------


class TestCLI:
    """Verify CLI stub content."""

    def test_cli_has_info_command(self, output_dir: Path) -> None:
        """CLI has info command."""
        project = bake(output_dir, with_typer_cli=True)
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def info(" in content

    def test_cli_has_config_command(self, output_dir: Path) -> None:
        """CLI has config command."""
        project = bake(output_dir, with_typer_cli=True)
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def config(" in content

    def test_cli_has_health_with_fastapi(self, output_dir: Path) -> None:
        """CLI has health command when FastAPI is enabled."""
        project = bake(output_dir, with_typer_cli=True, with_fastapi_api=True)
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def health(" in content

    def test_cli_no_health_without_fastapi(self, output_dir: Path) -> None:
        """CLI has no health command when FastAPI is disabled."""
        project = bake(output_dir, with_typer_cli=True, with_fastapi_api=False)
        content = (project / "src" / "test_project" / "cli.py").read_text()
        assert "def health(" not in content

    def test_cli_no_greet_command(self, output_dir: Path) -> None:
        """CLI does not have the old greet command."""
        project = bake(output_dir, with_typer_cli=True)
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
        """poe update task updates the project from its Copier template."""
        project = bake(output_dir)
        content = (project / "pyproject.toml").read_text()
        assert "[tool.poe.tasks.update]" in content
        assert "copier update" in content
        assert "cruft" not in content

    def test_poe_api_task_uses_exec(self, output_dir: Path) -> None:
        """The api task execs the server so it receives SIGTERM as PID 1.

        The container entrypoint is `poe api`, so without `use_exec` poe stays
        PID 1 and the server never sees `docker stop`'s SIGTERM, which costs a
        full stop timeout and skips graceful shutdown on every deploy.
        """
        import tomllib

        project = bake(output_dir, with_fastapi_api=True)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        api = parsed["tool"]["poe"]["tasks"]["api"]
        # A `shell` task cannot exec; the switch must be `cmd` tasks.
        assert "shell" not in api
        assert api["control"]["expr"] == "bool(${dev})"
        assert len(api["switch"]) == 2
        assert all(case["use_exec"] for case in api["switch"])
        dev, prod = (case for case in api["switch"] if case["case"] == "True"), (
            case for case in api["switch"] if case["case"] == "False"
        )
        assert "uvicorn" in next(dev)["cmd"]
        assert "gunicorn" in next(prod)["cmd"]

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
            with_fastapi_api=False,
            with_typer_cli=False,
            with_pytest_bdd=False,
            with_sentry=False,
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
            with_fastapi_api=True,
            with_typer_cli=True,
            with_pytest_bdd=True,
            with_sentry=True,
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
            with_fastapi_api=False,
            with_typer_cli=True,
            with_pytest_bdd=True,
        )
        assert (project / "tests" / "features" / "import.feature").is_file()
        assert (project / "tests" / "features" / "cli.feature").is_file()
        assert not (project / "tests" / "features" / "api.feature").exists()

    def test_bdd_on_but_no_typer(self, output_dir: Path) -> None:
        """BDD on but no Typer: cli.feature should not exist."""
        project = bake(
            output_dir,
            with_fastapi_api=True,
            with_typer_cli=False,
            with_pytest_bdd=True,
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
        assert "project" in parsed
        assert parsed["project"]["name"] == "test-project"
        assert parsed["build-system"]["build-backend"] == "uv_build"
        assert "uv" in parsed["tool"]
        assert "poetry" not in parsed["tool"]


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
        assert '"codespell>=2.4.0"' in content

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
            with_conventional_commits=False,
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
    """Verify pinned CI tool versions."""

    def test_checkout_version(self, output_dir: Path) -> None:
        """test.yml uses a current actions/checkout."""
        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "test.yml").read_text()
        assert "actions/checkout@v7" in content
        assert "actions/checkout@v6" not in content


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
        project = bake(output_dir, with_fastapi_api=True)
        content = (project / "CLAUDE.md").read_text()
        assert "FastAPI" in content
        assert "poe api" in content

    def test_claude_md_no_fastapi_when_disabled(self, output_dir: Path) -> None:
        """CLAUDE.md does not mention poe api when FastAPI is disabled."""
        project = bake(output_dir, with_fastapi_api=False)
        content = (project / "CLAUDE.md").read_text()
        assert "poe api" not in content


# ---------------------------------------------------------------------------
# README conditionalization tests
# ---------------------------------------------------------------------------


class TestReadmeConditional:
    """Verify README sections are conditionalized correctly."""

    def test_readme_has_api_section_with_fastapi(self, output_dir: Path) -> None:
        """README has API section when FastAPI is enabled."""
        project = bake(output_dir, with_fastapi_api=True)
        content = (project / "README.md").read_text()
        assert "poe api" in content

    def test_readme_no_api_section_without_fastapi(self, output_dir: Path) -> None:
        """README has no API section when FastAPI is disabled."""
        project = bake(output_dir, with_fastapi_api=False)
        content = (project / "README.md").read_text()
        assert "poe api" not in content

    def test_readme_has_cli_section_with_typer(self, output_dir: Path) -> None:
        """README has CLI section when Typer is enabled."""
        project = bake(output_dir, with_typer_cli=True)
        content = (project / "README.md").read_text()
        assert "### CLI" in content

    def test_readme_no_cli_section_without_typer(self, output_dir: Path) -> None:
        """README has no CLI section when Typer is disabled."""
        project = bake(output_dir, with_typer_cli=False)
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
        assert "Bash(uv *)" in allow
        assert "Bash(git *)" in allow
        assert "Bash(gh pr *)" in allow
        assert "Edit" in allow
        assert "Write" in allow
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
        assert "playwright" in content


# ---------------------------------------------------------------------------
# uv migration (Poetry -> uv)
# ---------------------------------------------------------------------------


class TestUvMigration:
    """Verify the project is a well-formed uv project, not a Poetry one."""

    def test_build_backend_is_uv_build(self, output_dir: Path) -> None:
        """Build backend is uv_build, not hatchling or poetry-core."""
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert parsed["build-system"]["build-backend"] == "uv_build"
        requires = " ".join(parsed["build-system"]["requires"])
        assert "uv_build" in requires
        assert "hatchling" not in requires
        assert "poetry" not in requires

    def test_build_backend_targets_src_package(self, output_dir: Path) -> None:
        """The uv build backend points at the src package."""
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        backend = parsed["tool"]["uv"]["build-backend"]
        assert backend["module-name"] == "test_project"
        assert backend["module-root"] == "src"
        assert "hatch" not in parsed["tool"]

    def test_no_tool_poetry_table(self, output_dir: Path) -> None:
        """No [tool.poetry] table remains anywhere in pyproject.toml."""
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert "poetry" not in parsed["tool"]
        assert "poetry" not in (project / "pyproject.toml").read_text().lower()

    def test_dependency_groups_present(self, output_dir: Path) -> None:
        """Dev/test dependencies live under [dependency-groups], not Poetry groups."""
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        groups = parsed["dependency-groups"]
        assert "test" in groups
        assert "dev" in groups
        # test group holds real test deps
        assert any(dep.startswith("pytest") for dep in groups["test"])
        # dev group holds tooling
        assert any(dep.startswith("mkdocs-material") for dep in groups["dev"])

    def test_runtime_deps_use_pep508(self, output_dir: Path) -> None:
        """Runtime dependencies are a PEP 508 list under [project], not a table."""
        import tomllib

        project = bake(output_dir, with_fastapi_api=True)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        deps = parsed["project"]["dependencies"]
        assert isinstance(deps, list)
        assert any(d.startswith("fastapi") for d in deps)
        assert any(d.startswith("pydantic-settings") for d in deps)

    def test_tool_uv_default_groups(self, output_dir: Path) -> None:
        """uv installs the test and dev groups by default."""
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert parsed["tool"]["uv"]["default-groups"] == ["test", "dev"]

    def test_poe_executor_is_simple(self, output_dir: Path) -> None:
        """poe runs tasks in the active venv (simple), not via `uv run`.

        Without this, poethepoet's auto executor triggers an implicit `uv sync`
        that reinstalls the editable project into the baked devcontainer venv and
        fails with a permission error, breaking `poe lint` / `poe test` in CI.
        """
        import tomllib

        project = bake(output_dir)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert parsed["tool"]["poe"]["executor"]["type"] == "simple"

    def test_commitizen_version_provider_is_not_poetry(self, output_dir: Path) -> None:
        """Commitizen does not read the version from Poetry.

        See TestProjectMetadata for the provider actually in use.
        """
        import tomllib

        project = bake(output_dir, development_environment="strict")
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert parsed["tool"]["commitizen"]["version_provider"] != "poetry"

    def test_typer_script_entry_point(self, output_dir: Path) -> None:
        """The CLI entry point is declared under [project.scripts]."""
        import tomllib

        project = bake(output_dir, with_typer_cli=True)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert parsed["project"]["scripts"]["test-project"] == "test_project.cli:app"

    def test_pre_commit_checks_uv_lock(self, output_dir: Path) -> None:
        """The pre-commit lock check uses uv, not `poetry check`."""
        project = bake(output_dir)
        content = (project / ".pre-commit-config.yaml").read_text()
        assert "uv lock --check" in content
        assert "poetry check" not in content

    def test_dependabot_uses_uv_ecosystem(self, output_dir: Path) -> None:
        """Dependabot tracks Python deps via the uv ecosystem, not pip."""
        import yaml

        project = bake(output_dir, development_environment="strict")
        parsed = yaml.safe_load((project / ".github" / "dependabot.yml").read_text())
        ecosystems = {u["package-ecosystem"] for u in parsed["updates"]}
        assert "uv" in ecosystems
        assert "pip" not in ecosystems

    def test_ci_cache_key_uses_uv_lock(self, output_dir: Path) -> None:
        """The CI Docker cache key hashes uv.lock, not poetry.lock."""
        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "test.yml").read_text()
        assert "uv.lock" in content
        assert "poetry.lock" not in content

    def test_dockerfile_installs_project_non_editable_free(self, output_dir: Path) -> None:
        """Dockerfile syncs with uv and never references Poetry."""
        project = bake(output_dir)
        content = (project / "Dockerfile").read_text()
        assert "uv sync" in content
        assert "ghcr.io/astral-sh/uv" in content
        assert "poetry" not in content.lower()

    def test_settings_allow_uv_not_poetry(self, output_dir: Path) -> None:
        """Claude Code settings allow uv commands and drop the Poetry allowance."""
        import json

        project = bake(output_dir)
        allow = json.loads(
            (project / ".claude" / "settings.json").read_text()
        )["permissions"]["allow"]
        assert "Bash(uv *)" in allow
        assert "Bash(poetry *)" not in allow


# ---------------------------------------------------------------------------
# Lint / CI configuration guards
# ---------------------------------------------------------------------------


class TestLintCiConfig:
    """Guard the config that keeps a freshly scaffolded project's CI green.

    These knobs were needed because ruff's preview rules and starlette 1.x
    otherwise make `poe lint` / `poe test` fail on generated projects.
    """

    def test_strict_ignores_churning_preview_rules(self, output_dir: Path) -> None:
        """Strict mode ignores the preview rules that conflict with our style."""
        import tomllib

        project = bake(output_dir, development_environment="strict")
        ignore = tomllib.loads(
            (project / "pyproject.toml").read_bytes().decode()
        )["tool"]["ruff"]["lint"]["ignore"]
        # RUF105: forces `# ruff: ignore` over `# noqa`. PLC0415: lazy imports.
        # RUF201: rewrites rule codes to names in this very config.
        for rule in ("RUF105", "PLC0415", "RUF201"):
            assert rule in ignore

    def test_simple_ignores_churning_preview_rules(self, output_dir: Path) -> None:
        """Simple mode ignores the same preview rules plus RUF100 (unused noqa)."""
        import tomllib

        project = bake(output_dir, development_environment="simple")
        ignore = tomllib.loads(
            (project / "pyproject.toml").read_bytes().decode()
        )["tool"]["ruff"]["lint"]["ignore"]
        for rule in ("RUF105", "PLC0415", "RUF201", "RUF100"):
            assert rule in ignore

    def test_strict_fastapi_filters_starlette_warning(self, output_dir: Path) -> None:
        """With FastAPI, strict pytest ignores starlette's httpx deprecation.

        starlette 1.x raises StarletteDeprecationWarning (a UserWarning, so not
        caught by `ignore::DeprecationWarning`); strict `filterwarnings=error`
        would turn it into a collection error. There is no httpx2 to migrate to.
        """
        import tomllib

        project = bake(output_dir, development_environment="strict", with_fastapi_api=True)
        filters = tomllib.loads(
            (project / "pyproject.toml").read_bytes().decode()
        )["tool"]["pytest"]["ini_options"]["filterwarnings"]
        assert any("StarletteDeprecationWarning" in f for f in filters)

    def test_no_starlette_filter_without_fastapi(self, output_dir: Path) -> None:
        """Without FastAPI, starlette is not installed, so do not reference it.

        Referencing an uninstalled warning class in filterwarnings would make
        pytest error out at startup.
        """
        import tomllib

        project = bake(output_dir, development_environment="strict", with_fastapi_api=False)
        filters = tomllib.loads(
            (project / "pyproject.toml").read_bytes().decode()
        )["tool"]["pytest"]["ini_options"]["filterwarnings"]
        assert not any("starlette" in f for f in filters)

    def test_codespell_ignores_french_terms(self, output_dir: Path) -> None:
        """codespell tolerates the French terms in CLAUDE.md's Agents IA section."""
        import tomllib

        project = bake(output_dir)
        words = tomllib.loads(
            (project / "pyproject.toml").read_bytes().decode()
        )["tool"]["codespell"]["ignore-words-list"]
        for term in ("projet", "architecte", "librairies"):
            assert term in words

    def test_stub_api_has_no_trailing_whitespace(self, output_dir: Path) -> None:
        """The FastAPI stub is free of trailing whitespace (ruff format / W291)."""
        project = bake(output_dir, with_fastapi_api=True)
        for line in (project / "src" / "test_project" / "api.py").read_text().splitlines():
            assert line == line.rstrip(), f"trailing whitespace: {line!r}"


# ---------------------------------------------------------------------------
# Upstream sync: build output and cross-platform hygiene
# ---------------------------------------------------------------------------


class TestIgnoreFiles:
    """Verify that generated build output is ignored."""

    def test_gitignore_ignores_mkdocs_site(self, output_dir: Path) -> None:
        """`mkdocs build` writes site/, which must not be committed."""
        project = bake(output_dir)
        assert "site/" in (project / ".gitignore").read_text().splitlines()

    def test_gitignore_ignores_egg_info(self, output_dir: Path) -> None:
        """An editable install writes *.egg-info/, which must not be committed."""
        project = bake(output_dir)
        assert "*.egg-info/" in (project / ".gitignore").read_text().splitlines()

    def test_dockerignore_excludes_venv(self, output_dir: Path) -> None:
        """A local virtualenv must stay out of the Docker build context."""
        project = bake(output_dir)
        assert ".venv/" in (project / ".dockerignore").read_text().splitlines()


class TestCrossPlatform:
    """Verify cross-platform guards."""

    def test_pre_commit_checks_illegal_windows_names(self, output_dir: Path) -> None:
        """Filenames that are illegal on Windows are rejected before commit."""
        project = bake(output_dir)
        content = (project / ".pre-commit-config.yaml").read_text()
        assert "check-illegal-windows-names" in content

    def test_dockerfile_appends_safe_directory(self, output_dir: Path) -> None:
        """`--add` appends to safe.directory instead of replacing it."""
        project = bake(output_dir)
        content = (project / "Dockerfile").read_text()
        assert "git config --system --add safe.directory" in content


class TestDocsWorkflow:
    """Verify the GitHub Pages documentation workflow."""

    def test_docs_workflow_exists(self, output_dir: Path) -> None:
        """The template ships a workflow that publishes the MkDocs site."""
        project = bake(output_dir)
        assert (project / ".github" / "workflows" / "docs.yml").is_file()

    def test_docs_workflow_valid_yaml(self, output_dir: Path) -> None:
        """docs.yml is valid YAML with the permissions Pages needs."""
        import yaml

        project = bake(output_dir)
        parsed = yaml.safe_load(
            (project / ".github" / "workflows" / "docs.yml").read_text()
        )
        assert parsed["permissions"]["pages"] == "write"
        assert parsed["permissions"]["id-token"] == "write"
        steps = parsed["jobs"]["build-and-deploy"]["steps"]
        assert any("mkdocs build" in step.get("run", "") for step in steps)
        assert any("deploy-pages" in step.get("uses", "") for step in steps)

    def test_docs_workflow_keeps_github_expressions(self, output_dir: Path) -> None:
        """The page_url expression survives templating instead of rendering away."""
        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "docs.yml").read_text()
        assert "${{ steps.deployment.outputs.page_url }}" in content

    def test_mkdocs_declares_repo_and_docs_url(self, output_dir: Path) -> None:
        """mkdocs.yml points at the repository and its published site."""
        import yaml

        project = bake(output_dir, github_org="Baseline-quebec")
        parsed = yaml.safe_load((project / "mkdocs.yml").read_text())
        assert parsed["repo_url"] == "https://github.com/Baseline-quebec/test-project"
        assert parsed["repo_name"] == "Baseline-quebec/test-project"
        assert parsed["site_url"] == "https://baseline-quebec.github.io/test-project"
        assert "pymdownx.superfences" in parsed["markdown_extensions"]

    def test_mkdocs_strict_only_in_strict_mode(self, output_dir: Path) -> None:
        """Strict mode fails the docs build on warnings; simple mode does not."""
        import yaml

        strict = yaml.safe_load(
            (bake(output_dir / "s", development_environment="strict") / "mkdocs.yml").read_text()
        )
        simple = yaml.safe_load(
            (bake(output_dir / "p", development_environment="simple") / "mkdocs.yml").read_text()
        )
        assert strict["strict"] is True
        # Unlisted ADRs must not fail the build.
        assert strict["validation"]["omitted_files"] == "info"
        assert "strict" not in simple


class TestProjectMetadata:
    """Verify [project.urls] and release tooling configuration."""

    def test_well_known_project_urls(self, output_dir: Path) -> None:
        """All well-known project URL labels are populated."""
        import tomllib

        project = bake(output_dir, github_org="Baseline-quebec")
        urls = tomllib.loads((project / "pyproject.toml").read_bytes().decode())["project"]["urls"]
        base = "https://github.com/Baseline-quebec/test-project"
        assert urls["homepage"] == base
        assert urls["source"] == base
        assert urls["changelog"] == f"{base}/blob/main/CHANGELOG.md"
        assert urls["releasenotes"] == f"{base}/releases"
        assert urls["issues"] == f"{base}/issues"
        assert urls["documentation"] == "https://baseline-quebec.github.io/test-project"

    def test_commitizen_version_provider_is_uv(self, output_dir: Path) -> None:
        """Commitizen bumps through uv, so uv.lock stays in step with the version."""
        import tomllib

        project = bake(output_dir, with_conventional_commits=True)
        parsed = tomllib.loads((project / "pyproject.toml").read_bytes().decode())
        assert parsed["tool"]["commitizen"]["version_provider"] == "uv"

    def test_ruff_format_options(self, output_dir: Path) -> None:
        """The formatter formats docstring code and ignores magic trailing commas."""
        import tomllib

        project = bake(output_dir)
        ruff = tomllib.loads((project / "pyproject.toml").read_bytes().decode())["tool"]["ruff"]
        assert ruff["format"]["docstring-code-format"] is True
        assert ruff["format"]["skip-magic-trailing-comma"] is True
        # Without this, isort and the formatter disagree about trailing commas.
        assert ruff["lint"]["isort"]["split-on-trailing-comma"] is False


class TestPinnedCiTooling:
    """Verify that generated CI does not float on upstream releases."""

    def test_devcontainers_cli_is_pinned(self, output_dir: Path) -> None:
        """`@latest` lets an upstream npm release break generated CI."""
        project = bake(output_dir)
        content = (project / ".github" / "workflows" / "test.yml").read_text()
        assert "@devcontainers/cli@latest" not in content
        assert "@devcontainers/cli@0.89.0" in content

    def test_setup_uv_is_pinned_to_an_exact_version(self, output_dir: Path) -> None:
        """setup-uv publishes no floating major tag past v7.

        Its releases are well beyond that, so `@v10` looks current but does not
        resolve and fails the job during setup.
        """
        import re as _re

        project = bake(output_dir)
        workflows = (project / ".github" / "workflows").glob("*.yml")
        refs = [
            ref
            for wf in workflows
            for ref in _re.findall(r"astral-sh/setup-uv@(\S+)", wf.read_text())
        ]
        assert refs, "expected at least one setup-uv reference"
        for ref in refs:
            assert _re.fullmatch(r"v\d+\.\d+\.\d+", ref), (
                f"setup-uv must be pinned to an exact version, got {ref!r}"
            )

    def test_pr_workflow_uses_uvx(self, output_dir: Path) -> None:
        """The PR title check runs commitizen through uvx, with no Python setup."""
        project = bake(output_dir, with_conventional_commits=True)
        content = (project / ".github" / "workflows" / "pr.yml").read_text()
        assert "uvx --from=commitizen cz check" in content
        assert "actions/setup-python" not in content
        assert "pip install" not in content
        # The PR title is attacker-controlled: it must reach cz through the
        # environment, never interpolated into the shell command.
        assert 'PR_TITLE: ${{ github.event.pull_request.title }}' in content
        assert 'cz check --message "$PR_TITLE"' in content

    def test_vscode_fix_on_save_is_ruff_scoped(self, output_dir: Path) -> None:
        """Fix-on-save is scoped to Python and to ruff's own code actions.

        An unscoped `source.fixAll` runs every installed extension's fixer on
        every save, in every language.
        """
        import json

        project = bake(output_dir)
        settings = json.loads(
            (project / ".devcontainer" / "devcontainer.json").read_text()
        )["customizations"]["vscode"]["settings"]
        assert "editor.codeActionsOnSave" not in settings
        actions = settings["[python]"]["editor.codeActionsOnSave"]
        assert actions["source.fixAll.ruff"] == "explicit"
        assert actions["source.organizeImports.ruff"] == "explicit"
