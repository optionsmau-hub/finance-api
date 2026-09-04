"""Endpoints REST para Presupuestos."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db
from app.core.dates import MONTH_PATTERN
from app.crud import budget as crud
from app.crud import category as category_crud
from app.models.user import User
from app.schemas.budget import BudgetCreate, BudgetRead, BudgetUpdate

router = APIRouter(prefix="/budgets", tags=["budgets"])


def _budget_not_found() -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Presupuesto no encontrado",
    )


@router.get("", response_model=list[BudgetRead])
def list_budgets(
    month: str | None = Query(default=None, pattern=MONTH_PATTERN),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return crud.list_(db, owner_id=current_user.id, month=month)


@router.post("", response_model=BudgetRead, status_code=status.HTTP_201_CREATED)
def create_budget(
    payload: BudgetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if category_crud.get(db, payload.category_id, owner_id=current_user.id) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"La categoria {payload.category_id} no existe",
        )
    existing = crud.get_by_category_month(
        db, payload.category_id, payload.month, owner_id=current_user.id
    )
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe un presupuesto para esa categoria en ese mes",
        )
    return crud.create(db, payload, owner_id=current_user.id)


@router.get("/{budget_id}", response_model=BudgetRead)
def get_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = crud.get(db, budget_id, owner_id=current_user.id)
    if budget is None:
        raise _budget_not_found()
    return budget


@router.patch("/{budget_id}", response_model=BudgetRead)
def update_budget(
    budget_id: int,
    payload: BudgetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = crud.get(db, budget_id, owner_id=current_user.id)
    if budget is None:
        raise _budget_not_found()
    return crud.update(db, budget, payload)


@router.delete("/{budget_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    budget = crud.get(db, budget_id, owner_id=current_user.id)
    if budget is None:
        raise _budget_not_found()
    crud.delete(db, budget)
