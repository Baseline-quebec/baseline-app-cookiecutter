"""Domain events emitted while the agent produces a reply.

These are transport-agnostic: `router.py` serializes them to Server-Sent Events,
but a WebSocket handler or a CLI renderer could consume the same stream. Each
event carries a literal `type` so the union is discriminated on the wire.
"""

from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field


class TextStreamStart(BaseModel):
    """The agent began writing a user-visible message."""

    type: Literal["text_start"] = "text_start"


class TextChunk(BaseModel):
    """An incremental piece of the agent's reply."""

    type: Literal["text_chunk"] = "text_chunk"
    chunk: str


class TextStreamEnd(BaseModel):
    """The agent finished a message. Carries the reassembled full text."""

    type: Literal["text_end"] = "text_end"
    content: str


class ReasoningChunk(BaseModel):
    """An incremental piece of the agent's reasoning.

    Only produced when the model is configured to return thinking content. On
    Anthropic models that means setting `anthropic_thinking` with
    `display="summarized"`; the default omits reasoning text entirely.
    """

    type: Literal["reasoning_chunk"] = "reasoning_chunk"
    chunk: str


class ToolCallStart(BaseModel):
    """The agent invoked a tool. Useful for rendering progress in a UI."""

    type: Literal["tool_call_start"] = "tool_call_start"
    tool_name: str
    tool_call_id: str
    args: dict[str, Any] = Field(default_factory=dict)


class ToolCallEnd(BaseModel):
    """A tool returned."""

    type: Literal["tool_call_end"] = "tool_call_end"
    tool_name: str
    tool_call_id: str


class ChatError(BaseModel):
    """The run failed. Terminal: no further events follow."""

    type: Literal["error"] = "error"
    message: str


ChatEvent = Annotated[
    TextStreamStart
    | TextChunk
    | TextStreamEnd
    | ReasoningChunk
    | ToolCallStart
    | ToolCallEnd
    | ChatError,
    Field(discriminator="type"),
]
