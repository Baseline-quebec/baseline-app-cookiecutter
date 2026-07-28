"""Chat orchestration: load history, stream a reply, persist the result.

`respond` is a producer in the sense described in `event_sender.py`: it takes an
`EventSender`, pushes events as they happen, and returns nothing. It is run as a
background task by `EventSender.execute`, which also closes the stream.
"""

import json
from typing import Any

from loguru import logger
from pydantic_ai import Agent, CallToolsNode, ModelRequestNode
from pydantic_ai.agent import AgentRun
from pydantic_ai.messages import (
    FunctionToolCallEvent,
    FunctionToolResultEvent,
    ModelMessage,
    PartDeltaEvent,
    PartStartEvent,
    TextPart,
    TextPartDelta,
    ThinkingPartDelta,
)
from pydantic_graph import End

from {{ cookiecutter.__project_name_snake_case }}.chat.agent import ChatDeps
from {{ cookiecutter.__project_name_snake_case }}.chat.event_sender import EventSender
from {{ cookiecutter.__project_name_snake_case }}.chat.events import (
    ChatError,
    ReasoningChunk,
    TextChunk,
    TextStreamEnd,
    TextStreamStart,
    ToolCallEnd,
    ToolCallStart,
)
from {{ cookiecutter.__project_name_snake_case }}.chat.history import ConversationStore


class ChatService:
    """Answers user messages with an agent, one run per message."""

    def __init__(self, agent: Agent[ChatDeps, str], store: ConversationStore) -> None:
        """Store the agent and the conversation history backend."""
        self._agent = agent
        self._store = store

    async def respond(
        self,
        event_sender: EventSender[Any],
        conversation_id: str,
        user_message: str,
        *,
        user_name: str | None = None,
    ) -> None:
        """Answer `user_message`, streaming progress and persisting the exchange.

        Args:
            event_sender: Receives text, reasoning and tool-call events.
            conversation_id: Identifies the conversation to continue.
            user_message: The message to answer.
            user_name: Display name of the sender, if known.
        """
        try:
            await self._run_and_store(event_sender, conversation_id, user_message, user_name)
        except Exception as exc:  # noqa: BLE001 — report to the client, don't break the stream
            # Response headers are already sent, so raising would drop the
            # connection with no explanation. Send a terminal event instead.
            logger.exception("Chat run failed for conversation {}", conversation_id)
            await event_sender.send_event(
                ChatError(message=f"The assistant could not reply: {exc}")
            )

    async def _run_and_store(
        self,
        event_sender: EventSender[Any],
        conversation_id: str,
        user_message: str,
        user_name: str | None,
    ) -> None:
        """Step the agent graph to completion and persist what it produced."""
        history = await self._store.load(conversation_id)
        deps = ChatDeps(conversation_id=conversation_id, user_name=user_name)
        new_messages: list[ModelMessage] = []

        async with self._agent.iter(user_message, message_history=history, deps=deps) as run:
            node = run.next_node
            while not isinstance(node, End):
                if isinstance(node, ModelRequestNode):
                    await _send_text(node, run, event_sender)
                elif isinstance(node, CallToolsNode):
                    await _send_tool_calls(node, run, event_sender)
                node = await run.next(node)
            if run.result is not None:
                new_messages = run.result.new_messages()

        await self._store.append(conversation_id, new_messages)


async def _send_text(
    node: ModelRequestNode[ChatDeps, Any],
    run: AgentRun[ChatDeps, Any],
    event_sender: EventSender[Any],
) -> None:
    """Send text and reasoning events for one model request."""
    started = False
    chunks: list[str] = []

    async with node.stream(run.ctx) as stream:
        async for event in stream:
            match event:
                case PartDeltaEvent(delta=ThinkingPartDelta(content_delta=text)) if text:
                    await event_sender.send_event(ReasoningChunk(chunk=text))
                case (
                    PartDeltaEvent(delta=TextPartDelta(content_delta=text))
                    | PartStartEvent(part=TextPart(content=text))
                ) if text:
                    if not started:
                        started = True
                        await event_sender.send_event(TextStreamStart())
                    chunks.append(text)
                    await event_sender.send_event(TextChunk(chunk=text))
                case _:
                    pass

    if started:
        await event_sender.send_event(TextStreamEnd(content="".join(chunks)))


async def _send_tool_calls(
    node: CallToolsNode[ChatDeps, Any],
    run: AgentRun[ChatDeps, Any],
    event_sender: EventSender[Any],
) -> None:
    """Send start and end events for each tool the model invoked."""
    async with node.stream(run.ctx) as stream:
        async for event in stream:
            match event:
                case FunctionToolCallEvent():
                    await event_sender.send_event(
                        ToolCallStart(
                            tool_name=event.part.tool_name,
                            tool_call_id=event.part.tool_call_id or "",
                            args=_as_dict(event.part.args),
                        )
                    )
                case FunctionToolResultEvent():
                    # `part` is a ToolReturnPart on success and a RetryPromptPart
                    # when the model has to be asked again; both carry the name.
                    await event_sender.send_event(
                        ToolCallEnd(
                            tool_name=event.part.tool_name or "",
                            tool_call_id=event.part.tool_call_id or "",
                        )
                    )
                case _:
                    pass


def _as_dict(args: str | dict[str, Any] | None) -> dict[str, Any]:
    """Coerce tool-call arguments to a dict.

    Providers differ: some stream arguments as a JSON string, others hand back a
    parsed object. Never string-match the serialized form.
    """
    if args is None:
        return {}
    if isinstance(args, str):
        try:
            parsed = json.loads(args)
        except json.JSONDecodeError:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return args
