"""create botuser

Revision ID: 018e3bcffc8f
Revises: 
Create Date: 2022-12-01 13:39:11.097203

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '018e3bcffc8f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("botuser", sa.Column("bot_joined_channel", sa.Boolean))


def downgrade() -> None:
    op.drop_column("botuser", "bot_joined_channel")

