from typing import Protocol


class BankUser(Protocol):
    def withdraw(self, amount: int):
        ...

    def deposit(self, amount: int):
        ...
