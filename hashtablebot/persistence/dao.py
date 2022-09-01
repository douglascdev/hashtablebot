from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Iterable

from sqlalchemy import select

from hashtablebot.persistence.session import Session

T = TypeVar("T")


class Dao(Generic[T], ABC):
    @staticmethod
    @abstractmethod
    def get_by_id(obj_id: int) -> T:
        pass

    @staticmethod
    @abstractmethod
    def get_by_ids(obj_ids: Iterable[int]) -> list[T]:
        pass

    @staticmethod
    @abstractmethod
    def get_all() -> list[T]:
        pass

    @staticmethod
    @abstractmethod
    def save(*objs: T):
        pass

    @staticmethod
    @abstractmethod
    def update(*objs: T):
        pass

    @staticmethod
    @abstractmethod
    def delete(*objs: T):
        pass
