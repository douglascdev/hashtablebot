import logging
from dataclasses import dataclass, field

from hashtablebot.banking.bank_user import BankUser
from hashtablebot.banking.transaction import Transaction


@dataclass
class Deposit:
    bank_user: BankUser
    amount: int

    @property
    def transfer_details(self) -> str:
        return f"${self.amount} to bot_user {self.bank_user.name()}"

    def execute(self) -> None:
        self.bank_user.deposit(self.amount)
        logging.info(f"Deposited {self.transfer_details}")

    def undo(self) -> None:
        self.bank_user.withdraw(self.amount)
        logging.info(f"Undid deposit of {self.transfer_details}")

    def redo(self) -> None:
        self.bank_user.deposit(self.amount)
        logging.info(f"Redid deposit of {self.transfer_details}")


@dataclass
class Withdrawal:
    bank_user: BankUser
    amount: int

    @property
    def transfer_details(self) -> str:
        return f"${self.amount/100} from bot_user {self.bank_user.name()}"

    def execute(self) -> None:
        self.bank_user.withdraw(self.amount)
        logging.info(f"Withdrawn {self.transfer_details}")

    def undo(self) -> None:
        self.bank_user.deposit(self.amount)
        logging.info(f"Undid withdrawal of {self.transfer_details}")

    def redo(self) -> None:
        self.bank_user.withdraw(self.amount)
        logging.info(f"Redid withdrawal of {self.transfer_details}")


@dataclass
class Transfer:
    from_bank_user: BankUser
    to_bank_user: BankUser
    amount: int

    @property
    def transfer_details(self) -> str:
        return (
            f"${self.amount} from bot_user {self.from_bank_user.name()}"
            f" to bot_user {self.to_bank_user.name()}"
        )

    def execute(self) -> None:
        self.from_bank_user.withdraw(self.amount)
        self.to_bank_user.deposit(self.amount)
        logging.info(f"Transferred {self.transfer_details}")

    def undo(self) -> None:
        self.to_bank_user.withdraw(self.amount)
        self.from_bank_user.deposit(self.amount)
        logging.info(f"Undid transfer of {self.transfer_details}")

    def redo(self) -> None:
        self.from_bank_user.withdraw(self.amount)
        self.to_bank_user.deposit(self.amount)
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
        except Exception:
            for command in reversed(completed_commands):
                command.undo()
            raise

    def undo(self) -> None:
        for command in reversed(self.commands):
            command.undo()

    def redo(self) -> None:
        for command in self.commands:
            command.redo()
