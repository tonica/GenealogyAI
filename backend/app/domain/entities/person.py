"""Entitat de domínio `Person` (independent de la persistència).

Aquesta classe represente una persona de la genealogia sense cap
dependència d'SQLAlchemy. Als mappers la convertiran en els seus
equivalents ORM i viceversa.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Person:
    """Persona (individu) del arbre genealogic.

    Atributs bàsicos ideals iguals que el model ORM, però sense ORM.
    Les relacions es representen amb llistes d'identificadors (xref/uuid)
    per mantenir el domínio independent de les claus i les relacions.
    """

    # Identificació
    id: int | None = None
    uuid: str | None = None
    xref: str | None = None

    # Nom (es podrien usar value objects, però el mantenim simple).
    given_name: Optional[str] = None
    surname: Optional[str] = None
    prefix: Optional[str] = None
    suffix: Optional[str] = None

    # Dades vitals
    sex: Optional[str] = None
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    notes: Optional[str] = None

    # Camps de cerca precalculats
    search_name: Optional[str] = None
    slug: Optional[str] = None
    soundex: Optional[str] = None
    metaphone: Optional[str] = None

    # Llistats de relacions (UUID o ID) per in a mjukut de la persistència.
    event_ids: list[int] = field(default_factory=list)
    family_as_child_ids: list[int] = field(default_factory=list)
    family_as_spouse_ids: list[int] = field(default_factory=list)

    @property
    def display_name(self) -> str:
        """Nom llegible de la persona."""
        name = " ".join(
            part for part in (self.given_name or "", self.surname or "") if part
        )
        return name or (self.xref or "")

    def add_event(self, event_id: int) -> None:
        if event_id not in self.event_ids:
            self.event_ids.append(event_id)
