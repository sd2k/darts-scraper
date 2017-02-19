"""Add Profile model

Revision ID: 83505c1e34db
Revises: 5d3efe3e663f
Create Date: 2017-02-18 21:22:32.252765

"""

# revision identifiers, used by Alembic.
from alembic import op
import sqlalchemy as sa


revision = '83505c1e34db'
down_revision = '5d3efe3e663f'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'profiles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('treble_hit_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('treble_miss_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('treble_big_miss_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('bullseye_hit_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('bullseye_miss_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('outer_bull_hit_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('outer_bull_miss_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('double_hit_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('double_miss_inside_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.Column('double_miss_outside_pct', sa.Numeric(precision=4, scale=2), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('profiles')
