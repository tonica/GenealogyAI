"""Capa de domínio (Hexagonal Architecture).

El domínio és el nucli de la lògica de negoci, totalment independent de
qualsevol tecnologia (SQLAlchemy, Pydantic, FastAPI, SQLite). Les capes
externes (application, infrastructure) depenen d'ell; mai al revés.
"""

from app.domain import entities, value_objects  # noqa: F401
from app.domain.exceptions import ConflictError, DomainError  # noqa: F401
from app.domain.exceptions import DuplicateEntityError, EntityNotFoundError

__all__ = [
    "DomainError",
    "DuplicateEntityError",
    "EntityNotFoundError",
    "ConflictError",
    "entities",
    "exceptions",
    "value_objects",
]
