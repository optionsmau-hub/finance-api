"""Endpoints de reportes: datos calculados a partir de las transacciones
(y de los presupuestos, en el caso de budget-status). Ninguno modifica
datos, todos son GET.
"""

from decimal import Decimal

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.dates import MONTH_PATTERN, month_bounds
from app.crud import report as crud
from app.models.transaction import TransactionType
from app.models.user import User
from app.schemas.report import BudgetStatus, CategoryTotal, MonthlySummary

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=MonthlySummary)
def summary(
    month: str = Query(pattern=MONTH_PATTERN, examples=["2026-09"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    date_from, date_to = month_bounds(month)
    totals = crud.monthly_totals(db, owner_id=current_user.id, date_from=date_from, date_to=date_to)
    income = totals[TransactionType.income]
    expense = totals[TransactionType.expense]
    return MonthlySummary(
        month=month,
        total_income=income,
        total_expense=expense,
        balance=income - expense,
    )


@router.get("/by-category", response_model=list[CategoryTotal])
def by_category(
    month: str = Query(pattern=MONTH_PATTERN, examples=["2026-09"]),
    type: TransactionType | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    date_from, date_to = month_bounds(month)
    rows = crud.totals_by_category(
        db, owner_id=current_user.id, date_from=date_from, date_to=date_to, type=type
    )
    return [
        CategoryTotal(category_id=cid, category_name=name, total=total) for cid, name, total in rows
    ]


@router.get("/budget-status", response_model=list[BudgetStatus])
def budget_status(
    month: str = Query(pattern=MONTH_PATTERN, examples=["2026-09"]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    date_from, date_to = month_bounds(month)
    spent_by_category = crud.spent_by_category_map(
        db, owner_id=current_user.id, date_from=date_from, date_to=date_to
    )
    budgets = crud.budgets_with_category_name(db, owner_id=current_user.id, month=month)

    result = []
    for budget, category_name in budgets:
        spent: Decimal = spent_by_category.get(budget.category_id, Decimal("0"))
        result.append(
            BudgetStatus(
                category_id=budget.category_id,
                category_name=category_name,
                month=month,
                limit_amount=budget.limit_amount,
                spent=spent,
                remaining=budget.limit_amount - spent,
                over_budget=spent > budget.limit_amount,
            )
        )
    return result
