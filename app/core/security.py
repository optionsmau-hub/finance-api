"""Hash de contraseñas y creacion/verificacion de tokens JWT.

Nunca guardamos la contraseña del usuario tal cual: guardamos un "hash"
(bcrypt), que es un resultado de un solo sentido -- no se puede revertir
para recuperar la contraseña original. Al hacer login, se vuelve a hashear
lo que el usuario escribio y se compara contra el hash guardado.
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
import jwt

from app.core.config import settings


def hash_password(plain_password: str) -> str:
    hashed = bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))


def create_access_token(subject: str) -> str:
    """Genera un JWT cuyo `sub` (subject) es el id del usuario, como texto."""
    expires_at = datetime.now(UTC) + timedelta(minutes=settings.access_token_expire_minutes)
    payload = {"sub": subject, "exp": expires_at}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_access_token(token: str) -> dict[str, Any] | None:
    """Verifica la firma y la expiracion. Devuelve None si el token es invalido."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except jwt.PyJWTError:
        return None
