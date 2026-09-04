"""Schemas Pydantic para la entidad Transaccion."""

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.transaction import TransactionType


class TransactionBase(BaseModel):
    # El monto siempre es positivo; el signo lo da el `type` (income/expense).
    amount: Decimal = Field(gt=0, max_digits=12, decimal_places=2, examples=["12.50"])
    type: TransactionType
    occurred_on: date
    note: str | None = Field(default=None, max_length=255)
    category_id: int


class TransactionCreate(TransactionBase):
    """Datos necesarios para registrar un movimiento."""


class TransactionUpdate(BaseModel):
    """Todos los campos opcionales: solo se actualiza lo que se envia."""

    amount: Decimal | None = Field(default=None, gt=0, max_digits=12, decimal_places=2)
    type: TransactionType | None = None
    occurred_on: date | None = None
    note: str | None = Field(default=None, max_length=255)
    category_id: int | None = None


class TransactionRead(TransactionBase):
    """Representacion que devuelve la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
