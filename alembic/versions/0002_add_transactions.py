"""add transactions

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-03
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0002"
down_revision: str | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "type",
            sa.Enum("income", "expense", name="transaction_type"),
            nullable=False,
        ),
        sa.Column("occurred_on", sa.Date(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_transactions_category_id", "transactions", ["category_id"])
    op.create_index("ix_transactions_occurred_on", "transactions", ["occurred_on"])
    op.create_index("ix_transactions_type", "transactions", ["type"])


def downgrade() -> None:
    op.drop_index("ix_transactions_type", table_name="transactions")
    op.drop_index("ix_transactions_occurred_on", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_table("transactions")
    # En PostgreSQL el tipo ENUM queda registrado aparte y hay que borrarlo.
    # En SQLite esto no hace nada.
    sa.Enum(name="transaction_type").drop(op.get_bind(), checkfirst=True)
