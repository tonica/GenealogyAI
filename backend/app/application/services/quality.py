"""Casos d'ús de qualitat de dades i intel·ligència genealògica.

Orquestren el `DomainLoader` (càrrega) i els motors de domínio
(anàlisi). La capa API només rep resultats ja calculats; no fa anàlisi.
"""

from __future__ import annotations

from app.application.domain_loader import DomainLoader, DomainDataset
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.services import (
    DataQualityReport,
    DataQualityReportGenerator,
    DomainStats,
    DuplicateCandidate,
    DuplicateDetector,
    ResearchTaskGenerator,
    ResearchTaskSuggestion,
    StatisticsEngine,
)


class QualityReportUseCase:
    """Genera l'informe complet de qualitat de dades."""

    def __init__(
        self,
        uow: AbstractUnitOfWork,
        duplicate_threshold: float = 0.55,
    ) -> None:
        self.uow = uow
        self._generator = DataQualityReportGenerator(
            duplicate_threshold=duplicate_threshold
        )

    def execute(self) -> DataQualityReport:
        ds: DomainDataset = DomainLoader(self.uow).load()
        return self._generator.generate(ds.persons, ds.places_raw)


class PersonQualityUseCase:
    """Qualitat individual d'una persona (score + factors)."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def execute(self, person_id: int) -> dict:
        from app.domain.services.quality_engine import QualityEngine

        ds: DomainDataset = DomainLoader(self.uow).load()
        person = next((p for p in ds.persons if p.id == person_id), None)
        if person is None:
            raise ValueError(f"Persona {person_id} no trobada")
        engine = QualityEngine()
        quality = engine.evaluate_person(
            person,
            has_parents=bool(person.family_as_child_ids),
            has_children=bool(getattr(person, "_children_ids", None)),
            has_sources=bool(
                next(
                    (ev for ev in ds.events if ev.person_id == person_id),
                    None,
                )
            ),
            event_count=sum(1 for ev in ds.events if ev.person_id == person_id),
            place_count=1 if person.birth_date else 0,
        )
        return quality.to_dict()


class DuplicatesUseCase:
    """Detecta possibles duplicats entre persones."""

    def __init__(self, uow: AbstractUnitOfWork, threshold: float = 0.55) -> None:
        self.uow = uow
        self._detector = DuplicateDetector(threshold=threshold)

    def execute(self) -> list[DuplicateCandidate]:
        ds: DomainDataset = DomainLoader(self.uow).load()
        return self._detector.detect_candidates(ds.persons)


class StatisticsUseCase:
    """Estadístiques agregades del conjunt de dades."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def execute(self) -> DomainStats:
        ds: DomainDataset = DomainLoader(self.uow).load()
        return StatisticsEngine().compute(ds.persons, ds.families, ds.events)


class ResearchTasksUseCase:
    """Genera suggeriments de tasques de recerca."""

    def __init__(
        self, uow: AbstractUnitOfWork, duplicate_threshold: float = 0.55
    ) -> None:
        self.uow = uow
        self._generator = ResearchTaskGenerator()
        self._detector = DuplicateDetector(threshold=duplicate_threshold)

    def execute(
        self, duplicates: list[DuplicateCandidate] | None = None
    ) -> list[ResearchTaskSuggestion]:
        ds: DomainDataset = DomainLoader(self.uow).load()
        pairs = duplicates or self._detector.detect_candidates(ds.persons)
        return self._generator.generate(
            ds.persons,
            [(c.person_a, c.person_b, c.score) for c in pairs],
        )


__all__ = [
    "QualityReportUseCase",
    "PersonQualityUseCase",
    "DuplicatesUseCase",
    "StatisticsUseCase",
    "ResearchTasksUseCase",
]
