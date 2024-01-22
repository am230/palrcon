from enum import Enum


class Type(int, Enum):
    LOGIN = 3
    COMMAND = 2
    RESPONSE = 0
    LOGIN_FAILED = -1

    def __bytes__(self):
        return self.value.to_bytes(4, "little")


class Packet:
    def __init__(self, id: int, type: Type, payload: bytes) -> None:
        self.id = id
        self.type = type
        self.payload = payload

    def __str__(self) -> str:
        return f"Packet({self.id}, {self.type}, {self.payload!r})"

    __repr__ = __str__
