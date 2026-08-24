"""Pydantic AI agent used by the chat endpoint."""

from dataclasses import dataclass
from datetime import UTC, datetime

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from {{ cookiecutter.__project_name_snake_case }}.settings import Settings


@dataclass(frozen=True, slots=True)
class ChatDeps:
    """Per-request context injected into tools via `RunContext`.

    Keep this small and immutable: it is the only channel between the request
    and the agent's tools. Shared collaborators (repositories, HTTP clients)
    belong on the tool objects themselves, not here.
    """

    conversation_id: str
    user_name: str | None = None


def build_model(app_settings: Settings) -> Model:
    """Build the chat model from the given settings.

    Settings arrive as an argument rather than being read from the module-level
    singleton, so the container decides what this is configured with.

    The provider package is imported lazily so that importing this module (for
    example during test collection) does not require an API key or the
    `anthropic` extra to be installed.

    Args:
        app_settings: Supplies the model name, token budget, and API key.
    """
    from pydantic_ai.models.anthropic import AnthropicModel, AnthropicModelSettings
    from pydantic_ai.providers.anthropic import AnthropicProvider

    return AnthropicModel(
        app_settings.chat_model,
        provider=AnthropicProvider(api_key=app_settings.anthropic_api_key),
        settings=AnthropicModelSettings(
            max_tokens=app_settings.chat_max_tokens,
            # Cache the static prefix: tool schemas render first, then the
            # instructions. Cache reads cost about a tenth of base input price,
            # and the whole prefix is re-sent on every tool round-trip, so this
            # is the highest-leverage setting in this file. It only works while
            # the prefix stays byte-identical, which is why the instructions are
            # a fixed string and per-request context is exposed through tools.
            anthropic_cache_tool_definitions=True,
            anthropic_cache_instructions=True,
        ),
    )


def build_agent(app_settings: Settings, model: Model | None = None) -> Agent[ChatDeps, str]:
    """Build the chat agent, optionally against an injected model.

    Tests pass `pydantic_ai.models.test.TestModel` (or `FunctionModel`) here so
    the suite never makes a network call and needs no API key.

    Args:
        app_settings: Supplies the instructions, and the model when none is given.
        model: Overrides the model built from settings. Tests use this.
    """
    agent = Agent(
        model if model is not None else build_model(app_settings),
        deps_type=ChatDeps,
        # A fixed string, not a callable: dynamic instructions would change the
        # cached prefix on every request. Put volatile context in a tool.
        instructions=app_settings.chat_system_prompt,
        retries=2,
    )

    @agent.tool_plain
    def current_utc_time() -> str:
        """Return the current date and time in UTC, ISO-8601 formatted."""
        return datetime.now(UTC).isoformat()

    @agent.tool
    def who_am_i(ctx: RunContext[ChatDeps]) -> str:
        """Return the display name of the person you are talking to."""
        return ctx.deps.user_name or "unknown"

    return agent
