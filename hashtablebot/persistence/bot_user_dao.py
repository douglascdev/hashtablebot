from typing import Iterable

from sqlalchemy import desc, select

from hashtablebot.entity.bot_user import BotUser
from hashtablebot.persistence.dao import Dao
from hashtablebot.persistence.session import Session


class BotUserDao(Dao[BotUser]):
    @staticmethod
    def get_by_id(obj_id: int) -> BotUser:
        """
        Return object with obj_id or raise an exception.

        :raises: NoResultFound
        """
        with Session.begin() as db_session:
            statement = select(BotUser).filter(BotUser.id == obj_id)
            return db_session.scalars(statement).one()

    @staticmethod
    def get_by_ids(obj_ids: Iterable[int]) -> list[BotUser]:
        """
        Return list with objects in obj_ids.
        """
        with Session.begin() as db_session:
            statement = select(BotUser).filter(BotUser.id in obj_ids)
            return db_session.scalars(statement).all()

    @staticmethod
    def get_all() -> list[BotUser]:
        """
        Return a list of all objects of type BotUser
        """
        with Session.begin() as db_session:
            return db_session.execute(select(BotUser)).all()

    @staticmethod
    def save(*objs: BotUser):
        with Session.begin() as db_session:
            db_session.add_all(objs)
            db_session.commit()

    @staticmethod
    def update(*objs: BotUser):
        with Session.begin() as db_session:
            not_added_objs = [obj for obj in objs if obj not in db_session]
            db_session.add_all(not_added_objs)
            db_session.commit()

    @staticmethod
    def delete(*objs: BotUser):
        with Session.begin() as db_session:
            for obj in objs:
                db_session.delete(obj)

            db_session.commit()

    @staticmethod
    def get_all_joined_channels() -> list[BotUser]:
        with Session.begin() as db_session:
            query = select(BotUser).filter(BotUser.bot_joined_channel)
            return list(db_session.execute(query).scalars())

    @staticmethod
    def get_until_limit_order_by_balance_desc(limit: int) -> list[BotUser]:
        with Session.begin() as db_session:
            query = select(BotUser).order_by(desc(BotUser.balance)).limit(limit)
            return list(db_session.execute(query).scalars())
