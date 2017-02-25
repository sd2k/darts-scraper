"""Change name of simulations table

Revision ID: 94dd72f228cf
Revises: b479012130d2
Create Date: 2017-02-25 19:56:54.810313

"""

# revision identifiers, used by Alembic.
from alembic import op

revision = '94dd72f228cf'
down_revision = 'b479012130d2'
branch_labels = None
depends_on = None


def upgrade():
    op.rename_table('simulations', 'player_simulations')


def downgrade():
    op.rename_table('player_simulations', 'simulations')
