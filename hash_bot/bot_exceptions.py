from abc import ABC, abstractmethod


class ExceptionWithChatMessage(ABC, Exception):
    @staticmethod
    @abstractmethod
    def get_chat_message() -> str:
        pass


class NotEnoughCoinError(ExceptionWithChatMessage):
    @staticmethod
    def get_chat_message() -> str:
        return "You don't have enough elis coins elisLookingAtYou"


class InvalidPointAmountError(ExceptionWithChatMessage):
    @staticmethod
    def get_chat_message() -> str:
        return "An invalid point amount was passed elisLookingAtYou"
