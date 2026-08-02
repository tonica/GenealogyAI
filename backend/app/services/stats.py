"""Deteccio d'errors basics i calcul d'estadistiques.

Treballa amb els objectes neutrals de `app.importer.models` (abans o
despues de persistir); no depèn de la base de dades, fet que el fa
fàcilment testable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.importer.models import GedcomDocument
from app.utils.dates import normalize_date
from app.utils.text import normalize_place


@dataclass
class ImportIssue:
    """Un problema detectat durant la importacio."""

    level: str  # "error" | "warning"
    code: str
    xref: str
    message: str


@dataclass
class ImportStats:
    """Estadistiques calculades de l'import."""

    persons: int = 0
    families: int = 0
    sources: int = 0
    media: int = 0
    places: int = 0
    notes: int = 0
    events: int = 0
    events_by_type: dict[str, int] = field(default_factory=dict)
    sex_by: dict[str, int] = field(default_factory=dict)
    persons_with_birth: int = 0
    persons_with_death: int = 0
    persons_without_name: int = 0
    surname_frequency: dict[str, int] = field(default_factory=dict)
    birth_year_range: tuple[int | None, int | None] = (None, None)
    unresolved_refs: int = 0

    def to_dict(self) -> dict:
        return {
            "persons": self.persons,
            "families": self.families,
            "sources": self.sources,
            "media": self.media,
            "places": self.places,
            "notes": self.notes,
            "events": self.events,
            "events_by_type": dict(self.events_by_type),
            "sex_by": dict(self.sex_by),
            "persons_with_birth": self.persons_with_birth,
            "persons_with_death": self.persons_with_death,
            "persons_without_name": self.persons_without_name,
            "surname_frequency": dict(self.surname_frequency),
            "birth_year_range": list(self.birth_year_range),
            "unresolved_refs": self.unresolved_refs,
        }


# ---------------------------------------------------------------- errors


def detect_errors(doc: GedcomDocument) -> list[ImportIssue]:
    issues: list[ImportIssue] = []
    _check_duplicates(doc, issues)
    _check_references(doc, issues)
    _check_dates(doc, issues)
    _check_names(doc, issues)
    return issues


def _check_duplicates(doc: GedcomDocument, issues: list[ImportIssue]) -> None:
    seen: set[str] = set()
    for rec in doc.persons + doc.families:
        if rec.xref in seen:
            issues.append(
                ImportIssue(
                    "error",
                    "duplicate_xref",
                    rec.xref,
                    f"xref {rec.xref!r} repetit al document",
                )
            )
        seen.add(rec.xref)


def _check_references(doc: GedcomDocument, issues: list[ImportIssue]) -> None:
    person_ids = {p.xref for p in doc.persons}
    fam_ids = {f.xref for f in doc.families}
    source_ids = set(doc.sources)
    media_ids = set(doc.media)
    note_ids = set(doc.notes)

    for f in doc.families:
        for role, ref in (("HUSB", f.husband), ("WIFE", f.wife)):
            if ref and ref not in person_ids:
                issues.append(
                    ImportIssue(
                        "error",
                        "missing_family_member",
                        f.xref,
                        f"La familia {f.xref!r} apunta a la persona "
                        f"inexistent {ref!r} com a {role}",
                    )
                )
        for child in f.children:
            if child not in person_ids:
                issues.append(
                    ImportIssue(
                        "error",
                        "missing_child",
                        f.xref,
                        f"El fill {child!r} de {f.xref!r} no està definit",
                    )
                )

    for p in doc.persons:
        for ref in p.families_as_child + p.families_as_spouse:
            if ref not in fam_ids:
                issues.append(
                    ImportIssue(
                        "error",
                        "missing_family",
                        p.xref,
                        f"La persona {p.xref!r} referencia la família "
                        f"inexistent {ref!r}",
                    )
                )
        for ref in p.sources:
            if ref not in source_ids:
                issues.append(
                    ImportIssue(
                        "warning",
                        "missing_source",
                        p.xref,
                        f"La font {ref!r} no està definida",
                    )
                )
        for ref in p.media:
            if ref not in media_ids:
                issues.append(
                    ImportIssue(
                        "warning",
                        "missing_media",
                        p.xref,
                        f"L'OBJE {ref!r} no està definit",
                    )
                )
        for ref in p.note_refs:
            if ref not in note_ids:
                issues.append(
                    ImportIssue(
                        "warning",
                        "missing_note",
                        p.xref,
                        f"La nota {ref!r} no està definida",
                    )
                )


def _check_dates(doc: GedcomDocument, issues: list[ImportIssue]) -> None:
    for p in doc.persons:
        for ev in p.events:
            if ev.date is None:
                continue
            nd = normalize_date(ev.date)
            if not nd.valid and nd.original:
                issues.append(
                    ImportIssue(
                        "warning",
                        "bad_date",
                        p.xref,
                        f"Data no reconeguda: {ev.date!r}",
                    )
                )


def _check_names(doc: GedcomDocument, issues: list[ImportIssue]) -> None:
    for p in doc.persons:
        if not p.names or all(not (n.given or n.surname) for n in p.names):
            issues.append(
                ImportIssue("warning", "no_name", p.xref, "Persona sense nom")
            )


# ---------------------------------------------------------------- stats


def compute_stats(doc: GedcomDocument) -> ImportStats:
    s = ImportStats()
    s.persons = len(doc.persons)
    s.families = len(doc.families)
    s.sources = len(doc.sources)
    s.media = len(doc.media)
    s.notes = len(doc.notes)

    places: set[str] = set()
    years: list[int] = []
    known = set(doc.sources) | set(doc.media) | set(doc.notes)
    unresolved = 0

    for p in doc.persons:
        sex = (p.sex or "U").upper()
        s.sex_by[sex] = s.sex_by.get(sex, 0) + 1

        if not p.names or not any(n.given or n.surname for n in p.names):
            s.persons_without_name += 1
        for n in p.names:
            if n.surname:
                s.surname_frequency[n.surname] = (
                    s.surname_frequency.get(n.surname, 0) + 1
                )

        for ref in p.sources + p.media + p.note_refs:
            if ref not in known:
                unresolved += 1

        for ev in p.events:
            s.events += 1
            key = ev.type.lower()
            s.events_by_type[key] = s.events_by_type.get(key, 0) + 1
            if ev.place:
                places.add(normalize_place(ev.place) or "")
            if key == "birth":
                s.persons_with_birth += 1
                nd = normalize_date(ev.date)
                if nd.year is not None:
                    years.append(nd.year)
            elif key == "death":
                s.persons_with_death += 1

    for f in doc.families:
        for ev in f.events:
            s.events += 1
            key = ev.type.lower()
            s.events_by_type[key] = s.events_by_type.get(key, 0) + 1
            if ev.place:
                places.add(normalize_place(ev.place) or "")

    s.places = len([x for x in places if x])
    if years:
        s.birth_year_range = (min(years), max(years))
    s.unresolved_refs = unresolved
    return s
