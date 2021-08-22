import asyncio
from dataclasses import dataclass
from enum import Enum, unique
from functools import cached_property
from typing import Any, Callable, Coroutine, Optional, TYPE_CHECKING, Union


if TYPE_CHECKING:
    from phx_events.channels_client import PHXChannelsClient


Topic = str
Event = str
ChannelEvent = Union['PHXEvent', Event]
ChannelMessage = Union['PHXMessage', 'PHXEventMessage']

EventHandlerFunction = Callable[['PHXMessage', 'PHXChannelsClient'], Coroutine[Any, Any, None]]
PHXEventHandlerFunction = Callable[['PHXEventMessage', 'PHXChannelsClient'], Coroutine[Any, Any, None]]
ChannelHandlerFunction = Union[EventHandlerFunction, PHXEventHandlerFunction]


@dataclass()
class EventHandlerConfig:
    queue: asyncio.Queue[ChannelMessage]
    default_handlers: list[ChannelHandlerFunction]
    topic_handlers: dict[Topic, list[ChannelHandlerFunction]]
    task: asyncio.Task[None]


@unique
class PHXEvent(Enum):
    close = 'phx_close'
    error = 'phx_error'
    join = 'phx_join'
    reply = 'phx_reply'
    leave = 'phx_leave'

    # hack for typing
    value: str

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True)
class BasePHXMessage:
    topic: Topic
    ref: Optional[str]
    payload: dict[str, Any]

    @cached_property
    def subtopic(self):
        if ':' not in self.topic:
            return None

        _, subtopic = self.topic.split(':', 1)
        return subtopic


@dataclass(frozen=True)
class PHXMessage(BasePHXMessage):
    event: Event


@dataclass(frozen=True)
class PHXEventMessage(BasePHXMessage):
    event: PHXEvent
