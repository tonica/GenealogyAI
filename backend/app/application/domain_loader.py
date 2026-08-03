"""Càrrega del dataset de domínio des de la infraestructura.

L'Application layer fa d'intermediari entre els repositoris (ORM) i els
motors de domínio: converteix via mappers i enriqueix les entitats amb les
relacions (pares, fills, llocs) que el domínio necessita.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.application.unit_of_work import AbstractUnitOfWork
from app.domain.entities import Event as DomainEvent
from app.domain.entities import Family as DomainFamily
from app.domain.entities import Person as DomainPerson
from app.domain.entities import Place as DomainPlace
from app.mappers import EventMapper, FamilyMapper, PersonMapper, PlaceMapper


@dataclass
class DomainDataset:
    """Conjunt complet de dades de domínio carregat de la persistència."""

    persons: list[DomainPerson] = field(default_factory=list)
    families: list[DomainFamily] = field(default_factory=list)
    events: list[DomainEvent] = field(default_factory=list)
    places: list[DomainPlace] = field(default_factory=list)
    places_raw: list[str] = field(default_factory=list)


class DomainLoader:
    """Carrega i enriqueix les entitats de domínio des dels repositoris."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def load(self) -> DomainDataset:
        # Carrega totes les persones i famílies (ORM).
        persons_orm = self.uow.persons.all()
        families_orm = self.uow.families.all()

        # Converteix a domínio.
        persons = [PersonMapper.to_domain(p) for p in persons_orm]
        families = [FamilyMapper.to_domain(f) for f in families_orm]

        # Índexs auxiliars.
        person_by_id = {p.id: p for p in persons}
        family_by_id = {f.id: f for f in families}

        # Enriqueix relacions de pares (famílies com a fill).
        for orm_fam in families_orm:
            fam_id = orm_fam.id
            for pc in orm_fam.parent_children:
                child = person_by_id.get(pc.child_id)
                if child is not None:
                    child.family_as_child_ids.append(fam_id)
                    fam = family_by_id.get(fam_id)
                    if fam is not None:
                        fam.add_child(pc.child_id)

        # Enriqueix famílies com a cònjuge (pare o mare de la família) i
        # llista inversa de fills (`_children_ids`) per a les regles de domínio.
        for orm_fam in families_orm:
            fam_id = orm_fam.id
            child_ids = [pc.child_id for pc in orm_fam.parent_children or []]
            for attr in ("father_id", "mother_id"):
                pid = getattr(orm_fam, attr)
                person = person_by_id.get(pid)
                if person is not None:
                    person.family_as_spouse_ids.append(fam_id)
                    person._children_ids = sorted(
                        set(getattr(person, "_children_ids", []) or []) | set(child_ids)
                    )

        # Converteix esdeveniments i llocs.
        events: list[DomainEvent] = []
        places_set: dict[int, DomainPlace] = {}
        # Persona -> (tipus, data text) per als esdeveniments vitals.
        life_events: dict[int, list[tuple[str, str | None]]] = {}
        for orm_p in persons_orm:
            for orm_ev in getattr(orm_p, "events", None) or []:
                ev = EventMapper.to_domain(orm_ev)
                if orm_ev.place is not None:
                    dom_place = places_set.setdefault(
                        orm_ev.place.id, PlaceMapper.to_domain(orm_ev.place)
                    )
                    ev.place = dom_place
                    ev.place_id = dom_place.id
                events.append(ev)
                life_events.setdefault(orm_p.id, []).append(
                    (ev.event_type or "", ev.date_text)
                )

        # El model ORM no omple person.birth_date/death_date (les dates viuen
        # als esdeveniments): les derivem aquí per al domini.
        for p in persons:
            if not p.birth_date and p.id is not None:
                for etype, dtext in life_events.get(p.id, []):
                    if etype in {"birth", "christening", "baptism"} and dtext:
                        p.birth_date = dtext
                        break
            if not p.death_date and p.id is not None:
                for etype, dtext in life_events.get(p.id, []):
                    if etype in {"death", "burial"} and dtext:
                        p.death_date = dtext
                        break

        places = list(places_set.values())
        places_raw = sorted({pl.name for pl in places if pl.name})

        return DomainDataset(
            persons=persons,
            families=families,
            events=events,
            places=places,
            places_raw=places_raw,
        )
