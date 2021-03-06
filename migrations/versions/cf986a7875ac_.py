"""empty message

Revision ID: cf986a7875ac
Revises: 21cc16de7963
Create Date: 2020-05-31 13:17:21.083958

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cf986a7875ac'
down_revision = '21cc16de7963'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tournament_templates', sa.Column('template_id', sa.Integer(), nullable=False))
    op.create_index(op.f('ix_tournament_templates_template_id'), 'tournament_templates', ['template_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_tournament_templates_template_id'), table_name='tournament_templates')
    op.drop_column('tournament_templates', 'template_id')
    # ### end Alembic commands ###
