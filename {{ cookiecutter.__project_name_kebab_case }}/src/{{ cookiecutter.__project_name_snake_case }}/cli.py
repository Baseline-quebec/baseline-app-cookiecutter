"""{{ cookiecutter.project_name }} CLI."""

{% if cookiecutter.with_fastapi_api|int -%}
import urllib.request
{% endif -%}
from typing import Annotated

import typer
from rich import print  # noqa: A004
from rich.table import Table

from {{ cookiecutter.__project_name_snake_case }}.settings import Settings, settings


app = typer.Typer(help="{{ cookiecutter.project_name }} command-line interface.")

_verbose: bool = False


@app.callback()
def main(
    verbose: Annotated[  # noqa: FBT002
        bool, typer.Option("--verbose", "-v", help="Enable verbose output.")
    ] = False,
) -> None:
    """{{ cookiecutter.project_name }} CLI."""
    global _verbose  # noqa: PLW0603
    _verbose = verbose


@app.command()
def info() -> None:
    """Display project metadata."""
    table = Table(title="{{ cookiecutter.project_name }}")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("App name", settings.app_name)
    table.add_row("Log level", settings.log_level)
    table.add_row("Debug", str(settings.debug))
    if _verbose:
        table.add_row("Settings class", type(settings).__name__)
    print(table)


@app.command()
def config() -> None:
    """Print current settings from environment and .env file."""
    table = Table(title="Settings")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    for field_name in Settings.model_fields:
        value = getattr(settings, field_name)
        if _verbose or field_name != "sentry_dsn":
            table.add_row(field_name, str(value))
    print(table)
{%- if cookiecutter.with_fastapi_api|int %}


@app.command()
def health() -> None:
    """Check the API health endpoint."""
    url = f"http://{settings.api_host}:{settings.api_port}/health"
    if _verbose:
        print(f"[dim]Checking {url}...[/dim]")
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            data = response.read().decode()
            print(f"[bold green]API is healthy:[/bold green] {data}")
    except Exception as exc:
        print(f"[bold red]API is unreachable:[/bold red] {exc}")
        raise typer.Exit(code=1) from exc
{%- endif %}
