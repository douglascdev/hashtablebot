"""add command prefix column

Revision ID: 982acebc614d
Revises: 018e3bcffc8f
Create Date: 2022-12-01 15:06:50.522339

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '982acebc614d'
down_revision = '018e3bcffc8f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("botuser", sa.Column("bot_command_prefix", sa.String, nullable=False, server_default="$"))


def downgrade() -> None:
    op.drop_column("botuser", "bot_command_prefix")

