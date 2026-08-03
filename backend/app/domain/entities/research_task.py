"""Entitat de domínio `ResearchTask` (independent de la persistència).

Placeholder preparat per representar una tasca de recerca genealògica
(per exemple, per a la futura integració d'IA al Sprint 5).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ResearchTask:
    """Una tònc objectiu de recerca sobre una persona.

    Nota: encara no hi ha model ORM per a aquesta entitat; el seu ús
    arribarà amb els futurs sprints (IA i cerca). Es defineix ara per a
    fixar el domini.
    """

    id: int | None = None
    uuid: str | None = None
    person_id: Optional[int] = None
    objective: str = ""
    hypothesis: Optional[str] = None
    status: str = "open"
    related_person_ids: list[int] = field(default_factory=list)
