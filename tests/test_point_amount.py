from unittest import TestCase

from hashtablebot.banking.bank_user import BankUser
from hashtablebot.bot_exceptions import PointConversionError
from hashtablebot.memory_entity.point_amount import PointAmountConverter
from tests.bank_user_test import BankUserTest


class TestPointAmountConverter(TestCase):
    """
    Test the point converter
    """

    def setUp(self) -> None:
        self.bank_user: BankUser = BankUserTest(balance=100)

    def test_convert_num(self):
        self.assertEqual(PointAmountConverter.convert("10", self.bank_user), 10)

        # Fails above 20 digits
        with self.assertRaises(PointConversionError):
            PointAmountConverter.convert("".join("1" * 21), self.bank_user)

        # Doesn't fail on 20 digits
        max_points = "".join("1" * 20)
        self.assertEqual(
            PointAmountConverter.convert(max_points, self.bank_user), int(max_points)
        )

    def test_convert_percent(self):
        self.assertEqual(PointAmountConverter.convert("10%", self.bank_user), 10)

        self.bank_user.withdraw(55)  # balance: 45
        self.assertEqual(PointAmountConverter.convert("10%", self.bank_user), 4)

        with self.assertRaises(PointConversionError):
            PointAmountConverter.convert("10%", None)

        with self.assertRaises(PointConversionError):
            PointAmountConverter.convert("a%", self.bank_user)

    def test_convert_keyword(self):
        self.assertEqual(PointAmountConverter.convert("all", self.bank_user), 100)
        self.assertEqual(PointAmountConverter.convert("half", self.bank_user), 50)

        with self.assertRaises(PointConversionError):
            PointAmountConverter.convert("asdasf", self.bank_user)

        with self.assertRaises(PointConversionError):
            PointAmountConverter.convert("all", None)
