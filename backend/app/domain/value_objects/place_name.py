"""Value object `PlaceName`.

Representa un lloc amb la seva forma canònica, tokens i mètodes de
similitud per a la dedupe i la futura geocodificació. No geocodifica.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceName:
    """Lloc i jerarquia administrativa normalitzada (sense geocodificar)."""

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

    def normalized(self) -> str:
        """Versió normalitzada (minúscules, sense accents, sense signes)."""
        return _normalize(self.display)

    @property
    def tokens(self) -> list[str]:
        """Tokens significatius del lloc (per a comparació i agrupació)."""
        words = [w for w in self.normalized().split() if w not in _STOPWORDS]
        return words

    def display_name(self) -> str:
        return self.display

    def canonical_name(self) -> str:
        return self.canonical

    def similarity(self, other: "PlaceName") -> float:
        """Similitud (0..1) entre dos llocs per tokens en comú."""
        a = set(self.tokens)
        b = set(other.tokens)
        if not a or not b:
            return 0.0
        if self.normalized() == other.normalized():
            return 1.0
        union = a | b
        return round(len(a & b) / len(union), 2)

    def contains(self, other: "PlaceName") -> bool:
        """Aquest lloc conté l'altre (p. ex. "Barcelona" conté "Sarrià")."""
        a = set(self.tokens)
        b = set(other.tokens)
        return bool(b) and b.issubset(a)

    def matches(self, other: "PlaceName") -> bool:
        """Coincidència exacta per canonical o similarity alta."""
        return (
            self.canonical == other.canonical
            or self.normalized() == other.normalized()
            or self.similarity(other) >= 0.8
        )


_STOPWORDS = frozenset(
    {"la", "el", "els", "les", "de", "del", "dels", "l", "san", "santa", "st"}
)


def _normalize(value: str) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()


def _canonicalize(value: str) -> str:
    return _normalize(value).replace(" ", "-")


def _slugify(value: str) -> str:
    import re

    return re.sub(r"[^a-z0-9]+", "-", _normalize(value)).strip("-")
