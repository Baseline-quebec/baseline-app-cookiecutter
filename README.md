[![CI](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/ci.yml/badge.svg)](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/ci.yml) [![Integration](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/test.yml/badge.svg)](https://github.com/Baseline-quebec/baseline-app-cookiecutter/actions/workflows/test.yml) [![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/Baseline-quebec/baseline-app-cookiecutter) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://github.com/codespaces/new?hide_repo_select=true&ref=main&repo=Baseline-quebec/baseline-app-cookiecutter)

# Baseline App Template

A modern [Copier](https://copier.readthedocs.io/) template for scaffolding Python apps at [Baseline](https://github.com/Baseline-quebec).

## Features

- Quick and reproducible development environments with VS Code's [Dev Containers](https://code.visualstudio.com/docs/devcontainers/containers), PyCharm's [Docker Compose interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote), and [GitHub Codespaces](https://github.com/features/codespaces)
- Cross-platform support for Linux, macOS (Apple silicon and Intel), and Windows
- Packaging and dependency management with [uv](https://github.com/astral-sh/uv)
- Task running with [Poe the Poet](https://github.com/nat-n/poethepoet)
- Code formatting and linting with [Ruff](https://github.com/astral-sh/ruff), [Mypy](https://github.com/python/mypy), and [Pre-commit](https://pre-commit.com/)
- Spell checking with [codespell](https://github.com/codespell-project/codespell)
- Optional [Conventional Commits](https://www.conventionalcommits.org/) with [Commitizen](https://github.com/commitizen-tools/commitizen)
- Optional [FastAPI](https://github.com/tiangolo/fastapi) REST API with health check, CRUD stubs, and Sentry integration
- Optional [Typer](https://github.com/tiangolo/typer) CLI with Rich output
- Optional [pytest-bdd](https://github.com/pytest-dev/pytest-bdd) for BDD-style tests with Gherkin feature files
- Continuous integration with [GitHub Actions](https://docs.github.com/en/actions)
- [LLM Configuration Scanner](https://github.com/Baseline-quebec/tracking-llm-discontinued) to detect deprecated LLM model references
- Test coverage with [Coverage.py](https://github.com/nedbat/coveragepy)
- Scaffolding updates with [Copier](https://copier.readthedocs.io/en/stable/updating/)
- Dependency updates with [Dependabot](https://docs.github.com/en/code-security/supply-chain-security/keeping-your-dependencies-updated-automatically/about-dependabot-version-updates)
- [Architecture Decision Records](https://cognitect.com/blog/2011/11/15/documenting-architecture-decisions) (ADR) template
- Claude Code instructions (`CLAUDE.md`) for AI-assisted development

## Using

### Creating a new Python project

> [!TIP]
> [Install uv](https://docs.astral.sh/uv/getting-started/installation/) first, so you can run Copier without installing it globally.

1. [Create a new repository](https://github.com/new) and clone it locally.

2. Run the following command in the **parent directory** of the cloned repository:

   ```sh
   uvx copier copy gh:Baseline-quebec/baseline-app-cookiecutter my-project
   ```

   Copier writes the project into the directory you name, so pass the cloned
   repository's path to scaffold straight into it.

3. Commit the result and push.

### Updating an existing project

From inside the generated project:

```sh
uvx copier update
```

Copier reads `.copier-answers.yml` to know which template version the project came from, re-asks nothing, and applies only the template's changes.

Where your edits and the template's overlap, Copier performs a three-way merge and leaves **inline conflict markers** (`<<<<<<< before updating`). Find them with `git status` and resolve them like any merge conflict. Pass `--conflict=rej` instead if you prefer `.rej` files alongside the originals.

Generated projects also expose this as `poe update`.

### Migrating a project generated with Cookiecutter

Projects scaffolded before this template moved to Copier have a `.cruft.json` instead of a `.copier-answers.yml`. There is no automatic migration; recreate the answers file once:

1. Create `.copier-answers.yml` in the project root:

   ```yaml
   # Changes here will be overwritten by Copier; NEVER EDIT MANUALLY.
   _commit: v0.1.0
   _src_path: gh:Baseline-quebec/baseline-app-cookiecutter
   ```

   Set `_commit` to the template tag the project was last updated from, and copy the remaining answers out of `.cruft.json`'s `context.cookiecutter` object (dropping the keys that start with `_`).

2. Delete `.cruft.json`.

3. Run `uvx copier update` and resolve any conflicts.

## Developing this template

### Quick reference

| Command | Description |
|---------|-------------|
| `uv sync` | Install the development environment |
| `uv run pytest tests/ -v` | Run unit tests (~119 tests, ~35s) |
| `uv run ruff check . && uv run ruff format --check .` | Lint this repository's own Python |
| `pre-commit run --all-files` | Run all pre-commit hooks |

### CI/CD

This repository has three CI workflows:

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| **CI** (`ci.yml`) | Push / PR | Runs unit tests on Python 3.12, 3.13 and 3.14, plus ruff |
| **PR** (`pr.yml`) | PR | Validates PR title follows conventional commits |
| **Integration** (`test.yml`) | Push / PR | Scaffolds a project on Python 3.12, 3.13 and 3.14, starts a devcontainer, runs `poe lint` + `poe test` |

### Project structure

```
baseline-app-cookiecutter/
├── copier.yml                         # Template questions and computed values
├── pyproject.toml                     # This repo's own tooling (uv, ruff, pytest)
├── uv.lock
├── tests/
│   └── test_template.py               # Unit tests for the template
├── template/                          # Everything below is rendered into the project
│   ├── .devcontainer/                 # Dev Container config
│   ├── .github/workflows/             # CI + LLM scan for generated projects
│   ├── src/{{ project_name_snake_case }}/
│   ├── tests/                         # Test stubs
│   ├── pyproject.toml.jinja           # project config (uv)
│   └── ...
├── .github/
│   ├── workflows/ci.yml               # Unit tests
│   ├── workflows/pr.yml               # PR title check
│   ├── workflows/test.yml             # Integration tests
│   ├── dependabot.yml                 # Dependency updates
│   └── CODEOWNERS                     # Code owners
└── .pre-commit-config.yaml            # Linting for template code
```

Every file under `template/` carries a `.jinja` suffix and is rendered with the
answers from `copier.yml`. Files and directories are included conditionally
through their **path**, not through a post-generation hook — for example
`src/{{ project_name_snake_case }}/{% if with_fastapi_api %}api.py{% endif %}.jinja`
renders to an empty name, and is therefore skipped, when the API is not wanted.

### Releasing a new template version

Copier resolves a template to its **newest git tag**, so generated projects only
see a change after it is tagged:

```sh
git checkout main
cz bump
git push origin main --tags
```

Until the first tag exists, `copier copy` falls back to `HEAD` and warns about it.
The test suite always renders the working tree by passing `--vcs-ref=HEAD`.

## Upstream sync

This template is a fork of [superlinear-ai/substrate](https://github.com/superlinear-ai/substrate). We have adopted the upstream's migrations to [uv](https://github.com/astral-sh/uv) (replacing Poetry) and [Copier](https://copier.readthedocs.io/) (replacing Cookiecutter).

We intentionally stay on **Mypy** rather than [ty](https://github.com/astral-sh/ty), which is still pre-1.0 and has no plugin system — the template depends on the `pydantic.mypy` plugin. Upstream has also dropped the `package` project type and the GitLab CI provider, both of which we keep. Instead of a full upstream merge, we cherry-pick individual improvements.

## Template parameters

| Parameter | Description |
|-----------|-------------|
| `project_name` <br> "my-app" | The name of the project. Slugified to `snake_case` for importing and `kebab-case` for installing. |
| `project_description` <br> "A Python app that..." | A single-line description of the project. |
| `github_org` <br> "Baseline-quebec" | The GitHub organization or user that owns the repository. |
| `project_url` <br> auto | Automatically constructed from `github_org` and `project_name`. |
| `author_name` <br> "John Smith" | The full name of the primary author. |
| `author_email` <br> "john@example.com" | The email address of the primary author. |
| `license` <br> ["Proprietary", "MIT", "Apache-2.0"] | Recorded as SPDX metadata in `pyproject.toml`. No LICENSE file is generated. |
| `python_version` <br> "3.12" | The minimum Python version. |
| `development_environment` <br> ["strict", "simple"] | Strict mode enables additional Ruff rules, strict Mypy, and strict Pytest. |
| `with_conventional_commits` <br> bool, auto | Adds Commitizen for conventional commits. Defaults to true in strict mode. |
| `with_fastapi_api` <br> bool, true | Adds FastAPI with health endpoint, CRUD stubs, Pydantic models, and `poe api`. |
| `with_typer_cli` <br> bool, true | Adds Typer CLI with `info`, `config`, and `health` commands. |
| `with_pytest_bdd` <br> bool, false | Adds pytest-bdd with Gherkin feature files. Default: plain pytest. |
| `with_sentry` <br> bool, false | Adds Sentry SDK with FastAPI integration. Only asked when `with_fastapi_api` is true. |
