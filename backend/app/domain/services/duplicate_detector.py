"""Servei de domínio `DuplicateDetector`.

Detecta possibles persones duplicades per regles de similitud purament
de domínio (nom, cognom, dates). No fa cap consulta a la base de dades;
rep llistats d'entitats `Person` i dedueix grups candidats a combinació.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.domain.entities import Person


def _norm(value: str | None) -> str:
    """Normalitza a minúscules i sense accents per comparar noms."""
    if not value:
        return ""
    import unicodedata

    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    return text.lower().strip()


@dataclass
class DuplicateGroup:
    """Grup de persones candidates a ser la mateixa (duplicades)."""

    persons: list[Person] = field(default_factory=list)
    reason: str = ""

    @property
    def size(self) -> int:
        return len(self.persons)

    @property
    def ids(self) -> list[int]:
        return [p.id for p in self.persons if p.id is not None]


class DuplicateDetector:
    """Pura regla de negoci per agrupar persones probablement duplicades."""

    def __init__(
        self,
        match_on_surname: bool = True,
        require_year: bool = False,
    ) -> None:
        self.match_on_surname = match_on_surname
        self.require_year = require_year

    def find_duplicates(self, persons: list[Person]) -> list[DuplicateGroup]:
        """Agrupa persones que comparteixen nom + (cognom) + any de naixement."""
        buckets: dict[tuple, list[Person]] = {}
        for p in persons:
            given = _norm(p.given_name)
            surname = _norm(p.surname)
            if self.match_on_surname:
                key_parts = (given, surname)
            else:
                key_parts = (given,)
            if self.require_year and p.birth_date:
                year = self._year_of(p.birth_date)
                key_parts = key_parts + (year,)

            bucket_key = "*".join(part for part in key_parts if part)
            if bucket_key:
                buckets.setdefault(bucket_key, []).append(p)

        return [
            DuplicateGroup(persons=group, reason=f"nom similar ({key})")
            for key, group in buckets.items()
            if len(group) > 1
        ]

    @staticmethod
    def _year_of(date_text: str) -> str:
        # Heurística simple per al domínio: busca els primers 4 dígits.
        import re

        m = re.search(r"\b(1[5-9]\d{2}|2\d{3})\b", date_text)
        return m.group(1) if m else ""

    def is_likely_duplicate(self, a: Person, b: Person) -> tuple[bool, str]:
        given = _norm(a.given_name) == _norm(b.given_name) and bool(_norm(a.given_name))
        surname = _norm(a.surname) == _norm(b.surname) and bool(_norm(a.surname))
        if given and (surname or not self.match_on_surname):
            return True, "nom i cognom idèntics"
        if not given and surname:
            return False, "cognom idèntic però sense nom"
        return False, "no coincideix"
