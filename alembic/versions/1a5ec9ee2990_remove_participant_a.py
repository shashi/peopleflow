"""Remove Participant.attended

Revision ID: 1a5ec9ee2990
Revises: 41bca295591d
Create Date: 2014-02-09 08:48:54.707522

"""

# revision identifiers, used by Alembic.
revision = '1a5ec9ee2990'
down_revision = '41bca295591d'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('participant', u'attend_date')
    op.drop_column('participant', u'attended')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('participant', sa.Column(u'attended', sa.BOOLEAN(), nullable=False))
    op.add_column('participant', sa.Column(u'attend_date', postgresql.TIMESTAMP(), nullable=True))
    ### end Alembic commands ###