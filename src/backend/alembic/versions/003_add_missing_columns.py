"""add missing columns

Revision ID: 003
Revises: 002
Create Date: 2026-05-16

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # items.low_stock_threshold - may already exist from prior debug endpoint
    op.add_column(
        "items",
        sa.Column(
            "low_stock_threshold", sa.Integer(), nullable=False, server_default="5"
        ),
    )

    # admin_users password reset columns
    op.add_column(
        "admin_users",
        sa.Column("password_reset_token", sa.String(255), nullable=True),
    )
    op.add_column(
        "admin_users",
        sa.Column(
            "password_reset_expires",
            sa.DateTime(timezone=True),
            nullable=True,
        ),
    )

    # admin_audit_logs table
    op.create_table(
        "admin_audit_logs",
        sa.Column(
            "id",
            sa.UUID(),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "admin_user_id",
            sa.UUID(),
            sa.ForeignKey("admin_users.id"),
            nullable=False,
        ),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("target_type", sa.String(50), nullable=False),
        sa.Column("target_id", sa.String(100), nullable=False),
        sa.Column("old_value", sa.JSON(), nullable=True),
        sa.Column("new_value", sa.JSON(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_table("admin_audit_logs")
    op.drop_column("admin_users", "password_reset_expires")
    op.drop_column("admin_users", "password_reset_token")
    op.drop_column("items", "low_stock_threshold")
