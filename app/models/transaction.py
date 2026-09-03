"""Modelo: Transaccion (un ingreso o un gasto)."""

from __future__ import annotations

import enum
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.category import Category


class TransactionType(enum.StrEnum):
    """Tipo de movimiento: entra dinero (income) o sale dinero (expense)."""

    income = "income"
    expense = "expense"


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Numeric(12, 2): hasta 10 digitos enteros y 2 decimales. Se mapea a Decimal
    # en Python para no perder precision con el dinero (nunca usar float).
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    type: Mapped[TransactionType] = mapped_column(
        SAEnum(TransactionType, name="transaction_type"), index=True
    )

    # Fecha en que ocurrio el movimiento (la elige el usuario).
    occurred_on: Mapped[date] = mapped_column(Date, index=True)

    note: Mapped[str | None] = mapped_column(String(255), default=None)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True
    )

    # Fecha/hora en que se registro la fila (la pone la base de datos).
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category: Mapped[Category] = relationship(back_populates="transactions")

    def __repr__(self) -> str:
        return f"<Transaction id={self.id} type={self.type} amount={self.amount}>"
