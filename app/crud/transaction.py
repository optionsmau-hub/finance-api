"""Operaciones de base de datos para Transaccion (capa CRUD).

Todas las consultas filtran por `owner_id`: un usuario nunca ve ni modifica
movimientos de otro, aunque adivine el id.
"""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.transaction import Transaction, TransactionType
from app.schemas.transaction import TransactionCreate, TransactionUpdate


def get(db: Session, transaction_id: int, owner_id: int) -> Transaction | None:
    stmt = select(Transaction).where(
        Transaction.id == transaction_id, Transaction.owner_id == owner_id
    )
    return db.scalar(stmt)


def list_(
    db: Session,
    owner_id: int,
    *,
    category_id: int | None = None,
    type: TransactionType | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    skip: int = 0,
    limit: int = 100,
) -> list[Transaction]:
    """Lista movimientos del usuario, del mas reciente al mas antiguo."""
    stmt = select(Transaction).where(Transaction.owner_id == owner_id)

    if category_id is not None:
        stmt = stmt.where(Transaction.category_id == category_id)
    if type is not None:
        stmt = stmt.where(Transaction.type == type)
    if date_from is not None:
        stmt = stmt.where(Transaction.occurred_on >= date_from)
    if date_to is not None:
        stmt = stmt.where(Transaction.occurred_on <= date_to)

    stmt = stmt.order_by(Transaction.occurred_on.desc(), Transaction.id.desc())
    stmt = stmt.offset(skip).limit(limit)
    return list(db.scalars(stmt))


def exists_for_category(db: Session, category_id: int, owner_id: int) -> bool:
    stmt = (
        select(Transaction.id)
        .where(Transaction.category_id == category_id, Transaction.owner_id == owner_id)
        .limit(1)
    )
    return db.scalar(stmt) is not None


def create(db: Session, data: TransactionCreate, owner_id: int) -> Transaction:
    transaction = Transaction(**data.model_dump(), owner_id=owner_id)
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction


def update(db: Session, transaction: Transaction, data: TransactionUpdate) -> Transaction:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    db.commit()
    db.refresh(transaction)
    return transaction


def delete(db: Session, transaction: Transaction) -> None:
    db.delete(transaction)
    db.commit()
