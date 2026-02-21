"""{{ cookiecutter.project_name }} CLI."""

from typing import Annotated

import typer
from rich import print  # noqa: A004
from rich.table import Table

from {{ cookiecutter.__project_name_snake_case }}.settings import settings


app = typer.Typer(help="{{ cookiecutter.project_name }} command-line interface.")


@app.callback()
def main(
    ctx: typer.Context,
    verbose: Annotated[  # noqa: FBT002
        bool, typer.Option("--verbose", "-v", help="Enable verbose output.")
    ] = False,
) -> None:
    """{{ cookiecutter.project_name }} CLI."""
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose


@app.command()
def info(ctx: typer.Context) -> None:
    """Display project metadata."""
    table = Table(title="{{ cookiecutter.project_name }}")
    table.add_column("Key", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("App name", settings.app_name)
    table.add_row("Log level", settings.log_level)
    table.add_row("Debug", str(settings.debug))
    if ctx.obj.get("verbose"):
        table.add_row("Settings class", type(settings).__name__)
    print(table)


@app.command()
def greet(
    name: Annotated[str, typer.Argument(help="Name to greet.")],
    ctx: typer.Context = None,  # type: ignore[assignment]
) -> None:
    """Greet someone by name."""
    if ctx and ctx.obj.get("verbose"):
        print(f"[dim]Greeting {name}...[/dim]")
    print(f"[bold green]Hello, {name}![/bold green]")
