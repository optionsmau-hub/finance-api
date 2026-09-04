"""Dependencias compartidas de la API."""

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.crud import user as user_crud
from app.db.session import get_db
from app.models.user import User

__all__ = ["get_db", "get_current_user"]

# tokenUrl le dice a la documentacion (/docs) donde se consigue el token,
# para que el boton "Authorize" sepa a que endpoint mandar usuario/contraseña.
_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(
    token: str = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Dependencia para proteger un endpoint: exige un token valido y devuelve
    el usuario dueño de ese token. FastAPI la resuelve antes de correr la
    funcion del endpoint; si algo falla, corta con 401 y ni siquiera se llega
    a ejecutar el codigo del endpoint.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar la credencial",
        headers={"WWW-Authenticate": "Bearer"},
    )

    payload = decode_access_token(token)
    if payload is None:
        raise unauthorized

    user_id = payload.get("sub")
    if user_id is None:
        raise unauthorized

    user = user_crud.get(db, int(user_id))
    if user is None:
        raise unauthorized

    return user
