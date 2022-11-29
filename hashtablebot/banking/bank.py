from sqlalchemy.exc import NoResultFound
from twitchio import Chatter

from hashtablebot.banking.commands import Deposit
from hashtablebot.banking.transaction import Transaction
from hashtablebot.entity.bot_user import BotUser
from hashtablebot.persistence.bot_user_dao import BotUserDao
from hashtablebot.user_checks import is_chatter


class Bank:
    """
    Controls transactions that change BotUser's balance.

    Uses ArjanCodes's implementation of the Command Design Pattern to
    ensure an error in a batch of transactions rolls back changes to all balances.
    """

    undo_stack: list[Transaction] = list()
    redo_stack: list[Transaction] = list()

    def execute(self, transaction: Transaction) -> None:
        transaction.execute()
        self.redo_stack.clear()
        self.undo_stack.append(transaction)

    def undo(self) -> None:
        if not self.undo_stack:
            return

        transaction = self.undo_stack.pop()
        transaction.undo()
        self.redo_stack.append(transaction)

    def redo(self) -> None:
        if not self.redo_stack:
            return

        transaction = self.redo_stack.pop()
        transaction.execute()
        self.undo_stack.append(transaction)

    def reward_chatter(self, chatter: Chatter, reward: int):
        if reward <= 0 or not is_chatter(chatter):
            return

        author_id = int(chatter.id)

        try:
            author_bot_user: BotUser = BotUserDao.get_by_id(author_id)
        except NoResultFound:
            # TODO: I guess this breaks single responsibility principle...? Should probably refactor it
            author_bot_user = BotUser(id=author_id)

        self.execute(Deposit(bot_user=author_bot_user, amount=reward))

        # TODO: should probably remove this too, saving should not happen here
        BotUserDao.save(author_bot_user)
