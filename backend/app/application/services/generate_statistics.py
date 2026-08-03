"""Cas d'ús: genera estadístiques de domín d'un conjunt de persones."""

from __future__ import annotations

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities import Event, Family, Person
from app.domain.services import DomainStats, StatisticsEngine
from app.mappers import EventMapper, FamilyMapper, PersonMapper


class GenerateStatisticsUseCase:
    """Calcula estadístiques usant StatisticsEngine (servei de domínio)."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow
        self.engine = StatisticsEngine()

    def execute(self, limit: int = 5000) -> DomainStats:
        persons_orm = self.uow.persons.all()[:limit]
        families_orm = self.uow.families.all()

        persons: list[Person] = [PersonMapper.to_domain(p) for p in persons_orm]
        families: list[Family] = [FamilyMapper.to_domain(f) for f in families_orm]

        events: list[Event] = []
        for orm in persons_orm:
            events.extend(
                EventMapper.to_domain(e) for e in getattr(orm, "events", None) or []
            )

        return self.engine.compute(
            persons=persons,
            families=families,
            events=events,
            sources=0,
            media=0,
        )
