"""empty message

Revision ID: 14206916d48b
Revises: 654a2e7b72d6
Create Date: 2023-04-12 13:19:13.337530

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14206916d48b'
down_revision = '654a2e7b72d6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('iban', sa.String(length=22), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'iban')
    # ### end Alembic commands ###