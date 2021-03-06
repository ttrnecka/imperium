"""empty message

Revision ID: 7315a1367475
Revises: c5223054be86
Create Date: 2019-05-13 20:09:04.572193

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '7315a1367475'
down_revision = 'c5223054be86'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('cards', sa.Column('deck_type', sa.String(length=255), nullable=False, server_default=sa.text("'base'")))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('cards', 'deck_type')
    # ### end Alembic commands ###
