"""Cas d'ús: combinació de persones duplicades (placeholder).

Coordina el detector de duplicats (servei de domínio) amb el repositori i
el UnitOfWork. Només prepara l'arquitectura; la lògica d'edició de
relacions es desenvoluparà més endavant.
"""

from __future__ import annotations

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities import Person
from app.domain.exceptions import ConflictError
from app.domain.services import DuplicateDetector
from app.mappers import PersonMapper


class MergePersonsUseCase:
    """Consolida dues persones candidates a ser la mateixa."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow
        self.detector = DuplicateDetector()

    def detect_candidates(self, q: str | None = None) -> list[list[Person]]:
        """Retorna grups de persones similar (només lectura)."""
        persons = self.uow.persons.search(q=q) if q else self.uow.persons.all()
        domain = [PersonMapper.to_domain(p) for p in persons]
        return [g.persons for g in self.detector.find_duplicates(domain)]

    def merge(self, primary_id: int, secondary_id: int) -> Person:
        """Fusiona `secondary` dins de `primary` (placeholder básico).

        Aquesta versió només valida i marca; la fusió real de relacions i
        mitjà vindrà en un sprint futur de qualitat de dades.
        """
        if primary_id == secondary_id:
            raise ConflictError("No es pot fusionar una persona amb si mateixa")

        primary = self.uow.persons.get(primary_id)
        secondary = self.uow.persons.get(secondary_id)
        if primary is None or secondary is None:
            raise ConflictError("Una de les persones no existeix")

        if (primary.xref or "").upper() == (secondary.xref or "").upper():
            raise ConflictError("xref duplicat; revisa la coherència")

        # Mantenim primary i descartem secondary (placeholder).
        self.uow.persons.delete(secondary)
        self.uow.commit()
        return PersonMapper.to_domain(primary)
