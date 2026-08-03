"""Entitat de domínio `Source` (independent de la persistència)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Source:
    """Font o cita genealògica."""

    id: int | None = None
    uuid: str | None = None
    xref: str | None = None
    title: str = ""
    author: Optional[str] = None
    publication: Optional[str] = None
    url: Optional[str] = None
    citation: Optional[str] = None
