"""Consultas de reportes: no son CRUD de una tabla, son datos calculados a
partir de Transaction (y, en el caso de budget-status, tambien de Budget).

Aqui usamos SUM/GROUP BY de SQL en vez de traer las filas y sumarlas en
Python: es el mismo trabajo, pero lo hace la base de datos, que esta
optimizada para eso y no tiene que mandar cada fila por la red.
"""

from datetime import date
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.category import Category
from app.models.transaction import Transaction, TransactionType


def monthly_totals(
    db: Session, owner_id: int, date_from: date, date_to: date
) -> dict[TransactionType, Decimal]:
    """Total de ingresos y de gastos entre dos fechas, en una sola consulta."""
    stmt = (
        select(Transaction.type, func.sum(Transaction.amount))
        .where(
            Transaction.owner_id == owner_id,
            Transaction.occurred_on >= date_from,
            Transaction.occurred_on <= date_to,
        )
        .group_by(Transaction.type)
    )
    totals = dict(db.execute(stmt).all())
    return {
        TransactionType.income: totals.get(TransactionType.income, Decimal("0")),
        TransactionType.expense: totals.get(TransactionType.expense, Decimal("0")),
    }


def totals_by_category(
    db: Session,
    owner_id: int,
    date_from: date,
    date_to: date,
    type: TransactionType | None = None,
) -> list[tuple[int, str, Decimal]]:
    """Gasto (o ingreso) total por categoria, de mayor a menor."""
    stmt = (
        select(Category.id, Category.name, func.sum(Transaction.amount))
        .join(Transaction, Transaction.category_id == Category.id)
        .where(
            Transaction.owner_id == owner_id,
            Transaction.occurred_on >= date_from,
            Transaction.occurred_on <= date_to,
        )
    )
    if type is not None:
        stmt = stmt.where(Transaction.type == type)

    stmt = stmt.group_by(Category.id, Category.name).order_by(func.sum(Transaction.amount).desc())
    return list(db.execute(stmt).all())


def spent_by_category_map(
    db: Session, owner_id: int, date_from: date, date_to: date
) -> dict[int, Decimal]:
    """{category_id: total gastado} en el rango, solo gastos (expense)."""
    rows = totals_by_category(db, owner_id, date_from, date_to, type=TransactionType.expense)
    return {category_id: total for category_id, _name, total in rows}


def budgets_with_category_name(db: Session, owner_id: int, month: str) -> list[tuple[Budget, str]]:
    """Los presupuestos de un mes, junto con el nombre de su categoria."""
    stmt = (
        select(Budget, Category.name)
        .join(Category, Category.id == Budget.category_id)
        .where(Budget.owner_id == owner_id, Budget.month == month)
        .order_by(Category.name)
    )
    return list(db.execute(stmt).all())
