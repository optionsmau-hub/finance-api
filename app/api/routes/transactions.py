"""Endpoints REST para Transacciones (ingresos y gastos)."""

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.crud import category as category_crud
from app.crud import transaction as crud
from app.models.transaction import TransactionType
from app.schemas.transaction import TransactionCreate, TransactionRead, TransactionUpdate

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _transaction_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Movimiento no encontrado",
    )


def _get_category_or_404(db: Session, category_id: int) -> None:
    if category_crud.get(db, category_id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoria {category_id} no existe",
        )


@router.get("", response_model=list[TransactionRead])
def list_transactions(
    db: Session = Depends(get_db),
    category_id: int | None = Query(default=None),
    type: TransactionType | None = Query(default=None),
    date_from: date | None = Query(default=None, description="Fecha minima (YYYY-MM-DD)"),
    date_to: date | None = Query(default=None, description="Fecha maxima (YYYY-MM-DD)"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
):
    return crud.list_(
        db,
        category_id=category_id,
        type=type,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=limit,
    )


@router.post("", response_model=TransactionRead, status_code=status.HTTP_201_CREATED)
def create_transaction(payload: TransactionCreate, db: Session = Depends(get_db)):
    _get_category_or_404(db, payload.category_id)
    return crud.create(db, payload)


@router.get("/{transaction_id}", response_model=TransactionRead)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get(db, transaction_id)
    if transaction is None:
        raise _transaction_not_found()
    return transaction


@router.patch("/{transaction_id}", response_model=TransactionRead)
def update_transaction(
    transaction_id: int, payload: TransactionUpdate, db: Session = Depends(get_db)
):
    transaction = crud.get(db, transaction_id)
    if transaction is None:
        raise _transaction_not_found()
    if payload.category_id is not None:
        _get_category_or_404(db, payload.category_id)
    return crud.update(db, transaction, payload)


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = crud.get(db, transaction_id)
    if transaction is None:
        raise _transaction_not_found()
    crud.delete(db, transaction)
