from hashtablebot.banking.transaction import Transaction


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
