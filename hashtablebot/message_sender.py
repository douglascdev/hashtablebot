import logging
from typing import Protocol

from twitchio import InvalidContent


class Named(Protocol):
    name: str


class AbstractTwitchContext(Protocol):
    channel: Named
    author: Named

    async def send(self, message: str):
        ...

    async def reply(self, message: str):
        ...


class AbstractMessageSender(Protocol):
    @staticmethod
    async def send(ctx: AbstractTwitchContext, msg: str, **kwargs) -> str:
        ...

    @staticmethod
    async def reply(ctx: AbstractTwitchContext, msg: str, **kwargs) -> str:
        ...


class SafeMessageSender:
    @staticmethod
    async def send(ctx: AbstractTwitchContext, msg: str, **kwargs):
        """

        Raises
        ------
        ValueError
        """
        command_execution_allowed: bool = kwargs.get("command_execution_allowed")

        if not command_execution_allowed and msg.lstrip().startswith("/"):
            logging.warning(f"Attempted command injection with message '{msg}' "
                            f"by '{ctx.author.name}' in channel '{ctx.channel.name}'.")
            msg = f"#{msg}"

        try:
            await ctx.send(msg)
            return msg
        except InvalidContent as e:
            raise ValueError("Invalid message") from e

    @staticmethod
    async def reply(ctx: AbstractTwitchContext, msg: str, **kwargs):
        """

        Raises
        ------
        ValueError
        """
        try:
            await ctx.reply(msg)
            return msg
        except InvalidContent as e:
            raise ValueError("Invalid message") from e
