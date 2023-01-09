from hashtablebot.banking.bank_user import BankUser
from hashtablebot.bot_exceptions import PointConversionError


class PointAmountConverter:
    """
    Handles the conversion of point values to an actual integer, somewhat based on the factory pattern.

    If a user wants to gamble points, for example, they could want to pass `10%`, `1`, or `all` as an argument
    and still get a result based on how many points they have.
    """

    @staticmethod
    def convert(amount: str, bank_user: BankUser) -> int:
        """
        Convert an amount of points from any format to an integer value.
        :param bank_user:
        :param amount: string with a percentage, number or word describing an amount
        :raises: PointConversionError if one of these conditions is met:
            - the amount passed is invalid
            - bank_user is not passed for a numeric amount
            - amount exceeds 20 digits
        """
        if len(amount) > 20:
            raise PointConversionError("Amount exceeds 20 digits!")

        if amount.isnumeric():
            return PointAmountConverter._convert_from_num(amount)

        if not bank_user:
            raise PointConversionError(
                "Non-numeric amounts require a BankUser to be passed!"
            )

        elif amount.endswith("%"):
            return PointAmountConverter._convert_from_percentage(amount, bank_user)
        else:
            return PointAmountConverter._convert_from_keyword(amount, bank_user)

    @staticmethod
    def _convert_from_num(amount: str) -> int:
        try:
            int_amount = int(amount)
        except ValueError:
            raise PointConversionError("An invalid amount of points was passed!")
        else:
            return int_amount

    @staticmethod
    def _convert_from_percentage(amount: str, bank_user: BankUser) -> int:
        try:
            int_percentage = int(amount[:-1])
        except ValueError:
            raise PointConversionError("An invalid percentage was passed!")
        else:
            return (bank_user.get_balance() * int_percentage) // 100

    @staticmethod
    def _convert_from_keyword(amount: str, bank_user: BankUser) -> int:
        match amount:
            case "all":
                return bank_user.get_balance()
            case "half":
                return bank_user.get_balance() // 2
            case _:
                raise PointConversionError("Not a valid amount")
