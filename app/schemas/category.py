"""Schemas Pydantic para la entidad Categoria.

Separan lo que entra por la API (Create/Update) de lo que sale (Read),
y definen la validacion de cada campo.
"""

from pydantic import BaseModel, ConfigDict, Field


class CategoryBase(BaseModel):
    name: str = Field(min_length=1, max_length=80, examples=["Comida"])
    description: str | None = Field(default=None, max_length=255)


class CategoryCreate(CategoryBase):
    """Datos necesarios para crear una categoria."""


class CategoryUpdate(BaseModel):
    """Todos los campos son opcionales: solo se actualiza lo que se envia."""

    name: str | None = Field(default=None, min_length=1, max_length=80)
    description: str | None = Field(default=None, max_length=255)


class CategoryRead(CategoryBase):
    """Representacion que devuelve la API."""

    model_config = ConfigDict(from_attributes=True)

    id: int
