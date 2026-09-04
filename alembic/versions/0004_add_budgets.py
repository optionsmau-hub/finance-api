"""add budgets

Revision ID: 0004
Revises: 0003
Create Date: 2026-09-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "budgets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category_id", sa.Integer(), nullable=False),
        sa.Column("owner_id", sa.Integer(), nullable=False),
        sa.Column("month", sa.String(length=7), nullable=False),
        sa.Column("limit_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["category_id"], ["categories.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "owner_id", "category_id", "month", name="uq_budgets_owner_category_month"
        ),
    )
    op.create_index("ix_budgets_category_id", "budgets", ["category_id"])
    op.create_index("ix_budgets_month", "budgets", ["month"])
    op.create_index("ix_budgets_owner_id", "budgets", ["owner_id"])


def downgrade() -> None:
    op.drop_index("ix_budgets_owner_id", table_name="budgets")
    op.drop_index("ix_budgets_month", table_name="budgets")
    op.drop_index("ix_budgets_category_id", table_name="budgets")
    op.drop_table("budgets")
