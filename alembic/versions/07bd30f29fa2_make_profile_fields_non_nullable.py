"""Make Profile fields non-nullable

Revision ID: 07bd30f29fa2
Revises: 7174d3fe6eb1
Create Date: 2017-02-20 21:51:14.499573

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '07bd30f29fa2'
down_revision = '7174d3fe6eb1'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'profiles',
        'bullseye_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'bullseye_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'double_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'double_miss_inside_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'double_miss_outside_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'name',
        existing_type=sa.VARCHAR(),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'outer_bull_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'outer_bull_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'treble_big_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'treble_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )
    op.alter_column(
        'profiles',
        'treble_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        'profiles',
        'treble_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'treble_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'treble_big_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'outer_bull_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'outer_bull_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'name',
        existing_type=sa.VARCHAR(),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'double_miss_outside_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'double_miss_inside_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'double_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'bullseye_miss_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
    op.alter_column(
        'profiles',
        'bullseye_hit_pct',
        existing_type=sa.NUMERIC(precision=4, scale=2),
        nullable=True,
    )
