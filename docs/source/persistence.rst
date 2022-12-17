.. _persistence:

Persistence
===========

To store user data like points the bot needs some way of persisting data to a database.
For that purpose, an `Object Relational Mapper` is used.

An ORM provides a higher level of abstraction over SQL and a DBMS, ensuring security against injection,
DBMS-independent code and makes storing and retrieving data a easier and less error-prone.

SQLAlchemy
----------

The bot uses `SQLAlchemy 1.4 <https://docs.sqlalchemy.org/en/14/contents.html>`_ as ORM, which connects to a Postgres
server running in a docker compose container.

The :py:mod:`hashtablebot.persistence` package contains the code that handles persisting and retrieving data, and
:py:mod:`hashtablebot.entity` defines the Python objects to be persisted and their corresponding table structures.

Alembic
-------

Despite new tables being created automatically by SQLAlchemy, changing, removing or adding new columns isn't.
For that purpose, `Alembic <https://alembic.sqlalchemy.org/en/latest/>`_ is used to create migrations.

