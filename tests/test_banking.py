import dataclasses
from unittest import TestCase

from hashtablebot.banking.bank import Bank
from hashtablebot.banking.bank_user import BankUser
from hashtablebot.banking.commands import Batch, Deposit, Transfer, Withdrawal
from hashtablebot.bot_exceptions import NotEnoughCoinError


class TestBanking(TestCase):
    """
    Tests for Banking module
    """

    @dataclasses.dataclass
    class TestBankUser:
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

    def setUp(self) -> None:
        self.bank_user: BankUser = self.TestBankUser(balance=100)

    def test_deposit_batch(self):
        Bank().execute(
            Batch(
                [
                    Deposit(bank_user=self.bank_user, amount=100),
                    Deposit(bank_user=self.bank_user, amount=100),
                ]
            )
        )
        self.assertEqual(self.bank_user.get_balance(), 300)

    def test_withdraw_batch(self):
        Bank().execute(
            Batch(
                [
                    Withdrawal(bank_user=self.bank_user, amount=10),
                    Withdrawal(bank_user=self.bank_user, amount=10),
                ]
            )
        )
        self.assertEqual(self.bank_user.get_balance(), 80)

    def test_undo_redo_batch(self):
        bank = Bank()
        bank.execute(
            Batch(
                [
                    Withdrawal(bank_user=self.bank_user, amount=10),
                    Withdrawal(bank_user=self.bank_user, amount=10),
                ]
            )
        )
        bank.undo()
        self.assertEqual(self.bank_user.get_balance(), 100)

        bank.redo()
        self.assertEqual(self.bank_user.get_balance(), 80)

    def test_redo_with_no_transactions(self):
        bank = Bank()

        # Redo stack is empty, should keep the same value
        bank.redo()
        self.assertEqual(self.bank_user.get_balance(), 100)

    def test_undo_with_no_transactions(self):
        bank = Bank()

        # Undo stack is empty, should keep the same value
        bank.undo()
        self.assertEqual(self.bank_user.get_balance(), 100)

    def test_failing_transaction_reverses_batch(self):
        with self.assertRaises(Exception):
            Bank().execute(
                Batch(
                    [
                        # Executes
                        Withdrawal(bank_user=self.bank_user, amount=50),
                        # Fails, should reverse previous transaction
                        Withdrawal(bank_user=self.bank_user, amount=51),
                    ]
                )
            )
        self.assertEqual(self.bank_user.get_balance(), 100)

    def test_transfer(self):
        transfer_target: BankUser = self.TestBankUser(balance=100)

        bank = Bank()

        bank.execute(Transfer(self.bank_user, transfer_target, 100))
        self.assertEqual(self.bank_user.get_balance(), 0)
        self.assertEqual(transfer_target.get_balance(), 200)

        bank.undo()
        self.assertEqual(self.bank_user.get_balance(), 100)
        self.assertEqual(transfer_target.get_balance(), 100)

        bank.redo()
        self.assertEqual(self.bank_user.get_balance(), 0)
        self.assertEqual(transfer_target.get_balance(), 200)
