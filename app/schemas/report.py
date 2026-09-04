"""Schemas Pydantic para los reportes (datos calculados, no una tabla)."""

from decimal import Decimal

from pydantic import BaseModel


class MonthlySummary(BaseModel):
    month: str
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class CategoryTotal(BaseModel):
    category_id: int
    category_name: str
    total: Decimal


class BudgetStatus(BaseModel):
    category_id: int
    category_name: str
    month: str
    limit_amount: Decimal
    spent: Decimal
    remaining: Decimal
    over_budget: bool
