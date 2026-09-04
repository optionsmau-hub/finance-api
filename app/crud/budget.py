"""Operaciones de base de datos para Budget (presupuesto)."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.schemas.budget import BudgetCreate, BudgetUpdate


def get(db: Session, budget_id: int, owner_id: int) -> Budget | None:
    stmt = select(Budget).where(Budget.id == budget_id, Budget.owner_id == owner_id)
    return db.scalar(stmt)


def get_by_category_month(
    db: Session, category_id: int, month: str, owner_id: int
) -> Budget | None:
    stmt = select(Budget).where(
        Budget.category_id == category_id,
        Budget.month == month,
        Budget.owner_id == owner_id,
    )
    return db.scalar(stmt)


def list_(
    db: Session, owner_id: int, month: str | None = None, skip: int = 0, limit: int = 100
) -> list[Budget]:
    stmt = select(Budget).where(Budget.owner_id == owner_id)
    if month is not None:
        stmt = stmt.where(Budget.month == month)
    stmt = stmt.order_by(Budget.month.desc(), Budget.id).offset(skip).limit(limit)
    return list(db.scalars(stmt))


def create(db: Session, data: BudgetCreate, owner_id: int) -> Budget:
    budget = Budget(**data.model_dump(), owner_id=owner_id)
    db.add(budget)
    db.commit()
    db.refresh(budget)
    return budget


def update(db: Session, budget: Budget, data: BudgetUpdate) -> Budget:
    budget.limit_amount = data.limit_amount
    db.commit()
    db.refresh(budget)
    return budget


def delete(db: Session, budget: Budget) -> None:
    db.delete(budget)
    db.commit()
