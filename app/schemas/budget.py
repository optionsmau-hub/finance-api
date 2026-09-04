"""Schemas Pydantic para la entidad Budget (presupuesto)."""

from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.core.dates import MONTH_PATTERN


class BudgetBase(BaseModel):
    category_id: int
    month: str = Field(pattern=MONTH_PATTERN, examples=["2026-09"])
    limit_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetCreate(BudgetBase):
    """Datos necesarios para crear un presupuesto."""


class BudgetUpdate(BaseModel):
    """Solo se puede ajustar el monto: la categoria y el mes son la identidad
    del presupuesto (para cambiarlos, se borra y se crea uno nuevo)."""

    limit_amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2)


class BudgetRead(BudgetBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
