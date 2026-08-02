"""Objectes Python tipats que representa la informacio parsejada d'un GEDCOM.

Aquests dataclasses son la capa neutra entre el fitxer GEDCOM (format text)
i la persistencia (models SQLAlchemy). El parser converteix el arbre brut en
aquests objectes.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Name:
    """Un nom d'individu, pot tenir variant/es."""

    value: str = ""
    given: str = ""
    surname: str = ""
    prefix: str = ""
    suffix: str = ""


@dataclass
class Event:
    """Esdeveniment vital (naixement, mort, matrimoni, ...)."""

    type: str = ""
    date: str | None = None
    place: str | None = None
    notes: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    media: list[str] = field(default_factory=list)


@dataclass
class Person:
    """Individu (INDI)."""

    xref: str = ""
    names: list[Name] = field(default_factory=list)
    sex: str | None = None
    events: list[Event] = field(default_factory=list)
    note_texts: list[str] = field(default_factory=list)
    note_refs: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    media: list[str] = field(default_factory=list)
    families_as_child: list[str] = field(default_factory=list)
    families_as_spouse: list[str] = field(default_factory=list)

    @property
    def primary_name(self) -> Name | None:
        return self.names[0] if self.names else None

    def event_of(self, type: str) -> Event | None:
        for ev in self.events:
            if ev.type == type:
                return ev
        return None

    @property
    def birth(self) -> Event | None:
        return self.event_of("birth")

    @property
    def death(self) -> Event | None:
        return self.event_of("death")


@dataclass
class Family:
    """Unitat familiar (FAM): els patrons i els fills."""

    xref: str = ""
    husband: str | None = None
    wife: str | None = None
    children: list[str] = field(default_factory=list)
    events: list[Event] = field(default_factory=list)
    note_texts: list[str] = field(default_factory=list)
    note_refs: list[str] = field(default_factory=list)
    sources: list[str] = field(default_factory=list)
    media: list[str] = field(default_factory=list)

    def event_of(self, type: str) -> Event | None:
        for ev in self.events:
            if ev.type == type:
                return ev
        return None


@dataclass
class SourceRecord:
    """Una font o citacio (SOUR)."""

    xref: str = ""
    title: str = ""
    author: str = ""
    publication: str = ""
    page: str = ""


@dataclass
class MediaRecord:
    """Un objecte multimoddia (OBJE)."""

    xref: str = ""
    file: str = ""
    title: str = ""


@dataclass
class NoteRecord:
    """Una nota sobira (NOTE)."""

    xref: str = ""
    text: str = ""


@dataclass
class GedcomDocument:
    """Resultat complet del parsing d'un fitxer GEDCOM."""

    header: dict = field(default_factory=dict)
    persons: list[Person] = field(default_factory=list)
    families: list[Family] = field(default_factory=list)
    sources: dict[str, SourceRecord] = field(default_factory=dict)
    media: dict[str, MediaRecord] = field(default_factory=dict)
    notes: dict[str, NoteRecord] = field(default_factory=dict)

    def person_by_xref(self, xref: str) -> Person | None:
        for p in self.persons:
            if p.xref == xref:
                return p
        return None
