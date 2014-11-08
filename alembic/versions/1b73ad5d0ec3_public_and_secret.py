"""public_and_secret

Revision ID: 1b73ad5d0ec3
Revises: 519731dea59
Create Date: 2014-11-08 17:40:15.076928

"""

# revision identifiers, used by Alembic.
revision = '1b73ad5d0ec3'
down_revision = '519731dea59'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('participant', sa.Column(u'public', sa.Unicode(4), nullable=False, server_default=''))
    op.alter_column('participant', 'public', server_default=None)
    op.add_column('participant', sa.Column(u'secret', sa.Unicode(20), nullable=False, server_default=''))
    op.alter_column('participant', 'secret', server_default=None)


def downgrade():
    op.drop_column('participant', u'public')
    op.drop_column('participant', u'secret')
