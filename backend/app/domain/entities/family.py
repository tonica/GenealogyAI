"""Entitat de domínio `Family` (independent de la persistència)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Family:
    """Unitat familiar (parella + fills)."""

    id: int | None = None
    uuid: str | None = None
    xref: str | None = None

    father_id: Optional[int] = None
    mother_id: Optional[int] = None
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None

    # Relacions
    event_ids: list[int] = field(default_factory=list)
    child_ids: list[int] = field(default_factory=list)

    def add_child(self, child_id: int) -> None:
        if child_id not in self.child_ids:
            self.child_ids.append(child_id)
