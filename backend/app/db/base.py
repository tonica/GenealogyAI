"""Punt central on es registren tots els models per a Alembic i els tests."""

from app.db.session import Base
from app.models import (  # noqa: F401 (re-export: registra els models)
    AuditLog,
    Event,
    Family,
    Media,
    ParentChild,
    Person,
    Place,
    Source,
    Suggestion,
)

__all__ = [
    "Base",
    "AuditLog",
    "Person",
    "Family",
    "ParentChild",
    "Place",
    "Event",
    "Source",
    "Media",
    "Suggestion",
]
