import asyncio

from palrcon import Type
from palrcon.packet import Packet


def test_pal_read():
    from palrcon.impl.pal import PalProtocol

    protocol = PalProtocol()
    read_buffer = (
        b"\n\x00\x00\x00"
        b"\x00\x00\x00\x00\x02\x00\x00\x00"
        b""
        b"\x00\x00"
        b"!\x00\x00\x00"
        b"\x00\x00\x00\x00\x00\x00\x00\x00"
        b"name,playeruid,steamid\n"
        b"\x00\x00"
    )

    async def reader(n: int) -> bytes:
        nonlocal read_buffer
        if len(read_buffer) < n:
            raise Exception("Not enough data")
        result = read_buffer[:n]
        read_buffer = read_buffer[n:]
        return result

    async def test():
        login_res = await protocol.read(reader)
        assert login_res.id == 0
        assert login_res.type == Type.COMMAND
        assert login_res.payload == b""
        cmd_res = await protocol.read(reader)
        assert cmd_res.id == 0
        assert cmd_res.type == Type.RESPONSE
        assert cmd_res.payload == b"name,playeruid,steamid\n"

    asyncio.run(test())


def test_pal_write():
    from palrcon.impl.pal import PalProtocol

    protocol = PalProtocol()

    buffer = [
        b"\n\x00\x00\x00\x00\x00\x00\x00\x03\x00\x00\x00\x00\x00",  # login
        b"\x15\x00\x00\x00\x00\x00\x00\x00\x02\x00\x00\x00ShowPlayers\x00\x00",  # command
    ]

    async def writer(data: bytes) -> None:
        buf = buffer.pop(0)
        assert data == buf

    async def test():
        await protocol.send(writer, Packet(0, Type.LOGIN, b""))
        await protocol.send(writer, Packet(0, Type.COMMAND, b"ShowPlayers"))

    asyncio.run(test())
