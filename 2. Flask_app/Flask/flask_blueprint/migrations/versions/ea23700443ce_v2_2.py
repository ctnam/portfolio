"""v2.2

Revision ID: ea23700443ce
Revises: f92668e7282f
Create Date: 2021-10-15 10:02:30.674146

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ea23700443ce'
down_revision = 'f92668e7282f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('insulins', sa.Column('NamisUsing', sa.Boolean(), nullable=True))
    op.create_index(op.f('ix_insulins_NamisUsing'), 'insulins', ['NamisUsing'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_insulins_NamisUsing'), table_name='insulins')
    op.drop_column('insulins', 'NamisUsing')
    # ### end Alembic commands ###
