# ruff: noqa: DOC201
"""API module for the application."""

from fastapi import FastAPI

from app.v1.api import app as v0_app


app = FastAPI(title="{{ cookiecutter.__project_name }}", version="0.1.0")

app.mount("/v0", v0_app)


@app.get("/", include_in_schema=False)
def root() -> str:
    """Latest documentation available at v0/docs."""
    return "Bienvenue sur l'API de {{ cookiecutter.__project_name }}! La documentation la plus récente est disponible à /v1/docs."


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=8000, log_level="info")
