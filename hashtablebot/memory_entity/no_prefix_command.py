from abc import ABC, abstractmethod
from twitchio import Message


# TODO: Turn NoPrefixCommand into Command and use a prefix callable to check for commands without a prefix
class NoPrefixCommand(ABC):
    """
    Abstract class for commands without a prefix, that are not handled by the twitchio API
    """
    def __init__(self, names: str, response: str):
        self.names: list[str] = names.split(" ")
        self.response: str = response

    @abstractmethod
    async def is_a_match(self, message: Message) -> bool:
        pass

    @abstractmethod
    async def respond(self, message):
        pass


class DefaultNoPrefix(NoPrefixCommand):
    """
    Default class for commands without a prefix.
    """
    async def is_a_match(self, message: Message) -> bool:
        """
        Check if every name in the names attribute matches the start of the message.

        Can't use `str.startswith()` because the message could start matching the names and not be a match, like in an
        emote that starts with the same prefix as others.

        :param message:
        :return:
        """
        return all((name == message_arg for name, message_arg in zip(self.names, message.content.split(" "))))

    async def respond(self, message):
        await message.channel.send(self.response)
