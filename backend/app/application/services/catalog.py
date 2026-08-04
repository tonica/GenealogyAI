"""Serveis d'aplicació per al contracte públic v1 (Sprint 2).

`CatalogService` assembla els DTOs del contracte (`app.schemas.dto`)
a partir del dataset de domínio (DomainLoader) i els motors existents,
sense tocar el Domain ni els Repositories.

Reusa els casos d'ús de qualitat/estadístiques per mantenir una única
font de veritat per als càlculs.
"""

from __future__ import annotations

from sqlalchemy import func, select

from app.application.domain_loader import DomainDataset, DomainLoader
from app.application.services.quality import (
    DuplicatesUseCase,
    ResearchTasksUseCase,
    StatisticsUseCase,
)
from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities import Event, Family, Person
from app.domain.services import (
    DuplicateDetector,
    QualityEngine,
    ResearchTaskGenerator,
)

_BIRTH_TYPES = {"birth", "christening", "baptism"}
_DEATH_TYPES = {"death", "burial"}


class CatalogService:
    """Assembla DTOs de persones, famílies i dashboard des del dataset."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow
        self._ds: DomainDataset | None = None

    # ------------------------------------------------------------------ #
    # Accés al dataset (carregat una sola vegada per instància)
    # ------------------------------------------------------------------ #
    @property
    def ds(self) -> DomainDataset:
        if self._ds is None:
            self._ds = DomainLoader(self.uow).load()
        return self._ds

    def _person_by_id(self, person_id: int) -> Person | None:
        return next((p for p in self.ds.persons if p.id == person_id), None)

    def _family_by_id(self, family_id: int) -> Family | None:
        return next((f for f in self.ds.families if f.id == family_id), None)

    def _events_by_person(self) -> dict[int, list[Event]]:
        result: dict[int, list[Event]] = {}
        for ev in self.ds.events:
            if ev.person_id is not None:
                result.setdefault(ev.person_id, []).append(ev)
        return result

    @staticmethod
    def _place_name(ev: Event | None) -> str | None:
        if ev is None or ev.place is None:
            return None
        return ev.place.name or ev.place.display_name

    @staticmethod
    def _life_event(events: list[Event], types: set[str]) -> Event | None:
        for ev in events:
            if (ev.event_type or "").lower() in types:
                return ev
        return None

    # ------------------------------------------------------------------ #
    # Persones
    # ------------------------------------------------------------------ #
    def _summary(self, person: Person, events_by_person: dict) -> dict:
        events = events_by_person.get(person.id or 0, [])
        birth = self._life_event(events, _BIRTH_TYPES)
        death = self._life_event(events, _DEATH_TYPES)
        return {
            "id": person.id,
            "xref": person.xref,
            "given_name": person.given_name,
            "surname": person.surname,
            "prefix": person.prefix,
            "suffix": person.suffix,
            "sex": person.sex,
            "display_name": person.display_name,
            "birth_date": person.birth_date,
            "death_date": person.death_date,
            "birth_year": birth.date_year if birth else None,
            "death_year": death.date_year if death else None,
            "birth_place": self._place_name(birth),
            "death_place": self._place_name(death),
            "quality": None,
        }

    def search(
        self,
        q: str | None = None,
        given_name: str | None = None,
        surname: str | None = None,
        sex: str | None = None,
        place: str | None = None,
        birth_year: int | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[dict]:
        events_by_person = self._events_by_person()
        matched: list[Person] = []
        for p in self.ds.persons:
            if q and q.lower() not in f"{p.given_name or ''} {p.surname or ''}".lower():
                continue
            if given_name and given_name.lower() not in (p.given_name or "").lower():
                continue
            if surname and surname.lower() not in (p.surname or "").lower():
                continue
            if sex and p.sex != sex:
                continue
            events = events_by_person.get(p.id or 0, [])
            birth = self._life_event(events, _BIRTH_TYPES)
            if birth_year is not None:
                if birth is None or birth.date_year != birth_year:
                    continue
            if place:
                names = [self._place_name(ev) or "" for ev in events]
                if not any(place.lower() in name.lower() for name in names):
                    continue
            matched.append(p)

        matched.sort(key=lambda p: (p.surname or "", p.given_name or ""))
        page = matched[offset : offset + limit]
        result = [self._summary(p, events_by_person) for p in page]
        for item, p in zip(result, page):
            item["quality"] = self._quality_score(p, events_by_person)
        return result

    def person(self, person_id: int) -> dict:
        person = self._person_by_id(person_id)
        if person is None:
            raise ValueError(f"Persona {person_id} no trobada")
        events_by_person = self._events_by_person()
        events = events_by_person.get(person.id or 0, [])
        base = self._summary(person, events_by_person)

        # Pares: famílies on la persona és fill/a.
        parents: list[dict] = []
        for fid in person.family_as_child_ids:
            fam = self._family_by_id(fid)
            if fam is None:
                continue
            for pid in (fam.father_id, fam.mother_id):
                parent = self._person_by_id(pid) if pid is not None else None
                if parent is not None:
                    parents.append(self._summary(parent, events_by_person))

        # Cònjuges: famílies pròpies (la persona n'és pare o mare).
        spouses: list[dict] = []
        for fid in person.family_as_spouse_ids:
            fam = self._family_by_id(fid)
            if fam is None:
                continue
            other_id = fam.mother_id if fam.father_id == person.id else fam.father_id
            other = self._person_by_id(other_id) if other_id is not None else None
            spouses.append(
                {
                    "family_id": fid,
                    "spouse": (
                        self._summary(other, events_by_person) if other else None
                    ),
                    "marriage_date": fam.marriage_date,
                    "marriage_place": fam.marriage_place,
                }
            )

        # Fills (inversa `_children_ids` enriquida pel DomainLoader).
        children: list[dict] = []
        for cid in getattr(person, "_children_ids", None) or []:
            child = self._person_by_id(cid)
            if child is not None:
                children.append(self._summary(child, events_by_person))
        children.sort(
            key=lambda c: (
                c["birth_year"] is None,
                c["birth_year"] if c["birth_year"] is not None else 0,
                c["display_name"] or "",
            )
        )

        # Duplicats i tasques de recerca (filtrats a aquesta persona).
        detector = DuplicateDetector()
        candidates = detector.detect_candidates(self.ds.persons)
        dupes = [
            c
            for c in candidates
            if c.person_a.id == person.id or c.person_b.id == person.id
        ]
        pairs = [(c.person_a, c.person_b, c.score) for c in candidates]
        tasks = [
            t
            for t in ResearchTaskGenerator().generate(self.ds.persons, pairs)
            if t.person_id == person.id
        ]

        birth_ev = self._life_event(events, _BIRTH_TYPES)
        death_ev = self._life_event(events, _DEATH_TYPES)
        return {
            **base,
            "notes": person.notes,
            "birth": self._timeline([birth_ev])[0] if birth_ev else None,
            "death": self._timeline([death_ev])[0] if death_ev else None,
            "parents": parents,
            "spouses": spouses,
            "children": children,
            "events": self._timeline(events),
            "timeline": self._timeline(events),
            "quality_detail": self._quality_detail(person, events_by_person),
            "duplicates": [c.to_dict() for c in dupes],
            "tasks": [t.to_dict() for t in tasks],
        }

    def _quality_score(
        self, person: Person, events_by_person: dict | None = None
    ) -> float | None:
        detail = self._quality_detail(person, events_by_person)
        return detail["score"] if detail else None

    def _quality_detail(
        self, person: Person, events_by_person: dict | None = None
    ) -> dict:
        events = (events_by_person or self._events_by_person()).get(person.id or 0, [])
        engine = QualityEngine()
        quality = engine.evaluate_person(
            person,
            has_parents=bool(person.family_as_child_ids),
            has_children=bool(getattr(person, "_children_ids", None)),
            has_sources=bool(events),
            event_count=len(events),
            place_count=1 if person.birth_date else 0,
        )
        return quality.to_dict()

    # ------------------------------------------------------------------ #
    # Línia del temps
    # ------------------------------------------------------------------ #
    def _timeline(self, events: list[Event]) -> list[dict]:
        out: list[dict] = []
        for ev in events:
            out.append(
                {
                    "id": ev.id,
                    "event_type": ev.event_type,
                    "date_text": ev.date_text,
                    "date_iso": ev.date_iso,
                    "date_year": ev.date_year,
                    "place": self._place_name(ev),
                    "place_id": ev.place_id,
                    "description": ev.description,
                    "sort_year": ev.date_year,
                }
            )
        out.sort(key=lambda e: (e["sort_year"] is None, e["sort_year"] or 0))
        return out

    # ------------------------------------------------------------------ #
    # Famílies
    # ------------------------------------------------------------------ #
    def families(self, limit: int = 50, offset: int = 0) -> list[dict]:
        fams = self.ds.families[offset : offset + limit]
        return [self.family(f.id) for f in fams if f.id is not None]

    def family(self, family_id: int) -> dict:
        fam = self._family_by_id(family_id)
        if fam is None:
            raise ValueError(f"Família {family_id} no trobada")
        events_by_person = self._events_by_person()
        father = self._person_by_id(fam.father_id) if fam.father_id else None
        mother = self._person_by_id(fam.mother_id) if fam.mother_id else None
        children = [self._person_by_id(cid) for cid in fam.child_ids if cid is not None]
        children = [c for c in children if c is not None]
        children.sort(
            key=lambda c: (
                c.birth_date is None,
                c.birth_date or "",
                c.display_name or "",
            )
        )
        fam_events = [ev for ev in self.ds.events if ev.family_id == family_id]
        return {
            "id": fam.id,
            "xref": fam.xref,
            "father": (self._summary(father, events_by_person) if father else None),
            "mother": (self._summary(mother, events_by_person) if mother else None),
            "children": [self._summary(c, events_by_person) for c in children],
            "marriage_date": fam.marriage_date,
            "marriage_place": fam.marriage_place,
            "events": self._timeline(fam_events),
        }

    # ------------------------------------------------------------------ #
    # Dashboard
    # ------------------------------------------------------------------ #
    def dashboard(self) -> dict:
        stats = StatisticsUseCase(self.uow).execute().to_dict()
        duplicates = DuplicatesUseCase(self.uow).execute()
        tasks = ResearchTasksUseCase(self.uow).execute(duplicates)

        scores: list[float] = []
        events_by_person = self._events_by_person()
        for p in self.ds.persons:
            score = self._quality_score(p, events_by_person)
            if score is not None:
                scores.append(score)
        avg_quality = round(sum(scores) / len(scores), 2) if scores else None

        sources = self._count("Source")
        media = self._count("Media")
        last_import = self._last_import()
        return {
            "persons": stats["persons"],
            "families": stats["families"],
            "events": stats["events"],
            "places": len(self.ds.places),
            "sources": sources,
            "media": media,
            "males": stats["males"],
            "females": stats["females"],
            "average_age": stats["average_age"],
            "average_quality": avg_quality,
            "duplicates": len(duplicates),
            "pending_tasks": len(tasks),
            "last_import": last_import,
        }

    # ------------------------------------------------------------------ #
    # Consultes read-only a la base (sense tocar repositoris)
    # ------------------------------------------------------------------ #
    def _count(self, model_name: str) -> int:
        from app.models import Event as _Event
        from app.models import Family as _Family
        from app.models import Media, Person, Place, Source

        table = {
            "Source": Source,
            "Media": Media,
            "Person": Person,
            "Family": _Family,
            "Event": _Event,
            "Place": Place,
        }[model_name]
        session = self.uow.persons.session
        return int(session.scalar(select(func.count(table.id))) or 0)

    def _last_import(self) -> str | None:
        from app.models import Person

        session = self.uow.persons.session
        value = session.scalar(select(func.max(Person.created_at)))
        if value is None:
            return None
        return value.isoformat()
