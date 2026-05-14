# backend/alembic/versions/001_init_schema.py
"""init schema

Revision ID: 001
Revises:
Create Date: 2026-05-14

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # categories
    op.create_table(
        "categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("name_zh", sa.String(100), nullable=False),
        sa.Column("name_en", sa.String(100), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_categories_active", "categories", ["is_active"])
    op.create_index("ix_categories_sort", "categories", ["sort_order"])

    # items
    op.create_table(
        "items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "category_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("categories.id"),
            nullable=False,
        ),
        sa.Column("name_zh", sa.String(200), nullable=False),
        sa.Column("name_en", sa.String(200), nullable=False),
        sa.Column("description_zh", sa.Text(), nullable=True),
        sa.Column("description_en", sa.Text(), nullable=True),
        sa.Column("price_sgd", sa.Numeric(10, 2), nullable=False),
        sa.Column("image_url", sa.String(500), nullable=True),
        sa.Column(
            "options_config", postgresql.JSONB(), nullable=False, server_default="{}"
        ),
        sa.Column("is_available", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("stock", sa.Integer(), nullable=True),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_items_category", "items", ["category_id"])
    op.create_index("ix_items_available", "items", ["is_available", "is_active"])
    op.create_index(
        "ix_items_stock",
        "items",
        ["stock"],
        postgresql_where=sa.text("stock IS NOT NULL"),
    )

    # seats
    op.create_table(
        "seats",
        sa.Column("id", sa.String(10), primary_key=True),
        sa.Column("label_zh", sa.String(50), nullable=False),
        sa.Column("label_en", sa.String(50), nullable=False),
        sa.Column("zone", sa.String(20), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="vacant"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "status IN ('vacant','occupied','reserved','inactive')",
            name="ck_seats_status",
        ),
    )
    op.create_index("ix_seats_zone", "seats", ["zone"])
    op.create_index("ix_seats_status", "seats", ["status"])

    # orders
    op.create_table(
        "orders",
        sa.Column("id", sa.String(20), primary_key=True),
        sa.Column("seat_id", sa.String(10), sa.ForeignKey("seats.id"), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="submitted"),
        sa.Column(
            "payment_status", sa.String(20), nullable=False, server_default="pending"
        ),
        sa.Column("payment_method", sa.String(30), nullable=True),
        sa.Column("payment_intent_id", sa.String(200), nullable=True),
        sa.Column("subtotal_sgd", sa.Numeric(10, 2), nullable=False),
        sa.Column("tax_sgd", sa.Numeric(10, 2), nullable=False),
        sa.Column("total_sgd", sa.Numeric(10, 2), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("customer_notes", sa.Text(), nullable=True),
        sa.Column("rejected_reason", sa.String(200), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("cancelled_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('submitted','confirmed','preparing','ready','completed','cancelled','rejected')",
            name="ck_orders_status",
        ),
        sa.CheckConstraint(
            "payment_status IN ('pending','paid','failed','refunded','cancelled')",
            name="ck_orders_payment_status",
        ),
    )
    op.create_index("ix_orders_seat", "orders", ["seat_id"])
    op.create_index("ix_orders_status", "orders", ["status"])
    op.create_index("ix_orders_payment", "orders", ["payment_status"])
    op.create_index("ix_orders_created", "orders", [sa.text("created_at DESC")])

    # order_items
    op.create_table(
        "order_items",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column(
            "order_id",
            sa.String(20),
            sa.ForeignKey("orders.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("items.id"),
            nullable=False,
        ),
        sa.Column("item_name_zh", sa.String(200), nullable=False),
        sa.Column("item_name_en", sa.String(200), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("options", postgresql.JSONB(), nullable=False, server_default="{}"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("print_group", sa.String(20), server_default="drink"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_order_items_order", "order_items", ["order_id"])

    # payment_transactions
    op.create_table(
        "payment_transactions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
        sa.Column("order_id", sa.String(20), nullable=False),
        sa.Column("stripe_payment_intent", sa.String(200), nullable=True),
        sa.Column("paynow_reference", sa.String(100), nullable=True),
        sa.Column("amount_sgd", sa.Numeric(10, 2), nullable=False),
        sa.Column("currency", sa.String(3), nullable=False, server_default="SGD"),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("payment_method", sa.String(30), nullable=True),
        sa.Column("failure_code", sa.String(50), nullable=True),
        sa.Column("failure_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_pt_order", "payment_transactions", ["order_id"])
    op.create_index(
        "ix_pt_payment_intent", "payment_transactions", ["stripe_payment_intent"]
    )


def downgrade() -> None:
    op.drop_table("payment_transactions")
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("seats")
    op.drop_table("items")
    op.drop_table("categories")
