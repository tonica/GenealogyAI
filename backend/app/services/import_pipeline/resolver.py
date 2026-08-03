"""Etapa de resolução do pipeline: `Resolver`.

Constrói objetos ORM a part do documento normalizado e resolve as
referências entre entidades (fonts desduplicades, lloc canònic, enllaços
HUSB/WIFE/CHIL). No fa commit; només prepara objectes a la sessió.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.models import Event, Family, Media, Person, Place, Source
from app.repositories import FamilyRepository, PersonRepository, PlaceRepository
from app.services.import_pipeline.normalizer import NormalizedFields
from app.utils.text import normalize_place


@dataclass
class ResolvedDoc:
    """Graf d'objectes ORM preparat per a l'`Importer`."""

    persons: dict[str, Person]  # xref -> Person
    families: dict[str, Family]
    sources: dict[str, Source]
    media: dict[str, Media]
    places: list[Place]
    # (reference_xref, Event, place_opcional) per persistir a la sessió.
    person_events: list[tuple[str, Event, Place | None]]
    family_events: list[tuple[str, Event, Place | None]]
    # (family_xref, child_xref, order) per a ParentChild.
    parent_child: list[tuple[str, str, int]]


class _PlaceIndex:
    """Molotx per a get-or-create de llocs usant la clau canònica."""

    def __init__(self, session) -> None:
        self.session = session
        self.repo = PlaceRepository(session)
        self._by_key: dict[str, Place] = {}
        self.created: list[Place] = []

    def get_or_create(self, display: str | None) -> Place | None:
        key = normalize_place(display)
        if not key:
            return None
        place = self._by_key.get(key)
        if place is None:
            existing = self.repo.get_by_name(display or "")
            if existing is None:
                place = Place(
                    name=display,
                    display_name=display,
                    canonical_name=key,
                )
                self.session.add(place)
                self.created.append(place)
            else:
                place = existing
            self._by_key[key] = place
        return place


class Resolver:
    """Mapeja el document neutra normalizado en objetos ORM."""

    def __init__(
        self, session, person_repo: PersonRepository, family_repo: FamilyRepository
    ) -> None:
        self.session = session
        self.person_repo = person_repo
        self.family_repo = family_repo

    def _build_persons(
        self, doc, fields: dict[str, NormalizedFields]
    ) -> dict[str, Person]:
        persons: dict[str, Person] = {}
        for person in doc.persons:
            f = fields.get(person.xref)
            persons[person.xref] = Person(
                xref=person.xref,
                given_name=f.given_name if f else None,
                surname=f.surname if f else None,
                sex=person.sex,
                notes=("\n".join(person.note_texts) or None),
                search_name=f.search_name if f else None,
                slug=f.slug if f else None,
                soundex=f.soundex if f else None,
                metaphone=f.metaphone if f else None,
            )
        return persons

    def _build_sources(self, doc) -> dict[str, Source]:
        # `sources.title` es únic a la DB; dedup per títol.
        sources: dict[str, Source] = {}
        seen: dict[str, Source] = {}
        for xref, s in doc.sources.items():
            title = s.title or xref
            obj = seen.get(title)
            if obj is None:
                obj = Source(xref=xref, title=title, author=s.author or None)
                seen[title] = obj
            sources[xref] = obj
        return sources

    def _build_media(self, doc) -> dict[str, Media]:
        return {
            xref: Media(xref=xref, file_path=m.file or "", caption=m.title)
            for xref, m in doc.media.items()
        }

    def resolve(self, doc, fields: dict[str, NormalizedFields]) -> ResolvedDoc:
        persons = self._build_persons(doc, fields)
        sources = self._build_sources(doc)
        media = self._build_media(doc)
        places_idx = _PlaceIndex(self.session)

        # Enlembre persons, fonts, media links.
        for person in doc.persons:
            p = persons[person.xref]
            for ref in person.sources:
                src = sources.get(ref)
                if src is not None:
                    if src not in p.sources:
                        p.sources.append(src)
            for ref in person.media:
                m = media.get(ref)
                if m is not None and m not in p.media:
                    p.media.append(m)

        # Enlembre esdeveniments i llocs (trobem quins imports perseguir).
        # Guardem la referència de lloc a banda; l'`Importer` l'assigna
        # un cop l'`Event` ja és a la sessió (evita SAWarning d'objecte
        # desatacat).
        person_events: list[tuple[str, Event, Place | None]] = []
        for person in doc.persons:
            p = persons[person.xref]
            if p.id is None:
                self.session.add(p)
            for ev in person.events:
                place = places_idx.get_or_create(ev.place)
                person_events.append(
                    (
                        person.xref,
                        Event(
                            event_type=ev.type.lower(),
                            date_text=ev.date,
                            person_id=None,
                        ),
                        place,
                    )
                )

        # L'Importer assignarà als eve_date data normalitzada i fill.
        families: dict[str, Family] = {}
        family_events: list[tuple[str, Event, Place | None]] = []
        parent_child: list[tuple[str, str, int]] = []
        for family in doc.families:
            fam = Family(
                xref=family.xref,
                father_id=(
                    persons[family.husband].id if family.husband in persons else None
                ),
                mother_id=persons[family.wife].id if family.wife in persons else None,
            )
            if fam.id is None:
                self.session.add(fam)
            families[family.xref] = fam
            for ev in family.events:
                place = places_idx.get_or_create(ev.place)
                family_events.append(
                    (
                        family.xref,
                        Event(
                            event_type=ev.type.lower(),
                            date_text=ev.date,
                            family_id=None,
                        ),
                        place,
                    )
                )
            for order, child_xref in enumerate(family.children, start=1):
                if child_xref in persons:
                    parent_child.append((family.xref, child_xref, order))

        return ResolvedDoc(
            persons=persons,
            families=families,
            sources=sources,
            media=media,
            places=list(dict.fromkeys(places_idx.created)),
            person_events=person_events,
            family_events=family_events,
            parent_child=parent_child,
        )
