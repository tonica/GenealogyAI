"""UnitOfWork: gestió de transaccions i repositoris.

CAP layer (application) que coordina repositoris sobre una sessió única.
Garanteix que cap servei faci `commit()` directament: tot passa per aquí.
Depend de les interfícies de domínio, de manera que es pot substituir la
persistència (PostgreSQL/Neo4j) sense tocar la lògica d'aplicació.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Iterator, TypeVar

from app.domain.interfaces import FamilyRepositoryInterface
from app.domain.interfaces import PersonRepositoryInterface
from app.domain.interfaces import PlaceRepositoryInterface

PersonRepo = TypeVar("PersonRepo")
FamilyRepo = TypeVar("FamilyRepo")
PlaceRepo = TypeVar("PlaceRepo")


class AbstractUnitOfWork(ABC):
    """Contracte d'UnitOfWork (per test i per a implementacions futures)."""

    persons: PersonRepositoryInterface
    families: FamilyRepositoryInterface
    places: PlaceRepositoryInterface

    @abstractmethod
    def commit(self) -> None: ...

    @abstractmethod
    def rollback(self) -> None: ...

    @abstractmethod
    def __enter__(self) -> "AbstractUnitOfWork": ...

    @abstractmethod
    def __exit__(self, *args: object) -> None: ...


class UnitOfWork(AbstractUnitOfWork):
    """Unit of Work SQLAlchemy concreto.

    `session` prové de `SessionLocal()`; la dependència `get_db` de
    FastAPI obre la sessió i la delega aquí.
    """

    def __init__(
        self,
        session: object,
        person_cls: type | None = None,
        family_cls: type | None = None,
        place_cls: type | None = None,
    ) -> None:
        self._session = session
        from app.repositories import FamilyRepository as _FImpl
        from app.repositories import PersonRepository as _PImpl
        from app.repositories import PlaceRepository as _PLImpl

        self.persons = (person_cls or _PImpl)(session)
        self.families = (family_cls or _FImpl)(session)
        self.places = (place_cls or _PLImpl)(session)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, *exc_type: object) -> None:
        exc = exc_type[0] if exc_type else None
        if exc is not None:
            self.rollback()
        self._session.close()


@contextmanager
def transaction(uow: AbstractUnitOfWork) -> Iterator[AbstractUnitOfWork]:
    """Context manager que fa commit al sortir sense excepció."""
    with uow:
        yield uow
        uow.commit()


__all__ = ["AbstractUnitOfWork", "UnitOfWork", "transaction"]
