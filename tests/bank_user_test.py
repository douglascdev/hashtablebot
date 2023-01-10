from dataclasses import dataclass

from hashtablebot.bot_exceptions import NotEnoughCoinError


@dataclass
class BankUserTest:
    """
    Test implementation of BankUser Protocol
    """

    balance: int

    def deposit(self, amount: int):
        self.balance += amount

    def withdraw(self, amount: int):
        if amount > self.balance:
            raise NotEnoughCoinError("Not enough funds")

        self.balance -= amount

    def name(self) -> str:
        return "Name"

    def get_balance(self) -> int:
        return self.balance
