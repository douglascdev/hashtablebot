from os import getenv

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

_db_user = getenv("POSTGRES_USER")
_db_password = getenv("POSTGRES_PASSWORD")
_db_name = getenv("POSTGRES_DB")
_db_host = getenv("POSTGRES_HOST")

engine = create_engine(
    f"postgresql+psycopg2://{_db_user}:{_db_password}@{_db_host}/{_db_name}",
    future=True,
)

# TODO: search: is it ok to use expire_on_commit like this?
Session = sessionmaker(engine, future=True, expire_on_commit=False)
