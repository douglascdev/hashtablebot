from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from hashtablebot.entity.bot_user import BotUser

engine = create_engine("sqlite:////home/douglas/hashtablebot.db", echo=True, future=True)

# TODO: search: is it ok to use expire_on_commit like this?
Session = sessionmaker(engine, future=True, expire_on_commit=False)

declarative_base().metadata.create_all(engine, tables=[BotUser.__table__])
