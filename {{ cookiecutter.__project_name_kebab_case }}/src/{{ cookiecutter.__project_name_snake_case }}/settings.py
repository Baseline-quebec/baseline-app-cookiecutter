"""{{ cookiecutter.project_name }} settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "{{ cookiecutter.project_name }}"
    log_level: str = "INFO"
    debug: bool = False
{%- if cookiecutter.with_fastapi_api|int %}
    api_host: str = "0.0.0.0"  # noqa: S104
    api_port: int = 8000
{%- endif %}
{%- if cookiecutter.with_sentry|int %}
    sentry_dsn: str = ""
    sentry_environment: str = "development"
    sentry_traces_sample_rate: float = 0.1
{%- endif %}


settings = Settings()
