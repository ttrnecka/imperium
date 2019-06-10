"""empty message

Revision ID: fbbcc3045320
Revises: 551e7f9786f5
Create Date: 2019-06-04 13:40:57.623570

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fbbcc3045320'
down_revision = '551e7f9786f5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('coaches', sa.Column('free_packs', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('coaches', 'free_packs')
    # ### end Alembic commands ###