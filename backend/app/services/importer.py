"""Servei d'importacio: rep els objectes del parser i els desa a SQLite.

Aplica —durant la persistencia— les normalitzacions demanades (dates,
llocs, cognoms i noms) i genera estadistiques i deteccio d'errors.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.importer.models import GedcomDocument
from app.models import Event, Family, Media, ParentChild, Person, Place, Source
from app.services.stats import ImportIssue, ImportStats, compute_stats, detect_errors
from app.utils.dates import normalize_date
from app.utils.text import normalize_place, normalize_surname


@dataclass
class ImportResult:
    """Resum de la importacio."""

    persons: int = 0
    families: int = 0
    sources: int = 0
    media: int = 0
    places: int = 0
    events: int = 0
    children: int = 0
    issues: list[ImportIssue] = field(default_factory=list)
    stats: ImportStats = field(default_factory=ImportStats)

    def to_dict(self) -> dict:
        return {
            "persons": self.persons,
            "families": self.families,
            "sources": self.sources,
            "media": self.media,
            "places": self.places,
            "events": self.events,
            "children": self.children,
            "issues": [iss.__dict__ for iss in self.issues],
            "stats": self.stats.to_dict(),
        }


class _PlaceIndex:
    """Molotx per a get-or-create de llocs usant la clau canònica."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self._by_key: dict[str, Place] = {}
        self.created = 0

    def get_or_create(self, display: str) -> Place | None:
        key = normalize_place(display)
        if not key:
            return None
        existing = self._by_key.get(key)
        if existing is not None:
            return existing
        existing = self.session.query(Place).filter(Place.name == display).one_or_none()
        if existing is None:
            existing = Place(name=display)
            self.session.add(existing)
            self.created += 1
        self._by_key[key] = existing
        return existing


def _resolve_notes(doc: GedcomDocument, refs: list[str]) -> list[str]:
    return [doc.notes[ref].text for ref in refs if ref in doc.notes]


def import_gedcom(session: Session, doc: GedcomDocument) -> ImportResult:
    """Deseea un `GedcomDocument` a la base de dades.

    No fa commit; el caller decideix entre commit i rollback.
    """
    result = ImportResult()
    result.issues = detect_errors(doc)
    result.stats = compute_stats(doc)

    places = _PlaceIndex(session)

    # --- Fonts (SOUR) ---
    # `sources.title` es únic a la DB; a la pràctica MyHeritage pot exportar
    # dos SOUR amb el mateix títol. Dedupiquem pel títol i apuntem tots els
    # xrefs col·lisionants a la mateixa fila.
    sources_objs: dict[str, Source] = {}
    seen_titles: dict[str, Source] = {}
    for xref, src in doc.sources.items():
        title = src.title or xref
        existing = seen_titles.get(title)
        if existing is None:
            obj = Source(xref=xref, title=title, author=src.author)
            session.add(obj)
            existing = obj
            seen_titles[title] = existing
        sources_objs[xref] = existing

    # --- Persones (INDI) ---
    person_objs: dict[str, Person] = {}
    for p in doc.persons:
        name = p.primary_name
        person = Person(
            xref=p.xref,
            given_name=_normalize_given(name.given) if name else None,
            surname=normalize_surname(name.surname) if name else None,
            sex=p.sex,
            notes=("\n".join(p.note_texts + _resolve_notes(doc, p.note_refs)) or None),
        )
        session.add(person)
        person_objs[p.xref] = person
    session.flush()

    # --- Media (OBJE) ---
    media_objs: dict[str, Media] = {}
    for xref, m in doc.media.items():
        med = Media(xref=xref, file_path=m.file or "", caption=m.title)
        session.add(med)
        media_objs[xref] = med
    session.flush()

    # --- Esdeveniments de persones, dates i llocs ---
    for p in doc.persons:
        person = person_objs[p.xref]
        for ev in p.events:
            place = places.get_or_create(ev.place) if ev.place else None
            nd = normalize_date(ev.date)
            session.add(
                Event(
                    event_type=ev.type.lower(),
                    date_text=ev.date,
                    date_iso=nd.iso,
                    date_year=nd.year,
                    person_id=person.id,
                    place=place,
                )
            )
        _set_life_dates(person, p.birth, p.death)
        for ref in p.sources:
            src = sources_objs.get(ref)
            if src and src not in person.sources:
                person.sources.append(src)
        for ref in p.media:
            med = media_objs.get(ref)
            if med:
                person.media.append(med)

    # --- Families (FAM) ---
    for f in doc.families:
        fam = Family(
            xref=f.xref,
            father_id=person_objs[f.husband].id if f.husband in person_objs else None,
            mother_id=person_objs[f.wife].id if f.wife in person_objs else None,
        )
        session.add(fam)
        session.flush()

        for ev in f.events:
            place = places.get_or_create(ev.place) if ev.place else None
            nd = normalize_date(ev.date)
            session.add(
                Event(
                    family_id=fam.id,
                    event_type=ev.type.lower(),
                    date_text=ev.date,
                    date_iso=nd.iso,
                    date_year=nd.year,
                    place=place,
                )
            )

        if f.children:
            father_id = person_objs[f.husband].id if f.husband in person_objs else None
            result.children += len(f.children)
            for order, child_ref in enumerate(f.children, start=1):
                child = person_objs.get(child_ref)
                if child is None:
                    continue
                session.add(
                    ParentChild(
                        family_id=fam.id,
                        child_id=child.id,
                        parent_id=father_id,
                        role="father" if father_id else None,
                        sibling_order=order,
                    )
                )

    result.persons = len(doc.persons)
    result.families = len(doc.families)
    result.sources = len(doc.sources)
    result.media = len(media_objs)
    result.places = places.created
    result.events = _count_events(session)
    return result


def _normalize_given(given: str) -> str:
    return given.strip().title() if given.strip() else given


def _set_life_dates(person: Person, birth, death) -> None:
    if birth and birth.date:
        person.birth_date = birth.date
    if death and death.date:
        person.death_date = death.date


def _count_events(session: Session) -> int:
    from sqlalchemy import func

    return session.query(func.count(Event.id)).scalar() or 0
