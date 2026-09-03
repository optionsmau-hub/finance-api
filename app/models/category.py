"""Modelo: Categoria de gasto/ingreso (ej. Comida, Transporte, Salario)."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    description: Mapped[str | None] = mapped_column(String(255), default=None)

    # Una categoria tiene muchas transacciones. No usamos cascade de borrado:
    # la FK esta como RESTRICT, asi que no se puede borrar una categoria que
    # todavia tenga movimientos (eso se valida en el endpoint con un 409).
    transactions: Mapped[list[Transaction]] = relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"
