"""v1.2

Revision ID: c2c8b6d9a6e4
Revises: 2ca3b7a7a343
Create Date: 2021-10-08 07:14:18.168282

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c2c8b6d9a6e4'
down_revision = '2ca3b7a7a343'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('namstasks', sa.Column('desc', sa.Text(), nullable=True))
    op.add_column('namstasks', sa.Column('result', sa.Text(), nullable=True))
    op.add_column('namstasks', sa.Column('thisinfo_lastupdatetime', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('namstasks', 'thisinfo_lastupdatetime')
    op.drop_column('namstasks', 'result')
    op.drop_column('namstasks', 'desc')
    # ### end Alembic commands ###
