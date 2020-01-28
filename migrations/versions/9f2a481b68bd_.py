"""empty message

Revision ID: 9f2a481b68bd
Revises: 31fead39d1e5
Create Date: 2020-01-24 17:30:43.792815

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f2a481b68bd'
down_revision = '31fead39d1e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('conclave_rules',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('type', sa.String(length=80), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.Text(), nullable=False),
    sa.Column('level1', sa.Integer(), nullable=False),
    sa.Column('level2', sa.Integer(), nullable=False),
    sa.Column('level3', sa.Integer(), nullable=False),
    sa.Column('notes', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tournament_admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('region', sa.String(length=255), nullable=False),
    sa.Column('load', sa.Integer(), nullable=False),
    sa.Column('tournament_types', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tournament_rooms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tournament_sponsors',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date_created', sa.DateTime(), nullable=True),
    sa.Column('date_modified', sa.DateTime(), nullable=True),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('effect', sa.Text(), nullable=False),
    sa.Column('skill_pack_granted', sa.String(length=255), nullable=True),
    sa.Column('special_rules', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('tournaments', sa.Column('consecration', sa.String(length=80), nullable=True))
    op.add_column('tournaments', sa.Column('corruption', sa.String(length=80), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tournaments', 'corruption')
    op.drop_column('tournaments', 'consecration')
    op.drop_table('tournament_sponsors')
    op.drop_table('tournament_rooms')
    op.drop_table('tournament_admins')
    op.drop_table('conclave_rules')
    # ### end Alembic commands ###