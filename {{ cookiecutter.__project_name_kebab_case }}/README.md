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
- [uv](https://docs.astral.sh/uv/getting-started/installation/)

```bash
uv sync
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
{%- if cookiecutter.with_chatbot|int %}

### Chatbot

Set `ANTHROPIC_API_KEY` in `.env`, start the API, then send a message. The route
is a POST that returns a Server-Sent Event stream, so read it incrementally
rather than with the browser `EventSource` API:

```bash
curl -N -X POST localhost:8000/chat/my-conversation \
  -H 'Content-Type: application/json' \
  -d '{"message": "What time is it?"}'
```

Fetch the transcript of a conversation with `GET /chat/my-conversation`.

The agent lives in `src/{{ cookiecutter.__project_name_snake_case }}/chat/`. To adapt it:

- `agent.py` — the model, the system prompt, and the tools the agent can call.
- `history.py` — conversation persistence. The default store is in-memory and
  therefore lost on restart; implement `ConversationStore` against a database
  before deploying.
- `service.py` — translates an agent run into `ChatEvent`s.
- `router.py` — the HTTP surface.

Collaborators are wired in `src/{{ cookiecutter.__project_name_snake_case }}/container.py` with
[dishka](https://dishka.readthedocs.io/): routes declare `FromDishka[...]` under
`@inject` and construct nothing themselves. Add a service by adding a `@provide`
method there, then asking for it in a route.

Tests use Pydantic AI's `TestModel` and `FunctionModel` behind a stub container,
so `poe test` needs no API key and makes no network calls.
{%- endif %}
{%- if cookiecutter.with_typer_cli|int %}

### CLI

```bash
uv run {{ cookiecutter.__project_name_kebab_case }} info
uv run {{ cookiecutter.__project_name_kebab_case }} config
{%- if cookiecutter.with_fastapi_api|int %}
uv run {{ cookiecutter.__project_name_kebab_case }} health
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
{%- if cookiecutter.with_chatbot|int %}
│   ├── chat/                                          # Pydantic AI chatbot
│   ├── container.py                                   # dishka DI container
{%- endif %}
│   ├── models.py                                      # Pydantic models
│   └── services.py                                    # business logic
├── tests/                                             # test suite
├── docs/                                              # MkDocs + ADRs
├── pyproject.toml                                     # project config (uv)
├── Dockerfile                                         # production image
└── docker-compose.yml                                 # local development
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
