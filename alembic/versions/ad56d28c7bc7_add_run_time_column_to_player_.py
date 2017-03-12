"""add run time column to player simulations table

Revision ID: ad56d28c7bc7
Revises: 94dd72f228cf
Create Date: 2017-03-12 13:00:30.972169

"""

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'ad56d28c7bc7'
down_revision = '94dd72f228cf'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'player_simulations',
        sa.Column('run_time', sa.DateTime(), nullable=True),
    )


def downgrade():
    op.drop_column('player_simulations', 'run_time')
