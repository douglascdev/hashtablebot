import dataclasses

from sqlalchemy import Boolean, Column, Integer, String, Table
from sqlalchemy.orm import registry

from hashtablebot.bot_exceptions import NotEnoughCoinError

mapper_registry = registry()


@mapper_registry.mapped
@dataclasses.dataclass
class BotUser:
    __table__ = Table(
        "botuser",
        mapper_registry.metadata,
        Column("id", Integer, primary_key=True),
        Column("balance", Integer),
        Column("bot_joined_channel", Boolean),
        Column("bot_command_prefix", String),
    )

    id: int = dataclasses.field(init=True)
    balance: int = 0

    """
    If the user ran the join command this is set to true
    so that the bot joins again even after shutting down
    """
    bot_joined_channel: bool = False

    """
    The command prefix the bot should respond to when in 
    the user's channel.
    """
    bot_command_prefix: str = "$"

    def deposit(self, amount: int):
        self.balance += amount

    def withdraw(self, amount: int):
        if amount > self.balance:
            raise NotEnoughCoinError("Not enough funds")

        self.balance -= amount

    def name(self) -> str:
        # TODO: add name attribute to bot_user
        return str(self.id)

    def get_balance(self) -> int:
        return self.balance
