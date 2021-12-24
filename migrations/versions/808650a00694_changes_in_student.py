"""changes in student.

Revision ID: 808650a00694
Revises: c8dd48e894db
Create Date: 2021-12-24 10:31:55.709747

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '808650a00694'
down_revision = 'c8dd48e894db'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lessons', sa.Column('lorder', sa.String(), nullable=True))
    op.drop_column('lessons', 'order')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('lessons', sa.Column('order', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.drop_column('lessons', 'lorder')
    # ### end Alembic commands ###