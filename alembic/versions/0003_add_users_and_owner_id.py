"""add users and owner_id

Revision ID: 0003
Revises: 0002
Create Date: 2026-09-04
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("(CURRENT_TIMESTAMP)"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    with op.batch_alter_table("categories", schema=None) as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=False))
        # El nombre ya no es unico globalmente, solo por usuario.
        batch_op.drop_index("ix_categories_name")
        batch_op.create_index("ix_categories_name", ["name"], unique=False)
        batch_op.create_index("ix_categories_owner_id", ["owner_id"], unique=False)
        batch_op.create_unique_constraint(
            "uq_categories_owner_name", ["owner_id", "name"]
        )
        batch_op.create_foreign_key(
            "fk_categories_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    with op.batch_alter_table("transactions", schema=None) as batch_op:
        batch_op.add_column(sa.Column("owner_id", sa.Integer(), nullable=False))
        batch_op.create_index("ix_transactions_owner_id", ["owner_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_transactions_owner_id_users",
            "users",
            ["owner_id"],
            ["id"],
            ondelete="RESTRICT",
        )


def downgrade() -> None:
    with op.batch_alter_table("transactions", schema=None) as batch_op:
        batch_op.drop_constraint("fk_transactions_owner_id_users", type_="foreignkey")
        batch_op.drop_index("ix_transactions_owner_id")
        batch_op.drop_column("owner_id")

    with op.batch_alter_table("categories", schema=None) as batch_op:
        batch_op.drop_constraint("fk_categories_owner_id_users", type_="foreignkey")
        batch_op.drop_constraint("uq_categories_owner_name", type_="unique")
        batch_op.drop_index("ix_categories_owner_id")
        batch_op.drop_index("ix_categories_name")
        batch_op.create_index("ix_categories_name", ["name"], unique=True)
        batch_op.drop_column("owner_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
