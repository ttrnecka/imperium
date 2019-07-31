"""empty message

Revision ID: a015feaa7e24
Revises: ba0330bb1335
Create Date: 2019-07-24 20:13:33.426857

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a015feaa7e24'
down_revision = 'ba0330bb1335'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('card_templates',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('race', sa.String(length=20), nullable=False),
    sa.Column('rarity', sa.String(length=20), nullable=False),
    sa.Column('card_type', sa.String(length=20), nullable=False),
    sa.Column('subtype', sa.String(length=30), nullable=False),
    sa.Column('notes', sa.String(length=255), nullable=True),
    sa.Column('value', sa.Integer(), nullable=False),
    sa.Column('skill_access', sa.String(length=20), nullable=True),
    sa.Column('multiplier', sa.Integer(), nullable=False),
    sa.Column('starter_multiplier', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_card_templates_card_type'), 'card_templates', ['card_type'], unique=False)
    op.create_index(op.f('ix_card_templates_name'), 'card_templates', ['name'], unique=False)
    op.create_index(op.f('ix_card_templates_rarity'), 'card_templates', ['rarity'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_card_templates_rarity'), table_name='card_templates')
    op.drop_index(op.f('ix_card_templates_name'), table_name='card_templates')
    op.drop_index(op.f('ix_card_templates_card_type'), table_name='card_templates')
    op.drop_table('card_templates')
    # ### end Alembic commands ###