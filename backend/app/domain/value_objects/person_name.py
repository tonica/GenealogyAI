"""Value object `PersonName` i la seva derivació per a la seva cerca."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PersonName:
    """Nom de persona normalitzat, sense persistència.

    Agrupa el nom i els cognoms d'una persona per poder construir de
    forma consistent el `search_name`, el `slug` i la resta de derivats
    que fem servir per a la inscripció i la cerca.
    """

    given: str | None = None
    middle: str | None = None
    surnames: str | None = None
    prefix: str | None = None
    suffix: str | None = None

    @property
    def full_name(self) -> str:
        return " ".join(
            part
            for part in (
                self.prefix or "",
                self.given or "",
                self.middle or "",
                self.surnames or "",
                self.suffix or "",
            )
            if part
        ).strip()

    @property
    def search_name(self) -> str:
        """Concactena les parts per a la cerca full-text."""
        return self.full_name

    @property
    def slug(self) -> str:
        """Slug simple (per compatibilitat; pot ampliar-se amb `slugify`)."""
        return _slugify(self.full_name)

    @classmethod
    def from_given_surname(cls, given: str | None, surname: str | None) -> "PersonName":
        return cls(given=given or None, surnames=surname or None)


def _slugify(value: str) -> str:
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text
