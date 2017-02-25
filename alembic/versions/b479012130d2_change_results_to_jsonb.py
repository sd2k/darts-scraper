"""Change results to JSONB

Revision ID: b479012130d2
Revises: 07bd30f29fa2
Create Date: 2017-02-25 19:53:46.792912

"""

# revision identifiers, used by Alembic.

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'b479012130d2'
down_revision = '07bd30f29fa2'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('simulations', 'results')
    op.add_column(
        'simulations',
        sa.Column(
            'results',
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
    )


def downgrade():
    op.drop_column('simulations', 'results')
    op.add_column(
        'simulations',
        sa.Column('results', postgresql.ARRAY(sa.Integer), nullable=False),
    )
