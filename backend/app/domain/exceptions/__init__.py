"""Excepcions de domini compartides per tot el sistema.

El domini no llencen excepcions d'infraestructura (SQLAlchemy, HTTP...).
Aquestes excepcions de domini fan de llindar entre les capes.
"""

from __future__ import annotations


class DomainError(Exception):
    """Error base de totes les excepcions de domínio."""


class EntityNotFoundError(DomainError):
    """Una entitat demanada no s'ha trobat."""


class DuplicateEntityError(DomainError):
    """Es vol crear una entitat que ja existeix (clau duplicada)."""


class InvalidOperationError(DomainError):
    """L'operació sol·licitada no és vàlida per al mateix domini."""


class ConflictError(DomainError):
    """Conflicte d'integritat o de regla de negoci (per ex. merge)."""
