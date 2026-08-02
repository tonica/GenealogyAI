"""Modelos ORM de SQLAlchemy 2.0.

La importacio d'aquest mòdul registra tots els models a `Base.metadata`,
necessari per als autogenerate d'Alembic i per al schema de test.
"""

from app.models.event import Event
from app.models.family import Family
from app.models.media import Media
from app.models.parent_child import ParentChild
from app.models.person import Person
from app.models.place import Place
from app.models.source import Source
from app.models.suggestion import Suggestion

__all__ = [
    "Event",
    "Family",
    "Media",
    "ParentChild",
    "Person",
    "Place",
    "Source",
    "Suggestion",
]
