"""Stream events from a background producer to an HTTP response.

A producer (typically a service method) is run as its own task and pushes events
into a queue that the response drains. That indirection is what makes streaming
correct rather than merely convenient:

- **Correct cancellation.** `Agent.iter` owns an anyio cancel scope. An async
  generator that yields while that scope is open can be finalized from a
  different task than the one that entered it, and anyio then raises "Attempted
  to exit cancel scope in a different task than it was entered in". Pushing from
  a dedicated task keeps the scope entered and exited in one place.
- **Durable turns.** When a client disconnects mid-reply the producer keeps
  running, so whatever it persists still lands. A plain generator would be closed
  at its current `yield` and the turn would be lost.

The cost is that a disconnected client still pays for the rest of the run. That
is usually the right trade, since the result is saved and a reload shows it
complete. Call `cancel()` from the producer's owner if you would rather stop.
"""

import asyncio
from collections.abc import AsyncIterator, Callable, Coroutine

from loguru import logger

from {{ cookiecutter.__project_name_snake_case }}.chat.events import ChatEvent


class _Sentinel:
    """Marks the end of the stream."""


_END_OF_STREAM = _Sentinel()

_QueueItem = ChatEvent | _Sentinel | BaseException

# Tasks in flight across all senders, so shutdown can wait for them. asyncio only
# holds weak references to running tasks, so this also keeps them alive.
_in_flight: set[asyncio.Task[None]] = set()


async def wait_for_pending_events() -> None:
    """Wait for in-flight producers to finish.

    Call this on application shutdown so a turn in progress is still persisted
    instead of being dropped along with the process.
    """
    # Filter out finished tasks rather than looping on `_in_flight` itself:
    # awaiting an already-done future does not yield to the event loop, so
    # re-checking a set that is only emptied by done-callbacks would spin
    # forever without ever letting those callbacks run.
    while pending := {task for task in _in_flight if not task.done()}:
        # `asyncio.wait` leaves the tasks running if this waiter is itself
        # canceled; `gather` would cancel the producers, which is the opposite
        # of what a graceful shutdown wants.
        await asyncio.wait(pending)
        await asyncio.sleep(0)  # let done-callbacks queue any follow-up work


class EventSender[T]:
    """Adapts a pushed event stream into an async iterator of wire values.

    The producer calls `send_event`; the response iterates. `T` is the transport
    type, produced by `event_type_adapter` (for example a `ServerSentEvent`).
    """

    def __init__(self, event_type_adapter: Callable[[ChatEvent], T]) -> None:
        """Store the adapter and create the queue.

        Args:
            event_type_adapter: Converts each domain event to the wire type.
        """
        self._queue: asyncio.Queue[_QueueItem] = asyncio.Queue()
        self._event_type_adapter = event_type_adapter
        self._closed = False
        self._background_task: asyncio.Task[None] | None = None

    async def send_event(self, event: ChatEvent) -> None:
        """Push an event to the stream.

        Args:
            event: The domain event to send.
        """
        if self._closed:
            logger.warning("Dropped {} sent to a closed EventSender", event.type)
            return
        await self._queue.put(event)

    async def close(self, error: BaseException | None = None) -> None:
        """Stop accepting events and unblock the iterator.

        Args:
            error: If given, re-raised from the iterator after the last event.
        """
        self._closed = True
        if error is not None:
            await self._queue.put(error)
        await self._queue.put(_END_OF_STREAM)

    def cancel(self) -> bool:
        """Stop the producer early. Returns True if a task was canceled."""
        if self._background_task is not None and not self._background_task.done():
            return self._background_task.cancel()
        return False

    async def __aiter__(self) -> AsyncIterator[T]:
        """Yield adapted events from the queue until the stream closes.

        Yields:
            One wire value per domain event, in the order they were sent.
        """
        while True:
            item = await self._queue.get()
            if isinstance(item, BaseException):
                raise item
            if isinstance(item, _Sentinel):
                return
            yield self._event_type_adapter(item)

    def execute(self, coroutine: Coroutine[None, None, None]) -> AsyncIterator[T]:
        """Run `coroutine` as a background task and return the event stream.

        The stream is always closed once the task ends, however it ends, and a
        task exception is re-raised from the iterator rather than swallowed.

        Args:
            coroutine: The producing coroutine — typically a service method that
                takes this sender and calls `send_event`.

        Returns:
            The adapted async iterator of events.
        """
        task = asyncio.create_task(coroutine)
        self._background_task = task
        _in_flight.add(task)
        task.add_done_callback(_in_flight.discard)
        task.add_done_callback(self._on_task_done)
        return aiter(self)

    def _on_task_done(self, task: asyncio.Task[None]) -> None:
        """Close the stream when the producer ends, forwarding any exception."""
        if task.cancelled():
            self._schedule_close(None)
            return

        error = task.exception()
        if error is not None:
            logger.opt(exception=error).error("EventSender background task failed")
        self._schedule_close(error)

    def _schedule_close(self, error: BaseException | None) -> None:
        """Close the stream from a done-callback, where awaiting is not possible."""
        close_task = asyncio.ensure_future(self.close(error))
        _in_flight.add(close_task)
        close_task.add_done_callback(_in_flight.discard)
