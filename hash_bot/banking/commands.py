import logging
from dataclasses import dataclass, field

from hash_bot.banking.transaction import Transaction
from hash_bot.entity.bot_user import BotUser


@dataclass
class Deposit:
    bot_user: BotUser
    amount: int

    @property
    def transfer_details(self) -> str:
        return f"${self.amount} to bot_user {self.bot_user.id}"

    def execute(self) -> None:
        self.bot_user.deposit(self.amount)
        logging.info(f"Deposited {self.transfer_details}")

    def undo(self) -> None:
        self.bot_user.withdraw(self.amount)
        logging.info(f"Undid deposit of {self.transfer_details}")

    def redo(self) -> None:
        self.bot_user.deposit(self.amount)
        logging.info(f"Redid deposit of {self.transfer_details}")


@dataclass
class Withdrawal:
    bot_user: BotUser
    amount: int

    @property
    def transfer_details(self) -> str:
        return f"${self.amount/100} from bot_user {self.bot_user.id}"

    def execute(self) -> None:
        self.bot_user.withdraw(self.amount)
        logging.info(f"Withdrawn {self.transfer_details}")

    def undo(self) -> None:
        self.bot_user.deposit(self.amount)
        logging.info(f"Undid withdrawal of {self.transfer_details}")

    def redo(self) -> None:
        self.bot_user.withdraw(self.amount)
        logging.info(f"Redid withdrawal of {self.transfer_details}")


@dataclass
class Transfer:
    from_bot_user: BotUser
    to_bot_user: BotUser
    amount: int

    @property
    def transfer_details(self) -> str:
        return (
            f"${self.amount} from bot_user {self.from_bot_user.id}"
            f" to bot_user {self.to_bot_user.id}"
        )

    def execute(self) -> None:
        self.from_bot_user.withdraw(self.amount)
        self.to_bot_user.deposit(self.amount)
        logging.info(f"Transferred {self.transfer_details}")

    def undo(self) -> None:
        self.to_bot_user.withdraw(self.amount)
        self.from_bot_user.deposit(self.amount)
        logging.info(f"Undid transfer of {self.transfer_details}")

    def redo(self) -> None:
        self.from_bot_user.withdraw(self.amount)
        self.to_bot_user.deposit(self.amount)
        logging.info(f"Redid transfer of {self.transfer_details}")


@dataclass
class Batch:
    commands: list[Transaction] = field(default_factory=list)

    def execute(self) -> None:
        completed_commands: list[Transaction] = []
        try:
            for command in self.commands:
                command.execute()
                completed_commands.append(command)
        except ValueError:
            for command in reversed(completed_commands):
                command.undo()
            raise

    def undo(self) -> None:
        for command in reversed(self.commands):
            command.undo()

    def redo(self) -> None:
        for command in self.commands:
            command.redo()
