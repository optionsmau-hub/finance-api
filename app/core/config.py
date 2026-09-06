"""Configuracion de la aplicacion.

Los valores se leen desde variables de entorno o desde un archivo .env.
Usamos pydantic-settings para tener validacion y tipado automatico.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

_DEV_SECRET = "dev-secret-change-me-in-production-0123456789"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Finance API"
    debug: bool = False

    # Por defecto SQLite para poder arrancar sin instalar nada.
    # En produccion se sobrescribe con una URL de PostgreSQL en el .env.
    database_url: str = "sqlite:///./finance.db"

    # Clave para firmar los JWT. El valor por defecto es SOLO para desarrollo:
    # en produccion se debe sobrescribir con una clave aleatoria en el .env
    # (por ejemplo: python -c "import secrets; print(secrets.token_hex(32))").
    secret_key: str = _DEV_SECRET
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 1 dia

    # Origenes (dominios) que pueden llamar a la API desde un navegador.
    # Coma-separados. "*" = cualquiera (comodo en desarrollo, no en produccion).
    cors_origins: str = "*"

    @model_validator(mode="after")
    def _require_real_secret_in_production(self) -> "Settings":
        """Si NO estamos en modo debug, la clave de desarrollo esta prohibida:
        arrancar produccion con ella seria un agujero de seguridad (cualquiera
        podria fabricar tokens validos). Mejor fallar de una que en silencio.
        """
        if not self.debug and self.secret_key == _DEV_SECRET:
            raise ValueError(
                "SECRET_KEY tiene el valor de desarrollo. Define uno propio en el "
                "entorno para produccion (debug=false)."
            )
        return self

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una unica instancia de Settings (cacheada)."""
    return Settings()


settings = get_settings()
