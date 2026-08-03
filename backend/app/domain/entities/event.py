"""Entitat de domínio `Event` (independent de la persistència)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Optional

from app.domain.value_objects import DateValue

if TYPE_CHECKING:
    from app.domain.entities.place import Place


@dataclass
class Event:
    """Esdeveniment vital (naixement, mort, matrimoni...).

    Usa value objects (`DateValue`) per a les dates normalitzades.
    """

    id: int | None = None
    uuid: str | None = None
    xref: str | None = None
    event_type: str | None = None
    date_text: Optional[str] = None
    date_value: Optional[DateValue] = None
    date_iso: Optional[str] = None
    date_year: Optional[int] = None
    description: Optional[str] = None

    person_id: Optional[int] = None
    family_id: Optional[int] = None
    place_id: Optional[int] = None
    place: "Place | None" = None

    # Relacions
    source_ids: list[int] = field(default_factory=list)
    media_ids: list[int] = field(default_factory=list)
