"""Servei de domínio `StatisticsEngine`.

Calcula estadístiques agregades a partir d'entitats de domínio només
(`Person`, `Family`, `Event`). Cap dependència de repository ni ORM.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Event, Family, Person
from app.domain.services.date_engine import DateEngine


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
    # Nous càlculs de l'Sprint 1.6.
    males: int = 0
    females: int = 0
    average_age: float | None = None
    max_age: int | None = None
    births_by_year: dict[int, int] = field(default_factory=dict)
    deaths_by_year: dict[int, int] = field(default_factory=dict)
    top_places: list[tuple[str, int]] = field(default_factory=list)
    top_surnames: list[tuple[str, int]] = field(default_factory=list)
    largest_branches: list[int] = field(default_factory=list)
    persons_without_data: int = 0

    def to_dict(self) -> dict:
        return {
            "persons": self.persons,
            "families": self.families,
            "sources": self.sources,
            "media": self.media,
            "events": self.events,
            "males": self.males,
            "females": self.females,
            "average_age": self.average_age,
            "max_age": self.max_age,
            "events_by_type": dict(self.events_by_type),
            "sex_by": dict(self.sex_by),
            "surname_frequency": dict(self.surname_frequency),
            "persons_without_name": self.persons_without_name,
            "persons_without_data": self.persons_without_data,
            "birth_year_range": list(self.birth_year_range),
            "births_by_year": dict(self.births_by_year),
            "deaths_by_year": dict(self.deaths_by_year),
            "top_places": [{"name": n, "count": c} for n, c in self.top_places],
            "top_surnames": [{"surname": n, "count": c} for n, c in self.top_surnames],
            "largest_branches": list(self.largest_branches),
        }


class StatisticsEngine:
    """Enginy d'estadístiques de domínio (funció per lots)."""

    def __init__(self) -> None:
        self._date_engine = DateEngine()

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

        ages: list[int] = []
        birth_years: list[int] = []
        death_years: list[int] = []

        for p in persons:
            sex = (p.sex or "U").upper()
            stats.sex_by[sex] = stats.sex_by.get(sex, 0) + 1
            if sex == "M":
                stats.males += 1
            elif sex == "F":
                stats.females += 1

            if p.surname:
                stats.surname_frequency[p.surname] = (
                    stats.surname_frequency.get(p.surname, 0) + 1
                )
            if not (p.given_name or p.surname):
                stats.persons_without_name += 1
            if not (p.birth_date or p.death_date or p.given_name or p.surname):
                stats.persons_without_data += 1

            age = self._age(p)
            if age is not None:
                ages.append(age)

            b_year = self._year_of(p.birth_date)
            if b_year is not None:
                birth_years.append(b_year)
                stats.births_by_year[b_year] = stats.births_by_year.get(b_year, 0) + 1
            d_year = self._year_of(p.death_date)
            if d_year is not None:
                death_years.append(d_year)
                stats.deaths_by_year[d_year] = stats.deaths_by_year.get(d_year, 0) + 1

        # Llocs i esdeveniments per tipus.
        places: dict[str, int] = {}
        for ev in events:
            key = (ev.event_type or "unknown").lower()
            stats.events_by_type[key] = stats.events_by_type.get(key, 0) + 1
            if key == "birth" and ev.date_year is not None:
                birth_years.append(ev.date_year)
            place_name = (
                ev.place.name
                if ev.place and ev.place.name
                else (
                    ev.place.display_name
                    if ev.place and ev.place.display_name
                    else None
                )
            )
            if place_name:
                places[place_name] = places.get(place_name, 0) + 1

        if birth_years:
            stats.birth_year_range = (min(birth_years), max(birth_years))

        if ages:
            stats.average_age = round(sum(ages) / len(ages), 1)
            stats.max_age = max(ages)

        stats.top_places = sorted(places.items(), key=lambda kv: -kv[1])[:10]
        stats.top_surnames = sorted(
            stats.surname_frequency.items(), key=lambda kv: -kv[1]
        )[:15]
        stats.largest_branches = self._largest_branches(persons, families)
        return stats

    # -------------------------------------------------------------- helpers
    def _year_of(self, date_text: str | None) -> int | None:
        if not date_text:
            return None
        dv = self._date_engine.parse(date_text)
        return dv.year

    def _age(self, p: Person) -> int | None:
        """Edat estimada: diferència d'anys naixement-defunció."""
        if not p.birth_date:
            return None
        b = self._date_engine.parse(p.birth_date)
        if b.year is None:
            return None
        if p.death_date:
            d = self._date_engine.parse(p.death_date)
            if d.year is not None and d.year >= b.year:
                return d.year - b.year
        return None

    @staticmethod
    def _largest_branches(persons: list[Person], families: list[Family]) -> list[int]:
        """Mida de les branques (famílies) més grans per nombre de fills."""
        sizes: dict[int, int] = {}
        for fam in families:
            n_children = len(fam.child_ids)
            if n_children:
                sizes[fam.id or -1] = n_children
        return sorted(sizes.values(), reverse=True)[:5]
