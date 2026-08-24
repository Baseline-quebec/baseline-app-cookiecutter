"""Chatbot: a Pydantic AI agent exposed over a streaming HTTP endpoint."""

from {{ cookiecutter.__project_name_snake_case }}.chat.agent import ChatDeps, build_agent, build_model
from {{ cookiecutter.__project_name_snake_case }}.chat.event_sender import EventSender, wait_for_pending_events
from {{ cookiecutter.__project_name_snake_case }}.chat.history import (
    ConversationStore,
    InMemoryConversationStore,
)
from {{ cookiecutter.__project_name_snake_case }}.chat.service import ChatService


__all__ = [
    "ChatDeps",
    "ChatService",
    "ConversationStore",
    "EventSender",
    "InMemoryConversationStore",
    "build_agent",
    "build_model",
    "wait_for_pending_events",
]
