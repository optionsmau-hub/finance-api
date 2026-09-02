"""Configuracion de la aplicacion.

Los valores se leen desde variables de entorno o desde un archivo .env.
Usamos pydantic-settings para tener validacion y tipado automatico.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


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


@lru_cache
def get_settings() -> Settings:
    """Devuelve una unica instancia de Settings (cacheada)."""
    return Settings()


settings = get_settings()
