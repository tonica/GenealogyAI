from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

# SQLite requiere este flag para permitir el uso desde varios hilos
# (los tests y la aplicacion web comparten el mismo engine).
connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """Base declarativa de SQLAlchemy 2.0 para todos los modelos."""


def get_db() -> Generator[Session, None, None]:
    """Dependencia FastAPI que provee una sesion por request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
