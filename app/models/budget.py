"""Modelo: Presupuesto (limite de gasto de una categoria en un mes)."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Budget(Base):
    __tablename__ = "budgets"
    # Un solo presupuesto por categoria y mes (por usuario). Si quieres
    # cambiar el limite, se actualiza el que ya existe (PATCH).
    __table_args__ = (
        UniqueConstraint(
            "owner_id", "category_id", "month", name="uq_budgets_owner_category_month"
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    # Si se borra la categoria (solo se puede si no tiene movimientos), su
    # presupuesto ya no tiene sentido: se borra junto con ella.
    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), index=True)

    # "YYYY-MM". Se guarda como texto porque solo nos interesa el mes, no un
    # dia exacto, y como es un formato de ancho fijo se puede ordenar y
    # comparar igual que si fuera una fecha.
    month: Mapped[str] = mapped_column(String(7), index=True)

    limit_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    def __repr__(self) -> str:
        return f"<Budget category_id={self.category_id} month={self.month}>"
