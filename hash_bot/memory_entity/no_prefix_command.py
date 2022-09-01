from abc import ABC, abstractmethod
from twitchio import Message


# TODO: Turn NoPrefixCommand into Command and use a prefix callable to check for commands without a prefix
class NoPrefixCommand(ABC):
    def __init__(self, names: tuple[str, ...], response: str):
        self.names: str = names
        self.response: str = response

    @abstractmethod
    async def is_a_match(self, message: Message) -> bool:
        pass

    @abstractmethod
    async def respond(self, message):
        pass


class DefaultNoPrefix(NoPrefixCommand):
    async def is_a_match(self, message: Message) -> bool:
        for name, message_arg in zip(self.names, message.content.split(" ")):
            if name != message_arg:
                return False

        return True

    async def respond(self, message):
        await message.channel.send(self.response)
