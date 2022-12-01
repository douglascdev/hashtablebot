import dataclasses

from sqlalchemy import Column, Integer, Boolean, Table
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
    )

    id: int = dataclasses.field(init=True)
    balance: int = 0
    bot_joined_channel: bool = False

    def deposit(self, amount: int):
        self.balance += amount

    def withdraw(self, amount: int):
        if amount > self.balance:
            raise NotEnoughCoinError("Not enough funds")

        self.balance -= amount
