"""Gestió del motor, les sessions i la Base declarativa.

S'encarrega de:
  - Crear l'engine (exactament un cop) configurat segons la URL de la base
    de dades.
  - Aplicar els PRAGMA de rendiment/fiabilitat quan la base es SQLite.
  - Proporcionar la dependència FastAPI `get_db` per obrir/commitejar/tancar
    una sessió per request.
"""

from __future__ import annotations

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite requereix aquest flag per permetre l'ús des de diversos threads
# (els tests i l'aplicació web comparteixen el mateix engine).
_connect_args = (
    {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
)


def _configure_sqlite_pragmas(dbapi_connection, _connection_record) -> None:
    """Activa pragmas de rendiment/fiabilitat per a cada connexió SQLite.

    - `journal_mode`: WAL (Write-Ahead Logging) millora la concorrencia
      lectors/escriptors i tolera talls de digestió.
    - `foreign_keys`: garanteix la integritat referencial.
    - `synchronous`: NORMAL és un bon compromis entre durabilitat i
      rendiment sota WAL.
    - `cache_size`: reserva més pàgines a memoria per als índex.
    - `temp_store`: manté les taules temporals (incloses les usades per
      ORDER BY/GROUP BY) a memoria en lloc de disc.
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-16384")  # amplia la cache de pàgines
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


engine = create_engine(
    settings.database_url,
    connect_args=_connect_args,
    pool_pre_ping=settings.database.pool_pre_ping,
)

if settings.database_url.startswith("sqlite"):
    event.listens_for(engine, "connect")(_configure_sqlite_pragmas)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy 2.0 per a tots els models."""


def get_db() -> Generator[Session, None, None]:
    """Dependència FastAPI que proveeix una sessió per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
