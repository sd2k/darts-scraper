"""Correctly use string for Event.venue

Revision ID: 515c77951c92
Revises: d4b287aba120
Create Date: 2016-02-13 22:57:51.403854

"""

# revision identifiers, used by Alembic.
revision = '515c77951c92'
down_revision = 'd4b287aba120'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'venue', type_=sa.String)
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('events', 'venue', type_=sa.Integer)
    ### end Alembic commands ###
