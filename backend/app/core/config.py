from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuracion global de la aplicacion."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Aplicacion ---
    APP_NAME: str = "GenealogyAI"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False

    # --- Base de datos ---
    # Por defecto apuntamos a la ruta que usa el contenedor Docker.
    # En desarrollo local sin contenedor puede sobreescribirse con una
    # variable de entorno DATABASE_URL.
    DATABASE_URL: str = "sqlite+pysqlite:////data/genealogyai.db"

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia unica (cacheada) de la configuracion."""
    return Settings()
