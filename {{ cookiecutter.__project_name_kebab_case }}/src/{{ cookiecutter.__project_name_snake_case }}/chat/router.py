"""Chat HTTP routes."""

from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from pydantic_ai.messages import ModelMessage, TextPart, UserPromptPart
from sse_starlette import EventSourceResponse, ServerSentEvent

from {{ cookiecutter.__project_name_snake_case }}.chat.agent import build_agent
from {{ cookiecutter.__project_name_snake_case }}.chat.event_sender import EventSender, wait_for_pending_events
from {{ cookiecutter.__project_name_snake_case }}.chat.events import ChatEvent
from {{ cookiecutter.__project_name_snake_case }}.chat.history import (
    ConversationStore,
    InMemoryConversationStore,
)
from {{ cookiecutter.__project_name_snake_case }}.chat.service import ChatService


class ChatRequest(BaseModel):
    """A message sent by the user."""

    message: str = Field(min_length=1, max_length=10_000, description="The user's message")
    user_name: str | None = Field(default=None, description="Display name, if known")


class ChatMessage(BaseModel):
    """One turn of a conversation, flattened for display."""

    role: str = Field(description="Either 'user' or 'assistant'")
    content: str = Field(description="The message text")


class ChatHistoryResponse(BaseModel):
    """The visible transcript of a conversation."""

    conversation_id: str
    messages: list[ChatMessage]


# --- Dependency injection --------------------------------------------------------

_store = InMemoryConversationStore()
_service: ChatService | None = None


def get_conversation_store() -> ConversationStore:
    """Provide the shared conversation store."""
    return _store


def get_chat_service() -> ChatService:
    """Provide the shared ChatService, building the agent on first use.

    Construction is deferred so that importing this module does not require an
    API key. Tests override this dependency with a service built on a test model.
    """
    global _service  # noqa: PLW0603
    if _service is None:
        _service = ChatService(build_agent(), get_conversation_store())
    return _service


async def shutdown_chat() -> None:
    """Let in-flight agent runs finish before the app goes away.

    A run outlives the HTTP response that started it, so without this a turn in
    progress would be lost on shutdown.
    """
    await wait_for_pending_events()


ChatServiceDep = Annotated[ChatService, Depends(get_chat_service)]
ConversationStoreDep = Annotated[ConversationStore, Depends(get_conversation_store)]

chat_router = APIRouter(prefix="/chat", tags=["chat"])


# --- Routes ----------------------------------------------------------------------


def adapt_to_server_sent_event(event: ChatEvent) -> ServerSentEvent:
    """Adapt a domain event to a Server-Sent Event named after its `type`.

    Args:
        event: The transport-agnostic event to adapt.

    Returns:
        The equivalent ServerSentEvent.
    """
    return ServerSentEvent(event=event.type, data=event.model_dump_json())


@chat_router.post("/{conversation_id}")
async def send_message(
    conversation_id: str, data: ChatRequest, service: ChatServiceDep
) -> EventSourceResponse:
    """Send a message and stream the reply.

    This is a POST that returns an SSE stream, so it is not consumable by the
    browser `EventSource` API (which can only issue GETs). Clients should read
    the body incrementally with `fetch`.
    """
    event_sender = EventSender[ServerSentEvent](event_type_adapter=adapt_to_server_sent_event)
    return EventSourceResponse(
        event_sender.execute(
            service.respond(event_sender, conversation_id, data.message, user_name=data.user_name)
        )
    )


@chat_router.get("/{conversation_id}")
async def get_history(conversation_id: str, store: ConversationStoreDep) -> ChatHistoryResponse:
    """Return the visible transcript of a conversation."""
    messages = await store.load(conversation_id)
    return ChatHistoryResponse(
        conversation_id=conversation_id, messages=_visible_messages(messages)
    )


def _visible_messages(messages: list[ModelMessage]) -> list[ChatMessage]:
    """Project the stored history down to what a user should see.

    Tool calls and tool returns are deliberately dropped here: they are kept in
    the store so the model can reason over them on later turns, but they are not
    part of the transcript.
    """
    visible: list[ChatMessage] = []
    for message in messages:
        for part in message.parts:
            match part:
                case UserPromptPart(content=str() as text):
                    visible.append(ChatMessage(role="user", content=text))
                case TextPart(content=text) if text:
                    visible.append(ChatMessage(role="assistant", content=text))
                case _:
                    pass
    return visible
