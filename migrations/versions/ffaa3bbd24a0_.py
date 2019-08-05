"""empty message

Revision ID: ffaa3bbd24a0
Revises: 69068c700909
Create Date: 2019-08-05 14:19:22.249007

"""
from alembic import op
import sqlalchemy as sa
from models.data_models import TextPickleType


# revision identifiers, used by Alembic.
revision = 'ffaa3bbd24a0'
down_revision = '69068c700909'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('decks', sa.Column('injury_map', TextPickleType(), nullable=False))
    op.add_column('decks', sa.Column('phase_done', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('decks', 'phase_done')
    op.drop_column('decks', 'injury_map')
    # ### end Alembic commands ###
