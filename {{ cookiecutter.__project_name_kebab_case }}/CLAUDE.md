# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Conventions

This project follows the [Baseline development conventions](https://github.com/Baseline-quebec/agents/blob/main/programmation/knowledge/conventions-baseline.md).

### Key rules

- **Language**: Code, commits, branches, and PRs in English. User-facing docs in French.
- **Naming**: `snake_case` (code), `kebab-case` (repos), `PascalCase` (classes), `UPPER_SNAKE_CASE` (constants)
- **Imports**: Absolute only (`from {{ cookiecutter.__project_name_snake_case }}.module import X`)
- **Type hints**: Required on all function signatures
- **Docstrings**: Google convention
- **Line length**: 99 characters max
- **Config**: Everything in `pyproject.toml` (no separate `.mypy.ini`, `.pylintrc`, etc.)

## Project layout

```
src/{{ cookiecutter.__project_name_snake_case }}/   # source code (src layout)
tests/                                              # test suite
docs/                                               # MkDocs documentation + ADRs
pyproject.toml                                      # Poetry config, tool settings
```

## Commands

Always use `poetry run` — never `poetry shell`.

```bash
poetry install                # install dependencies
poetry run poe lint           # ruff + mypy + pre-commit
poetry run poe test           # pytest with coverage
poetry run poe docs --serve   # serve MkDocs locally
{%- if cookiecutter.with_fastapi_api|int %}
poetry run poe api --dev      # start FastAPI dev server
{%- endif %}
```

## Git workflow

- **Branches**: `feat/`, `fix/`, `refactor/`, `docs/` + kebab-case description
- **Commits**: [Conventional Commits](https://www.conventionalcommits.org/) — `feat(scope): description`
- **PRs**: Squash merge only. PR title = final commit message on `main`.
- Never commit directly to `main`.

## Tech stack

- **Package manager**: [Poetry](https://python-poetry.org/)
- **Task runner**: [Poe the Poet](https://github.com/nat-n/poethepoet)
- **Linting**: [Ruff](https://docs.astral.sh/ruff/) (linting + formatting)
- **Type checking**: [Mypy](https://mypy.readthedocs.io/) (strict mode)
- **Testing**: [pytest](https://docs.pytest.org/){% if cookiecutter.with_pytest_bdd|int %} + [pytest-bdd](https://pytest-bdd.readthedocs.io/){% endif %}

- **CI**: GitHub Actions in devcontainer
{%- if cookiecutter.with_fastapi_api|int %}
- **API**: [FastAPI](https://fastapi.tiangolo.com/) + [Pydantic](https://docs.pydantic.dev/)
{%- endif %}
{%- if cookiecutter.with_typer_cli|int %}
- **CLI**: [Typer](https://typer.tiangolo.com/) + [Rich](https://rich.readthedocs.io/)
{%- endif %}
- **Config**: [pydantic-settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) with `.env` file
