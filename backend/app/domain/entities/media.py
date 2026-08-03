"""Entitat de domínio `Media` (independent de la persistència)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Media:
    """Recurs multimediàtic (imatge, àudio, ...)."""

    id: int | None = None
    uuid: str | None = None
    xref: str | None = None
    file_path: str = ""
    media_type: Optional[str] = None
    caption: Optional[str] = None
    person_id: Optional[int] = None
    event_id: Optional[int] = None
    source_id: Optional[int] = None
