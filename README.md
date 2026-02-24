[![CI](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/ci.yml/badge.svg)](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/ci.yml) [![Integration](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/test.yml/badge.svg)](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/test.yml) [![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Baseline-quebec/baseline-app-cookiecutter) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=Baseline-quebec/baseline-app-cookiecutter)

# Baseline App Cookiecutter

A modern [Cookiecutter](https://github.com/cookiecutter/cookiecutter) template for scaffolding Python packages and apps at [Baseline](https://github.com/Baseline-quebec).

## Features

- Quick and reproducible development environments with VS Code's [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers), PyCharm's [Docker Compose interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote), and [GitHub Codespaces](https://github.com/features/codespaces)
- Cross-platform support for Linux, macOS (Apple silicon and Intel), and Windows
- Packaging and dependency management with [Poetry](https://github.com/python-poetry/poetry)
- Task running with [Poe the Poet](https://github.com/nat-n/poethepoet)
- Code formatting and linting with [Ruff](https://github.com/charliermarsh/ruff), [Mypy](https://github.com/python/mypy), and [Pre-commit](https://pre-commit.com/)
- Spell checking with [codespell](https://github.com/codespell-project/codespell)
- Documentation with [MkDocs Material](https://squidfunk.github.io/mkdocs-material/)
- Optional [Conventional Commits](https://www.conventionalcommits.org/) with [Commitizen](https://github.com/commitizen-tools/commitizen)
- Optional [FastAPI](https://github.com/tiangolo/fastapi) REST API with health check, CRUD stubs, and Sentry integration
- Optional [Typer](https://github.com/tiangolo/typer) CLI with Rich output
- Optional [pytest-bdd](https://github.com/pytest-dev/pytest-bdd) for BDD-style tests with Gherkin feature files
- Continuous integration with [GitHub Actions](https://docs.github.com/en/actions)
- [LLM Configuration Scanner](https://github.com/Baseline-quebec/tracking-llm-discontinued) to detect deprecated LLM model references
- Test coverage with [Coverage.py](https://github.com/nedbat/coveragepy)
- Scaffolding updates with [Cruft](https://github.com/cruft/cruft)
- Dependency updates with [Dependabot](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/about-dependabot-version-updates)
- [Architecture Decision Records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (ADR) template
- Claude Code instructions (`CLAUDE.md`) for AI-assisted development

## Using

### Creating a new Python project

1. Install [Cruft](https://github.com/cruft/cruft) and [Cookiecutter](https://github.com/cookiecutter/cookiecutter):

   ```sh
   pip install --upgrade "cruft>=2.12.0" "cookiecutter>=2.1.1"
   ```

2. [Create a new repository](https://github.com/new) and clone it locally.

3. Run the following command in the **parent directory** of the cloned repository:

   ```sh
   cruft create -f https://github.com/Baseline-quebec/baseline-app-cookiecutter
   ```

   <details>
   <summary>If your repository name differs from the project's slugified name</summary>

   Copy the scaffolded project into the repository:

   ```sh
   cp -r {project-name}/ {repository-name}/
   ```

   </details>

4. Add the remote origin and push.

### Updating an existing project

```sh
cruft update --cookiecutter-input
```

If any file updates failed, resolve conflicts by inspecting the `.rej` files.

## Developing this template

### Quick reference

| Command | Description |
|---------|-------------|
| `pip install cookiecutter pytest pyyaml` | Install test dependencies |
| `pytest tests/ -v` | Run unit tests (~60 tests, ~7s) |
| `pre-commit run --all-files` | Run linting on template code |

### CI/CD

This repository has three CI workflows:

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| **CI** (`ci.yml`) | Push / PR | Runs unit tests on Python 3.12 + 3.13 (~20s) |
| **PR** (`pr.yml`) | PR | Validates PR title follows conventional commits |
| **Integration** (`test.yml`) | Push / PR | Scaffolds a project, starts a devcontainer, runs `poe lint` + `poe test` (~3 min) |

### Project structure

```
baseline-app-cookiecutter/
├── cookiecutter.json                  # Template parameters
├── hooks/
│   ├── pre_gen_project.py             # Input validation
│   └── post_gen_project.py            # Conditional file removal
├── tests/
│   └── test_cookiecutter.py           # Unit tests for the template
├── {{ cookiecutter.__project_name_kebab_case }}/
│   ├── .devcontainer/                 # Dev Container config
│   ├── .github/workflows/             # CI + LLM scan for generated projects
│   ├── src/{{ ... }}/                 # Source code stubs
│   ├── tests/                         # Test stubs
│   ├── pyproject.toml                 # Poetry config
│   └── ...
├── .github/
│   ├── workflows/ci.yml               # Unit tests
│   ├── workflows/pr.yml               # PR title check
│   ├── workflows/test.yml             # Integration tests
│   ├── dependabot.yml                 # Dependency updates
│   └── CODEOWNERS                     # Code owners
└── .pre-commit-config.yaml            # Linting for template code
```

## Upstream sync

This template is a fork of [superlinear-ai/substrate](https://github.com/superlinear-ai/substrate). The upstream has since migrated to [uv](https://github.com/astral-sh/uv) (replacing Poetry), [Copier](https://copier.readthedocs.io/) (replacing Cookiecutter), and [ty](https://github.com/astral-sh/ty) (replacing Mypy). These are major structural changes that would require reworking the entire Baseline toolchain.

We intentionally stay on **Poetry + Cookiecutter + Mypy** to maintain compatibility with existing Baseline projects. Instead of a full upstream merge, we cherry-pick individual improvements that are independent of the build system migration.

## Template parameters

| Parameter | Description |
|-----------|-------------|
| `project_name` <br> "my-app" | The name of the project. Slugified to `snake_case` for importing and `kebab-case` for installing. |
| `project_description` <br> "A Python app that..." | A single-line description of the project. |
| `github_org` <br> "Baseline-quebec" | The GitHub organization or user that owns the repository. |
| `project_url` <br> auto | Automatically constructed from `github_org` and `project_name`. |
| `author_name` <br> "John Smith" | The full name of the primary author. |
| `author_email` <br> "john@example.com" | The email address of the primary author. |
| `license` <br> ["Proprietary", "MIT", "Apache-2.0"] | The license. Generates a LICENSE file for MIT and Apache-2.0. |
| `python_version` <br> "3.12" | The minimum Python version. |
| `development_environment` <br> ["strict", "simple"] | Strict mode enables additional Ruff rules, strict Mypy, and strict Pytest. |
| `with_conventional_commits` <br> ["0", "1"] | Adds Commitizen for conventional commits. Auto-enabled in strict mode. |
| `with_fastapi_api` <br> ["0", "1"] | Adds FastAPI with health endpoint, CRUD stubs, Pydantic models, and `poe api`. |
| `with_typer_cli` <br> ["0", "1"] | Adds Typer CLI with `info`, `config`, and `health` commands. |
| `with_pytest_bdd` <br> ["0", "1"] | Adds pytest-bdd with Gherkin feature files. Default: plain pytest. |
| `with_sentry` <br> ["0", "1"] | Adds Sentry SDK with FastAPI integration. Requires `with_fastapi_api=1`. |
