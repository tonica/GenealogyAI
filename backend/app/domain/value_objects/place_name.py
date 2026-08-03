"""Value object `PlaceName`.

Representa una altitud de la forma canònica que facilita la dedupe i la
futura geccodificació, sense dependre de serveis externs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceName:
    """Lloc i jerarquia administrativa normalitzada (sense geccodificar)."""

    name: str
    country: str | None = None
    region: str | None = None
    province: str | None = None
    municipality: str | None = None

    @property
    def display(self) -> str:
        return self.name or ""

    @property
    def canonical(self) -> str:
        return _canonicalize(self.display)

    @property
    def slug(self) -> str:
        return _slugify(self.display)


def _canonicalize(value: str) -> str:
    return _slugify(value)


def _slugify(value: str) -> str:
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text
