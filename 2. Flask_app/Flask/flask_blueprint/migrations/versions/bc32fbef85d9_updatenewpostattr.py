"""'updatenewpostattr'

Revision ID: bc32fbef85d9
Revises: 3f7a01b152e5
Create Date: 2021-09-27 06:26:09.866506

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'bc32fbef85d9'
down_revision = '3f7a01b152e5'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('toquery_authornamestartswitha', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_posts_toquery_authornamestartswitha'), 'posts', ['toquery_authornamestartswitha'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_posts_toquery_authornamestartswitha'), table_name='posts')
    op.drop_column('posts', 'toquery_authornamestartswitha')
    # ### end Alembic commands ###
