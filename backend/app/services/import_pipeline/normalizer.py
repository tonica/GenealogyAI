"""Etapa de normalització del pipeline: `Normalizer`.

Pura (no toca BDD): a partir d'un `GedcomDocument` final retorna els camps
normalitzats per persona (nom, cognoms, search_name, slug, soundex,
metaphone). Pretens que el Resolver només hagués de mapejar a ORM.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.importer.models import GedcomDocument
from app.services.search import metaphone, soundex
from app.utils.search import build_search_name, slugify
from app.utils.text import normalize_surname


@dataclass
class NormalizedFields:
    """Camps normalitzats d'una persona preparats pel Resolver."""

    given_name: str | None = None
    surname: str | None = None
    search_name: str | None = None
    slug: str | None = None
    soundex: str | None = None
    metaphone: str | None = None


def _title_given(given: str | None) -> str | None:
    if not given or not given.strip():
        return given
    return " ".join(
        part.capitalize() if part[:1].isalpha() else part for part in given.split()
    )


class Normalizer:
    """Etape neutra que prepara els camps per cada person neutra."""

    def normalize_person(
        self, given: str | None, surname: str | None
    ) -> NormalizedFields:
        given_n = _title_given(given)
        surname_n = normalize_surname(surname)
        full = " ".join(p for p in (given_n, surname_n) if p).strip()
        return NormalizedFields(
            given_name=given_n,
            surname=surname_n,
            search_name=build_search_name(given_n, surname_n) or None,
            slug=slugify(full),
            soundex=soundex(surname_n) if surname_n else None,
            metaphone=metaphone(full),
        )

    def normalize_document(self, doc: GedcomDocument) -> dict[str, NormalizedFields]:
        """Torna un mapa xref -> camps normalitzats per a cada persona."""
        out: dict[str, NormalizedFields] = {}
        for person in doc.persons:
            name = person.primary_name
            out[person.xref] = self.normalize_person(
                name.given if name else None,
                name.surname if name else None,
            )
        return out
