"""test

Revision ID: 627a0b050b86
Revises: 
Create Date: 2021-12-24 11:58:49.997354

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '627a0b050b86'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.String(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_group_id'), 'group', ['id'], unique=False)
    op.create_table('lessons',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('room', sa.String(), nullable=True),
    sa.Column('subject', sa.String(), nullable=True),
    sa.Column('teacher', sa.String(), nullable=True),
    sa.Column('date', sa.DateTime(), nullable=True),
    sa.Column('group', sa.String(), nullable=True),
    sa.Column('order', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lessons_id'), 'lessons', ['id'], unique=False)
    op.create_table('student',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=True),
    sa.Column('username', sa.String(), nullable=True),
    sa.Column('tid', sa.Integer(), nullable=True),
    sa.Column('language_code', sa.String(), nullable=True),
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['group_id'], ['group.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_student_id'), 'student', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_student_id'), table_name='student')
    op.drop_table('student')
    op.drop_index(op.f('ix_lessons_id'), table_name='lessons')
    op.drop_table('lessons')
    op.drop_index(op.f('ix_group_id'), table_name='group')
    op.drop_table('group')
    # ### end Alembic commands ###