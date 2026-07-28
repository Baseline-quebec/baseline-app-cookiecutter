"""Conversation history persistence."""

from typing import Protocol

from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter


class ConversationStore(Protocol):
    """Stores the full Pydantic AI message history for a conversation."""

    async def load(self, conversation_id: str) -> list[ModelMessage]:
        """Return the stored history, oldest first, or an empty list."""
        ...

    async def append(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        """Append newly produced messages to the conversation."""
        ...


class InMemoryConversationStore:
    """Process-local, non-durable store. Swap for a database in production.

    History is serialized with `ModelMessagesTypeAdapter`, which round-trips
    tool calls and tool returns alongside plain text. Storing only the final
    assistant text is lossy in a way that is easy to miss: on the next turn the
    model has no record of what its own tools returned, only whatever it
    happened to say about them.

    Implementing `ConversationStore` against a real database means replacing the
    dict below; the (de)serialization is already handled here.
    """

    def __init__(self) -> None:
        """Initialize an empty store."""
        self._conversations: dict[str, bytes] = {}

    async def load(self, conversation_id: str) -> list[ModelMessage]:
        """Return the stored history, oldest first, or an empty list."""
        raw = self._conversations.get(conversation_id)
        if raw is None:
            return []
        return list(ModelMessagesTypeAdapter.validate_json(raw))

    async def append(self, conversation_id: str, messages: list[ModelMessage]) -> None:
        """Append newly produced messages to the conversation."""
        if not messages:
            return
        history = await self.load(conversation_id)
        history.extend(messages)
        self._conversations[conversation_id] = ModelMessagesTypeAdapter.dump_json(history)

    async def conversation_ids(self) -> list[str]:
        """Return the identifiers of every known conversation."""
        return list(self._conversations)
