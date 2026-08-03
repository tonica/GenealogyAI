"""Etapa d'importació del pipeline: `Importer`.

Persisteix el graf `ResolvedDoc` a la BDD mitjançant els repositories,
crea els esdeveniments (amb dates normalitzades), vincula els fills i crea
els `ParentChild`, calcula estadístiques i retorna un `ImportResult`.
L'`Importer` no fa `commit`; el decideix el caller (el pipeline)."""

from __future__ import annotations

from app.importer.models import GedcomDocument
from app.models import Event, ParentChild
from app.repositories import FamilyRepository, PersonRepository, PlaceRepository
from app.services.import_pipeline.response import ImportResult
from app.services.import_pipeline.resolver import ResolvedDoc
from app.services.stats import compute_stats
from app.utils.dates import normalize_date


class Importer:
    """Persisteix a la BDD el graf resolt pel `Resolver`."""

    def __init__(self, session) -> None:
        self.session = session
        self.person_repo = PersonRepository(session)
        self.family_repo = FamilyRepository(session)
        self.place_repo = PlaceRepository(session)

    def persist(
        self, doc: GedcomDocument, resolved: ResolvedDoc, issues
    ) -> ImportResult:
        # Registra persons, families, sources i media ja seus a la sessió.
        for p in resolved.persons.values():
            self.person_repo.add(p)
        for f in resolved.families.values():
            self.family_repo.add(f)
        for s in resolved.sources.values():
            self.session.add(s)
        for m in resolved.media.values():
            self.session.add(m)
        self.session.flush()

        # Assigna person_id / family_id i llocs als esdeveniments, i els
        # persisteix amb dates normalitzades.
        for xref, ev, place in resolved.person_events:
            ev.person_id = resolved.persons[xref].id
            self._add_event(ev, place)
        for xref, ev, place in resolved.family_events:
            ev.family_id = resolved.families[xref].id
            self._add_event(ev, place)

        # Vincula els fills amb l'ordre dins de la família.
        for fam_xref, child_xref, order in resolved.parent_child:
            fam = resolved.families[fam_xref]
            child = resolved.persons[child_xref]
            self.session.add(
                ParentChild(
                    family_id=fam.id,
                    child_id=child.id,
                    parent_id=fam.father_id,
                    role="father" if fam.father_id else None,
                    sibling_order=order,
                )
            )

        result = ImportResult(
            persons=len(resolved.persons),
            families=len(resolved.families),
            sources=len(resolved.sources),
            media=len(resolved.media),
            places=len(resolved.places),
            events=len(resolved.person_events) + len(resolved.family_events),
            children=len(resolved.parent_child),
            issues=issues,
            stats=compute_stats(doc),
        )
        self.session.flush()
        return result

    def _add_event(self, ev: Event, place) -> None:
        """Persisteix un esdeveniment amb la data normalitzada i el lloc."""
        nd = normalize_date(ev.date_text)
        ev.date_iso = nd.iso
        ev.date_year = nd.year
        self.session.add(ev)
        if place is not None:
            ev.place = place
