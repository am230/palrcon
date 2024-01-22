from __future__ import annotations

import asyncio
import struct
from typing import Optional

from ..executor import Executor
from ..packet import Packet, Type
from ..protocol import Protocol, Read, Write


class MCProtocol(Protocol):
    async def send(self, write: Write, packet: Packet) -> None:
        out_payload = (
            struct.pack("<ii", packet.id, packet.type.value)
            + packet.payload
            + b"\x00\x00"
        )
        out_length = struct.pack("<i", len(out_payload))
        await write(out_length + out_payload)

    async def read(self, read: Read) -> Packet:
        length = struct.unpack("<i", await read(4))[0]
        id, type = struct.unpack("<ii", await read(8))
        payload = await read(length - 10)
        terminator = await read(2)
        if terminator != b"\x00\x00":
            raise Exception(f"Unexpected terminator: {terminator=}")
        return Packet(id, Type(type), payload)


class MCRcon(Executor):
    def __init__(
        self,
        protocol: Protocol,
        writer: asyncio.StreamWriter,
        reader: asyncio.StreamReader,
    ):
        self._protocol = protocol
        self._writer = writer
        self._reader = reader
        self._read_lock = asyncio.Lock()
        self._read_task: Optional[asyncio.Task] = None
        self._id = 0
        self._tasks: dict[int, asyncio.Future[Packet]] = {}

    @classmethod
    async def connect(
        cls,
        host: str,
        port: int = 25575,
        password: Optional[str] = None,
        protocol: Optional[Protocol] = None,
    ):
        reader, writer = await asyncio.open_connection(host, port)
        rcon = cls(protocol or MCProtocol(), writer, reader)
        if password is not None:
            await rcon.login(password)
        return rcon

    async def login(self, password: str) -> Packet:
        await self._send(Packet(0, Type.LOGIN, password.encode("utf8")))
        packet = await self.read()
        if packet.type == Type.LOGIN_FAILED:
            raise Exception("Login failed")
        if packet.id != 0:
            raise Exception(f"Unexpected packet id: {packet.id=}")
        return packet

    async def execute(self, command: str) -> str:
        packet = await self.send(Type.COMMAND, command.encode("utf8"))
        if packet.type != Type.RESPONSE:
            raise Exception(f"Unexpected response type: {packet.type=}")
        return packet.payload.decode("utf8")

    async def _send(self, packet: Packet):
        async def write(data: bytes):
            self._writer.write(data)
            await self._writer.drain()

        await self._protocol.send(write, packet)

    async def send(self, type: Type, payload: bytes) -> Packet:
        # self._id += 1
        id = self._id
        await self._send(Packet(id, type, payload))
        future = asyncio.get_event_loop().create_future()
        self._tasks[id] = future
        self._listen()
        return await future

    async def read(self) -> Packet:
        async with self._read_lock:
            return await self._protocol.read(self._reader.readexactly)

    async def _read_loop(self):
        while self._tasks:
            packet = await self.read()
            if packet.id in self._tasks:
                self._tasks[packet.id].set_result(packet)
                del self._tasks[packet.id]
            else:
                print(f"Unexpected packet: {packet=}")
                raise Exception(f"Unexpected packet: {packet=}")
        self._read_task = None

    def _listen(self):
        if self._read_task is None:
            self._read_task = asyncio.create_task(self._read_loop())
