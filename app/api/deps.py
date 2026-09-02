"""Dependencias compartidas de la API.

Por ahora solo re-exporta `get_db`. Cuando agreguemos autenticacion,
aqui viviran cosas como `get_current_user`.
"""

from app.db.session import get_db

__all__ = ["get_db"]
