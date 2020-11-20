"""empty message

Revision ID: 0b07c59aad12
Revises: 4f3530932397
Create Date: 2020-11-19 14:13:49.944109

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0b07c59aad12'
down_revision = '4f3530932397'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('genre', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'genre')
    # ### end Alembic commands ###