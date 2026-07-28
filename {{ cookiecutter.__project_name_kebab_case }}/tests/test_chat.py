"""Tests for the chatbot.

Every test here is hermetic: the model is a Pydantic AI test double, so the
suite needs no API key and makes no network call.
"""

from collections.abc import AsyncIterator, Iterator
from http import HTTPStatus

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from pydantic_ai.messages import ModelMessage, ModelResponse
from pydantic_ai.models.function import AgentInfo, FunctionModel
from pydantic_ai.models.test import TestModel

from {{ cookiecutter.__project_name_snake_case }}.api import app
from {{ cookiecutter.__project_name_snake_case }}.chat.agent import build_agent
from {{ cookiecutter.__project_name_snake_case }}.chat.event_sender import EventSender, wait_for_pending_events
from {{ cookiecutter.__project_name_snake_case }}.chat.events import ChatEvent
from {{ cookiecutter.__project_name_snake_case }}.chat.history import InMemoryConversationStore
from {{ cookiecutter.__project_name_snake_case }}.chat.router import (
    get_chat_service,
    get_conversation_store,
)
from {{ cookiecutter.__project_name_snake_case }}.chat.service import ChatService


REPLY = "Hello there"
# How many events to read before simulating a client hanging up.
EVENTS_BEFORE_DISCONNECT = 2


@pytest.fixture
def store() -> InMemoryConversationStore:
    """Provide a fresh in-memory conversation store."""
    return InMemoryConversationStore()


@pytest.fixture
def service(store: InMemoryConversationStore) -> ChatService:
    """Provide a ChatService backed by a deterministic model."""
    return ChatService(build_agent(TestModel(custom_output_text=REPLY)), store)


@pytest.fixture
def chat_app(store: InMemoryConversationStore, service: ChatService) -> Iterator[FastAPI]:
    """Provide the API with the chat dependencies overridden.

    Yields:
        The FastAPI app, with overrides cleared afterwards.
    """
    app.dependency_overrides[get_chat_service] = lambda: service
    app.dependency_overrides[get_conversation_store] = lambda: store
    yield app
    app.dependency_overrides.clear()


def _identity(event: ChatEvent) -> ChatEvent:
    """Pass domain events through unchanged, so tests assert on them directly."""
    return event


def open_stream(
    service: ChatService, conversation_id: str, message: str
) -> AsyncIterator[ChatEvent]:
    """Start a turn and return its event stream, as the route does."""
    sender = EventSender[ChatEvent](event_type_adapter=_identity)
    return sender.execute(service.respond(sender, conversation_id, message))


async def drain(service: ChatService, conversation_id: str, message: str) -> list[ChatEvent]:
    """Run one turn to completion and collect every event."""
    return [event async for event in open_stream(service, conversation_id, message)]


async def test_service_streams_text(service: ChatService) -> None:
    """The text stream reassembles to the model's full reply."""
    events = await drain(service, "c1", "hi")
    types = [event.type for event in events]

    assert "text_start" in types
    assert "text_chunk" in types
    end = next(event for event in events if event.type == "text_end")
    assert end.content == REPLY


async def test_service_emits_tool_events(service: ChatService) -> None:
    """Tool calls surface as start and end events, in order."""
    types = [event.type for event in await drain(service, "c1", "what time is it")]

    assert types.index("tool_call_start") < types.index("tool_call_end")


async def test_history_keeps_tool_calls(
    service: ChatService, store: InMemoryConversationStore
) -> None:
    """Persisted history retains tool calls and returns, not only the reply.

    This is what lets the model reason about earlier retrievals on later turns.
    """
    await drain(service, "c1", "hi")
    messages = await store.load("c1")
    parts = {type(part).__name__ for message in messages for part in message.parts}

    assert {"ToolCallPart", "ToolReturnPart", "TextPart"} <= parts


async def test_history_accumulates_across_turns(
    service: ChatService, store: InMemoryConversationStore
) -> None:
    """Each turn appends to the conversation rather than replacing it."""
    await drain(service, "c1", "first")
    after_first = len(await store.load("c1"))
    await drain(service, "c1", "second")

    assert len(await store.load("c1")) > after_first


async def test_conversations_are_isolated(service: ChatService) -> None:
    """Two conversation ids do not share history."""
    await drain(service, "c1", "hi")
    events = await drain(service, "c2", "hi")

    assert any(event.type == "text_end" for event in events)


async def test_model_failure_yields_error_event(store: InMemoryConversationStore) -> None:
    """A failing model ends the stream with an error event instead of raising."""
    message = "model exploded"

    def explode(_messages: list[ModelMessage], _info: AgentInfo) -> ModelResponse:
        raise RuntimeError(message)

    failing = ChatService(build_agent(FunctionModel(explode)), store)
    events = await drain(failing, "c1", "hi")

    assert events[-1].type == "error"
    assert await store.load("c1") == []


async def test_disconnect_still_persists_the_turn(
    service: ChatService, store: InMemoryConversationStore
) -> None:
    """A client that hangs up mid-reply does not lose the exchange.

    The agent run lives in its own task, so abandoning the event stream (which is
    what happens when a browser tab closes) lets the run finish and write to the
    store. Consuming events directly from a generator would drop the turn.
    """
    stream = open_stream(service, "c1", "hi")
    seen = 0
    async for _event in stream:
        seen += 1
        if seen == EVENTS_BEFORE_DISCONNECT:
            break
    await stream.aclose()
    await wait_for_pending_events()

    assert seen == EVENTS_BEFORE_DISCONNECT
    assert await store.load("c1") != []


async def test_disconnect_does_not_raise_cancel_scope_error(service: ChatService) -> None:
    """Tearing down the stream early is clean.

    `Agent.iter` owns an anyio cancel scope. Yielding while it is open makes anyio
    raise "Attempted to exit cancel scope in a different task"; pushing events
    from a dedicated task does not.
    """
    stream = open_stream(service, "c1", "hi")
    async for _event in stream:
        break
    await stream.aclose()
    await wait_for_pending_events()


async def test_chat_endpoint_streams_sse(chat_app: FastAPI) -> None:
    """POST /chat/{id} returns an event stream carrying the reply."""
    async with AsyncClient(
        transport=ASGITransport(app=chat_app), base_url="http://test"
    ) as client:
        response = await client.post("/chat/c1", json={"message": "hi"})

    assert response.status_code == HTTPStatus.OK
    assert "text/event-stream" in response.headers["content-type"]
    assert "event: text_chunk" in response.text


async def test_history_endpoint_returns_transcript(chat_app: FastAPI) -> None:
    """GET /chat/{id} returns the user and assistant turns, without tool noise."""
    async with AsyncClient(
        transport=ASGITransport(app=chat_app), base_url="http://test"
    ) as client:
        await client.post("/chat/c1", json={"message": "hi"})
        response = await client.get("/chat/c1")

    assert response.status_code == HTTPStatus.OK
    messages = response.json()["messages"]
    assert [message["role"] for message in messages] == ["user", "assistant"]
    assert messages[0]["content"] == "hi"
    assert messages[1]["content"] == REPLY


async def test_empty_message_is_rejected(chat_app: FastAPI) -> None:
    """An empty message fails validation."""
    async with AsyncClient(
        transport=ASGITransport(app=chat_app), base_url="http://test"
    ) as client:
        response = await client.post("/chat/c1", json={"message": ""})

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
