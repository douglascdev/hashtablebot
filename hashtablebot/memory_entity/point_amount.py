from hashtablebot.bot_exceptions import InvalidPointAmountError
from hashtablebot.entity.bot_user import BotUser


class PointAmountConverter:
    """
    Handles the conversion of point values to an actual integer, somewhat based on the factory pattern.

    If a user wants to gamble points, for example, they could want to pass `10%`, `1`, or `all` as an argument
    and still get a result based on how many points they have.
    """
    @staticmethod
    def convert(amount: str, bot_user: BotUser) -> int:
        """
        Convert an amount of points from any format to an integer value.
        :param bot_user:
        :param amount: string with a percentage, number or word describing an amount
        :raises: InvalidPointAmountError
        """
        if amount.isnumeric():
            return PointAmountConverter._convert_from_num(amount)
        elif amount.endswith("%"):
            return PointAmountConverter._convert_from_percentage(amount, bot_user)
        else:
            return PointAmountConverter._convert_from_keyword(amount, bot_user)

    @staticmethod
    def _convert_from_num(amount: str) -> int:
        try:
            int_amount = int(amount)
        except ValueError:
            raise InvalidPointAmountError("An invalid amount of points was passed!")
        else:
            return int_amount

    @staticmethod
    def _convert_from_percentage(amount: str, bot_user: BotUser) -> int:
        try:
            int_percentage = int(amount[:-1])
        except ValueError:
            raise InvalidPointAmountError("An invalid percentage was passed!")
        else:
            if not bot_user:
                raise InvalidPointAmountError("Not a valid user!")

            return (bot_user.balance * int_percentage) // 100

    @staticmethod
    def _convert_from_keyword(amount: str, bot_user: BotUser) -> int:
        match amount:
            case "all":
                return bot_user.balance
            case "half":
                return bot_user.balance // 2
            case _:
                raise InvalidPointAmountError("Not a valid amount")
