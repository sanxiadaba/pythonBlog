"""one-time codes and hot-path indexes

Revision ID: 9f1c2b7a4d10
Revises: 5c6ddb001dda
Create Date: 2026-11-10 09:20:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "9f1c2b7a4d10"
down_revision = "5c6ddb001dda"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "users",
        sa.Column("session_version", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_table(
        "one_time_code",
        sa.Column("token", sa.String(length=64), nullable=False),
        sa.Column("kind", sa.String(length=16), nullable=False),
        sa.Column("code_hash", sa.String(length=64), nullable=False),
        sa.Column("subject", sa.String(length=254), nullable=True),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("attempts", sa.Integer(), server_default="0", nullable=False),
        sa.PrimaryKeyConstraint("token"),
    )
    op.create_index("ix_one_time_code_expires", "one_time_code", ["expires_at"])
    op.create_index("ix_comment_user_created", "comment", ["userid", "createtime"])
    op.create_index("ix_favorite_user", "favorite", ["userid", "canceled"])
    op.create_index("ix_log_category_target", "log", ["category", "target"])


def downgrade():
    op.drop_index("ix_log_category_target", table_name="log")
    op.drop_index("ix_favorite_user", table_name="favorite")
    op.drop_index("ix_comment_user_created", table_name="comment")
    op.drop_index("ix_one_time_code_expires", table_name="one_time_code")
    op.drop_table("one_time_code")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("session_version")
