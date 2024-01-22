import abc


class Executor(abc.ABC):
    @abc.abstractmethod
    async def execute(self, command: str) -> str:
        pass
