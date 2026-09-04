"""Operaciones de base de datos para Categoria (capa CRUD).

Todas las consultas filtran por `owner_id`: un usuario nunca ve ni modifica
categorias de otro, aunque adivine el id.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate


def get(db: Session, category_id: int, owner_id: int) -> Category | None:
    stmt = select(Category).where(Category.id == category_id, Category.owner_id == owner_id)
    return db.scalar(stmt)


def get_by_name(db: Session, name: str, owner_id: int) -> Category | None:
    stmt = select(Category).where(Category.name == name, Category.owner_id == owner_id)
    return db.scalar(stmt)


def list_all(db: Session, owner_id: int, skip: int = 0, limit: int = 100) -> list[Category]:
    stmt = (
        select(Category)
        .where(Category.owner_id == owner_id)
        .order_by(Category.id)
        .offset(skip)
        .limit(limit)
    )
    return list(db.scalars(stmt))


def create(db: Session, data: CategoryCreate, owner_id: int) -> Category:
    category = Category(**data.model_dump(), owner_id=owner_id)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


def update(db: Session, category: Category, data: CategoryUpdate) -> Category:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(category, field, value)
    db.commit()
    db.refresh(category)
    return category


def delete(db: Session, category: Category) -> None:
    db.delete(category)
    db.commit()
