"""Configuració centralitzada de l'aplicació (Pydantic Settings).

Agrupa i tipa la configuració per dominis (database, logging, import,
search, ai) i permet sobreescriure-la amb variables d'entorn i un `.env`.
`get_settings()` cacheja la instància per reutilitzar-la a tota l'app.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    """Configuració de la connexió a la base de dades."""

    url: str = "sqlite+pysqlite:////data/genealogyai.db"
    # Paràmetres de rendiment/fiabilitat de SQLite (només s'apliquen quan
    # la URL és SQLite; els motors externs ignoren aquests pragmas).
    pool_pre_ping: bool = True


class LoggingSettings(BaseSettings):
    """Configuració del registre (logging)."""

    level: str = "INFO"
    # Format del log; 'json' produeix línies JSON estructurades.
    format: str = "text"  # 'text' | 'json'
    file: str | None = None


class ImportSettings(BaseSettings):
    """Configuració de la importació GEDCOM."""

    # Maxima mida (bytes) d'un fitxer admes (30 MB per defecte).
    max_file_size: int = 30 * 1024 * 1024
    # Si cal reconstruir l'índex de cerca després d'una importació.
    rebuild_search_index: bool = True


class SearchSettings(BaseSettings):
    """Configuració del motor de cerca (FTS5)."""

    fts_table: str = "person_fts"
    # Inclou cognom i nom en l'índex.
    include_surname_prefix: bool = True
    # Nombre màxim de resultats per consulta.
    default_limit: int = 50


class AiSettings(BaseSettings):
    """Configuració futura del motor d'IA (reservada; no usada encara)."""

    enabled: bool = False
    provider: str = "none"
    api_endpoint: str | None = None


class Settings(BaseSettings):
    """Configuració global agrupada per dominis."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
        env_nested_delimiter="__",
    )

    # --- Aplicació ---
    APP_NAME: str = "GenealogyAI"
    APP_VERSION: str = "0.2.0"
    DEBUG: bool = False

    # --- CORS ---
    CORS_ORIGINS: list[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    # --- Agrupacions ---
    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    logging: LoggingSettings = Field(default_factory=LoggingSettings)
    import_: ImportSettings = Field(default_factory=ImportSettings)
    search: SearchSettings = Field(default_factory=SearchSettings)
    ai: AiSettings = Field(default_factory=AiSettings)

    # Atributs d'accés ràpid que mantenen compatibilitat amb l'antic
    # `Settings` (camps plans) usats per Alembic i els tests.
    DATABASE_URL: str = "sqlite+pysqlite:////data/genealogyai.db"

    @property
    def database_url(self) -> str:
        return self.database.url or self.DATABASE_URL


@lru_cache
def get_settings() -> Settings:
    """Devuelve una instancia unica (cacheada) de la configuración."""
    return Settings()
