"""Venue BaseNameMixin

Revision ID: 4071a0ce67ef
Revises: 28dea4ec9f96
Create Date: 2014-02-10 09:25:24.992339

"""

# revision identifiers, used by Alembic.
revision = '4071a0ce67ef'
down_revision = '28dea4ec9f96'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('venue', sa.Column('name', sa.Unicode(length=250), nullable=False))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('venue', 'name')
    ### end Alembic commands ###
