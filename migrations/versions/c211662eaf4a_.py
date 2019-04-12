"""empty message

Revision ID: c211662eaf4a
Revises: 630adadff77b
Create Date: 2019-04-10 15:11:51.581716

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'c211662eaf4a'
down_revision = '630adadff77b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coaches', 'deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=True,
               existing_server_default=sa.text("'0'"))
    # ### end Alembic commands ###
    op.alter_column('cards', 'description',
               type_=sa.Text())
    op.alter_column('transactions', 'description',
               type_=sa.String(255))

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('coaches', 'deleted',
               existing_type=mysql.TINYINT(display_width=1),
               nullable=False,
               existing_server_default=sa.text("'0'"))
    # ### end Alembic commands ###
    op.alter_column('cards', 'description',
               type_=sa.String(255))
    op.alter_column('transactions', 'description',
               type_=sa.String(20))