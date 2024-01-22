from __future__ import annotations

import abc
from typing import TYPE_CHECKING, Awaitable, Callable

if TYPE_CHECKING:
    from .packet import Packet

type Coro[**P, R] = Callable[P, Awaitable[R]]
type Write = Coro[[bytes], None]
type Read = Coro[[int], bytes]


class Protocol(abc.ABC):
    async def send(self, write: Write, packet: Packet) -> None:
        ...

    async def read(self, read: Read) -> Packet:
        ...
