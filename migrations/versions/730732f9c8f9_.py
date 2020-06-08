"""empty message

Revision ID: 730732f9c8f9
Revises: 73133c8f8ab4
Create Date: 2020-06-08 19:44:03.725643

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '730732f9c8f9'
down_revision = '73133c8f8ab4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card_templates', sa.Column('number_of_uses', sa.Integer(), nullable=False))
    op.drop_column('card_templates', 'one_time_use')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card_templates', sa.Column('one_time_use', mysql.TINYINT(display_width=1), server_default=sa.text("'0'"), autoincrement=False, nullable=False))
    op.drop_column('card_templates', 'number_of_uses')
    # ### end Alembic commands ###
