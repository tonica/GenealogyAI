"""Interfícies de repositoris de domínio.

Els serveis d'aplicació i de domínio depen només d'aquestes contractes
(ABC), mai de les implementacions SQLAlchemy. Això desacople el domínio de
la infraestructura i permet canviar de base de dades (PostgreSQL, Neo4j...)
sense tocar la lògica.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from app.domain.entities import Family, Person, Place

T = TypeVar("T")


class BaseRepositoryInterface(ABC, Generic[T]):
    """Interface comuna per a quals-repositori."""

    @abstractmethod
    def get(self, entity_id: int) -> T | None: ...

    @abstractmethod
    def add(self, entity: T) -> T: ...

    @abstractmethod
    def delete(self, entity: T) -> None: ...


class PersonRepositoryInterface(BaseRepositoryInterface[Person]):
    """Operacions de repository accessibles al domínio per a `Person`."""

    @abstractmethod
    def get_by_xref(self, xref: str) -> Person | None: ...

    @abstractmethod
    def get_by_uuid(self, uuid: str) -> Person | None: ...

    @abstractmethod
    def search(
        self,
        q: str | None = None,
        sex: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Person]: ...

    @abstractmethod
    def count(self) -> int: ...


class FamilyRepositoryInterface(BaseRepositoryInterface[Family]):
    """Interface per a `Family`."""

    @abstractmethod
    def get_by_xref(self, xref: str) -> Family | None: ...

    @abstractmethod
    def count(self) -> int: ...


class PlaceRepositoryInterface(BaseRepositoryInterface[Place]):
    """Interface per a `Place`."""

    @abstractmethod
    def get_by_canonical_name(self, canonical: str) -> Place | None: ...

    @abstractmethod
    def get_by_name(self, name: str) -> Place | None: ...

    @abstractmethod
    def count(self) -> int: ...


__all__ = [
    "BaseRepositoryInterface",
    "PersonRepositoryInterface",
    "FamilyRepositoryInterface",
    "PlaceRepositoryInterface",
]
