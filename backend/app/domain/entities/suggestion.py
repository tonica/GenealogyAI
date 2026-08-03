"""Entitat de domínio `Suggestion` (independent de la persistència)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Suggestion:
    """Suggerència (humana o generada per IA)."""

    id: int | None = None
    uuid: str | None = None
    person_id: Optional[int] = None
    suggestion_type: str = ""
    title: str = ""
    body: Optional[str] = None
    confidence: Optional[float] = None
    status: str = "open"
