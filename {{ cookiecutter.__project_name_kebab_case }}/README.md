# {{ cookiecutter.project_name }}

{{ cookiecutter.project_description }}

## Documentation

- [Architecture Decision Records](docs/decisions/)
- [MkDocs](https://{{ cookiecutter.github_org }}.github.io/{{ cookiecutter.__project_name_kebab_case }}/) (run `poe docs --serve` locally)

## Setup

### Environment variables

Create a copy of `.env.example` and fill in the values:

```bash
cp .env.example .env
```

### Local setup

Requirements:

- [Python {{ cookiecutter.python_version }}](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

```bash
poetry install
```

### Container setup

Requirements: [Docker](https://docs.docker.com/get-docker/)

```bash
docker compose up --build
```

## Usage

Run `poe` to see all available tasks.
{% if cookiecutter.with_fastapi_api|int %}
### API
{%- if cookiecutter.with_fastapi_api|int %}

```bash
poe api --dev
```

Access the API at [localhost:8000](http://localhost:8000) and the docs at [localhost:8000/docs](http://localhost:8000/docs).
{%- endif %}
{% endif %}
{%- if cookiecutter.with_typer_cli|int %}

### CLI

```bash
poetry run {{ cookiecutter.__project_name_kebab_case }} info
poetry run {{ cookiecutter.__project_name_kebab_case }} config
{%- if cookiecutter.with_fastapi_api|int %}
poetry run {{ cookiecutter.__project_name_kebab_case }} health
{%- endif %}
```
{%- endif %}

### Common tasks

```bash
poe test          # run tests
poe lint          # run linting
poe docs --serve  # serve documentation locally
```

## Project structure

```
{{ cookiecutter.__project_name_kebab_case }}/
├── src/{{ cookiecutter.__project_name_snake_case }}/  # source code
│   ├── settings.py                                    # pydantic-settings config
{%- if cookiecutter.with_fastapi_api|int %}
│   ├── api.py                                         # FastAPI application
{%- endif %}
{%- if cookiecutter.with_typer_cli|int %}
│   ├── cli.py                                         # Typer CLI
{%- endif %}
│   ├── models.py                                      # Pydantic models
│   └── services.py                                    # business logic
├── tests/                                             # test suite
├── docs/                                              # MkDocs + ADRs
├── pyproject.toml                                     # Poetry config
├── Dockerfile                                         # production image
└── docker-compose.yml                                 # local development
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
