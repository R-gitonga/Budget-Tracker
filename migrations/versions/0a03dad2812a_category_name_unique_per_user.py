"""category name unique per user

Revision ID: 0a03dad2812a
Revises: 7101a0d3d754
Create Date: 2026-10-27 09:27:34.253507

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = '0a03dad2812a'
down_revision = '7101a0d3d754'
branch_labels = None
depends_on = None


def upgrade():
    # Category names were globally unique; make them unique per user instead.
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_constraint('category_name_key', type_='unique')
        batch_op.create_unique_constraint('uq_category_user_name', ['user_id', 'name'])


def downgrade():
    # Fails if two users now share a category name (a global unique rule can't hold).
    with op.batch_alter_table('category', schema=None) as batch_op:
        batch_op.drop_constraint('uq_category_user_name', type_='unique')
        batch_op.create_unique_constraint('category_name_key', ['name'])