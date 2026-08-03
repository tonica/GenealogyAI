"""Value object `PersonName` i derivació per a la cerca i la dedupació."""

from __future__ import annotations

from dataclasses import dataclass

_PHONETIC_RULES = {
    "B": "1",
    "F": "1",
    "P": "1",
    "V": "1",
    "C": "2",
    "G": "2",
    "J": "2",
    "K": "2",
    "Q": "2",
    "S": "2",
    "X": "2",
    "Z": "2",
    "D": "3",
    "T": "3",
    "L": "4",
    "M": "5",
    "N": "5",
    "R": "6",
}


@dataclass(frozen=True)
class PersonName:
    """Nom de persona normalitzat, sense persistència.

    No modifica mai el nom original: deriva de forma immutable els camps
    per a la cerca i la similitud.
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
        """Slug url-friendly del nom complet."""
        return _slugify(self.full_name)

    def normalized(self) -> str:
        """Versió normalitzada (minúscules, sense accents)."""
        return _normalize(self.full_name)

    def display_name(self) -> str:
        """Nom per a la UI (manté l'original)."""
        return self.full_name

    def initials(self) -> str:
        """Inicials de les parts significatives (ex. "J M")."""
        parts = [
            p for p in (self.given or "", self.middle or "", self.surnames or "") if p
        ]
        return " ".join(p[0].upper() + "." for p in parts if p and p[0].isalpha())

    def phonetic_key(self) -> str:
        """Clau fonètica de la part més rellevant (cognoms o nom)."""
        base = (self.surnames or self.given or "").strip()
        return _phonetic(base)

    def similarity(self, other: "PersonName") -> float:
        """Similitud (0..1) entre dos noms: combinació fonètica + edicio."""
        a_norm = self.normalized()
        b_norm = other.normalized()
        if not a_norm or not b_norm:
            return 0.0
        if a_norm == b_norm:
            return 1.0
        phonetic = self.phonetic_key() == other.phonetic_key()
        edit_sim = _levenshtein_similarity(a_norm, b_norm)
        score = max(edit_sim, 0.55 if phonetic else 0.0)
        return round(score, 2)

    @classmethod
    def from_given_surname(cls, given: str | None, surname: str | None) -> "PersonName":
        return cls(given=given or None, surnames=surname or None)


# ------------------------------------------------------------------ helpers


def _normalize(value: str) -> str:
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()


def _slugify(value: str) -> str:
    import re
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text


def _phonetic(value: str) -> str:
    """Soundex-like (4 caràcters) per a la comparació fonètica."""
    if not value:
        return ""
    norm = _normalize(value)
    chars = [c for c in norm if c.isalpha()]
    if not chars:
        return ""
    first = chars[0].upper()
    code = first
    prev = _PHONETIC_RULES.get(first, "")
    for ch in chars[1:]:
        digit = _PHONETIC_RULES.get(ch.upper(), "")
        if digit and digit != prev:
            code += digit
            if len(code) >= 4:
                break
        prev = digit
    return (code + "000")[:4]


def _levenshtein_similarity(a: str, b: str) -> float:
    if a == b:
        return 1.0
    if not a or not b:
        return 0.0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cost = 0 if ca == cb else 1
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + cost))
        prev = cur
    dist = prev[-1]
    return 1.0 - dist / max(len(a), len(b))
