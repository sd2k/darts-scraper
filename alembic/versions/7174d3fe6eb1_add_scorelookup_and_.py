"""Add ScoreLookup and Simulation model

Revision ID: 7174d3fe6eb1
Revises: 83505c1e34db
Create Date: 2017-02-20 08:43:52.844621

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '7174d3fe6eb1'
down_revision = '83505c1e34db'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'score_lookups',
        sa.Column('score', sa.Integer(), nullable=False),
        sa.Column(
            'dart',
            sa.Enum('one', 'two', 'three', name='dart_numbers'),
            nullable=False,
        ),
        sa.Column(
            'shot_type',
            sa.Enum('single', 'treble', 'bull', 'outer_bull', 'double', name='shot_types'),  # noqa
            nullable=False,
        ),
        sa.Column('hit_points', sa.Integer(), nullable=False),
        sa.Column('miss_points', sa.Integer(), nullable=True),
        sa.Column('big_miss_points', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('score', 'dart')
    )
    op.create_table(
        'simulations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('profile_id', sa.Integer(), nullable=True),
        sa.Column('iterations', sa.Integer(), nullable=False),
        sa.Column('results', postgresql.ARRAY(sa.Integer()), nullable=False),
        sa.ForeignKeyConstraint(['profile_id'], ['profiles.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('simulations')
    op.drop_table('score_lookups')
