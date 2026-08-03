"""Cas d'ús: obtenir una persona per ID del domínio."""

from __future__ import annotations

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities import Person
from app.domain.exceptions import EntityNotFoundError
from app.mappers import PersonMapper


class GetPersonUseCase:
    """Retorna una persona convertida al domínio.

    Coordina el repositori (via UnitOfWork) i el mapper; no duu lògica
    de negoci ni toca SQL directament.
    """

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def execute(self, person_id: int) -> Person:
        orm_person = self.uow.persons.get(person_id)
        if orm_person is None:
            raise EntityNotFoundError(f"Persona {person_id} no trobada")
        return PersonMapper.to_domain(orm_person)
