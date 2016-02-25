"""Add Fixtures model

Revision ID: 5d3efe3e663f
Revises: cacc6a13f2d7
Create Date: 2016-02-25 10:17:33.951783

"""

# revision identifiers, used by Alembic.
revision = '5d3efe3e663f'
down_revision = 'cacc6a13f2d7'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('fixtures',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=True),
    sa.Column('date', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['event_id'], ['events.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('fixture_players',
    sa.Column('player_id', sa.Integer(), nullable=False),
    sa.Column('fixture_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['fixture_id'], ['fixtures.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['players.id'], ),
    sa.PrimaryKeyConstraint('player_id', 'fixture_id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('fixture_players')
    op.drop_table('fixtures')
    ### end Alembic commands ###
