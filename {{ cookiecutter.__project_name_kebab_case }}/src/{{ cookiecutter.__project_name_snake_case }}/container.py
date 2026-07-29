"""Dishka dependency injection container.

Every collaborator the API needs is built here, once, at `Scope.APP`. Routes ask
for what they need with `FromDishka[...]` and never construct anything
themselves, which is what makes them testable: a test swaps the container and no
real client is ever created.

Providers that own a connection should `yield` it rather than `return` it, so
dishka closes it when the app shuts down:

    @provide
    @staticmethod
    async def provide_client(app_settings: Settings) -> AsyncIterable[Client]:
        client = Client(app_settings.some_url)
        yield client
        await client.close()
"""

from dishka import AsyncContainer, Provider, Scope, make_async_container, provide
{%- if cookiecutter.with_chatbot|int %}
from pydantic_ai import Agent
from pydantic_ai.models import Model
{%- endif %}

{% if cookiecutter.with_chatbot|int -%}
from {{ cookiecutter.__project_name_snake_case }}.chat.agent import ChatDeps, build_agent, build_model
from {{ cookiecutter.__project_name_snake_case }}.chat.history import (
    ConversationStore,
    InMemoryConversationStore,
)
from {{ cookiecutter.__project_name_snake_case }}.chat.service import ChatService
{% endif -%}
from {{ cookiecutter.__project_name_snake_case }}.services import ItemService
from {{ cookiecutter.__project_name_snake_case }}.settings import Settings, settings


class ConfigProvider(Provider):
    """Provides the application settings."""

    scope = Scope.APP

    @provide
    @staticmethod
    def provide_settings() -> Settings:
        """Return the application settings loaded from the environment and `.env`."""
        return settings


class CoreProvider(Provider):
    """Provides the domain services.

    This is where a new service goes as the project grows: add a `@provide`
    method returning it, then ask for it in a route with `FromDishka[...]`.
    Infrastructure adapters (database clients, HTTP clients) belong in a separate
    `InfraProvider` so the layers stay visible.
    """

    scope = Scope.APP

    @provide
    @staticmethod
    def provide_item_service() -> ItemService:
        """Create the item service.

        `Scope.APP` means one instance for the whole application, which is what
        the in-memory store needs to keep items between requests. A service that
        holds per-request state would use `Scope.REQUEST` instead.
        """
        return ItemService()
{%- if cookiecutter.with_chatbot|int %}

    @provide
    @staticmethod
    def provide_model(app_settings: Settings) -> Model:
        """Create the Pydantic AI model backing the chat agent."""
        return build_model(app_settings)

    @provide
    @staticmethod
    def provide_agent(app_settings: Settings, model: Model) -> Agent[ChatDeps, str]:
        """Create the chat agent against the injected model."""
        return build_agent(app_settings, model)

    @provide
    @staticmethod
    def provide_conversation_store() -> ConversationStore:
        """Create the conversation history backend.

        Returns the in-memory implementation. Point this at a database and every
        caller follows, because they all depend on the `ConversationStore`
        protocol rather than on this class.
        """
        return InMemoryConversationStore()

    @provide
    @staticmethod
    def provide_chat_service(agent: Agent[ChatDeps, str], store: ConversationStore) -> ChatService:
        """Create the chat service with all injected dependencies."""
        return ChatService(agent=agent, store=store)
{%- endif %}


def make_container() -> AsyncContainer:
    """Create the dishka async container with all providers."""
    return make_async_container(
        ConfigProvider(),
        CoreProvider(),
    )
