"""empty message

Revision ID: 69068c700909
Revises: 2e4dc45970d9
Create Date: 2019-07-31 20:34:26.714379

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '69068c700909'
down_revision = '2e4dc45970d9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('packs', sa.Column('season', sa.String(length=20), nullable=False, server_default=sa.text("'0'")))
    op.create_index(op.f('ix_packs_season'), 'packs', ['season'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_packs_season'), table_name='packs')
    op.drop_column('packs', 'season')
    # ### end Alembic commands ###
