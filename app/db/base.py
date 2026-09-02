"""Clase base para todos los modelos ORM.

Todos los modelos heredan de `Base`, y `Base.metadata` contiene la definicion
de todas las tablas (lo usan Alembic y los tests para crear el esquema).
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass
