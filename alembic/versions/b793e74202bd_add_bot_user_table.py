"""Add bot user table

Revision ID: b793e74202bd
Revises: 
Create Date: 2022-12-17 17:41:34.916176

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b793e74202bd'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('botuser',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('balance', sa.Integer(), nullable=True),
    sa.Column('bot_joined_channel', sa.Boolean(), nullable=True),
    sa.Column('bot_command_prefix', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('botuser')
    # ### end Alembic commands ###
