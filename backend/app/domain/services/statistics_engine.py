"""Servei de domínio `StatisticsEngine`.

Calcula estadístiques agregades a partir de les entitats del domínio
(`Person`, `Family`, `Event`), sense cap accés a la base de dades.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Event, Family, Person


@dataclass
class DomainStats:
    """Estadístiques calculades sobre el domínio."""

    persons: int = 0
    families: int = 0
    sources: int = 0
    media: int = 0
    events: int = 0
    events_by_type: dict[str, int] = field(default_factory=dict)
    sex_by: dict[str, int] = field(default_factory=dict)
    surname_frequency: dict[str, int] = field(default_factory=dict)
    persons_without_name: int = 0
    birth_year_range: tuple[int | None, int | None] = (None, None)


class StatisticsEngine:
    """Enginy d'estadístiques de domínio (funció per lots)."""

    def compute(
        self,
        persons: list[Person],
        families: list[Family],
        events: list[Event],
        sources: int = 0,
        media: int = 0,
    ) -> DomainStats:
        stats = DomainStats()
        stats.persons = len(persons)
        stats.families = len(families)
        stats.sources = sources
        stats.media = media
        stats.events = len(events)

        year_ranges: list[int] = []
        for p in persons:
            sex = (p.sex or "U").upper()
            stats.sex_by[sex] = stats.sex_by.get(sex, 0) + 1
            if p.surname:
                stats.surname_frequency[p.surname] = (
                    stats.surname_frequency.get(p.surname, 0) + 1
                )
            if not (p.given_name or p.surname):
                stats.persons_without_name += 1

        for ev in events:
            key = (ev.event_type or "unknown").lower()
            stats.events_by_type[key] = stats.events_by_type.get(key, 0) + 1
            if key == "birth" and ev.date_year is not None:
                year_ranges.append(ev.date_year)

        if year_ranges:
            stats.birth_year_range = (min(year_ranges), max(year_ranges))
        return stats
