"""Etapa de validação do pipeline: `Validator`.

Pura: comprova la coherencia dun document neutra (referencias, dates,
duplicados, nomes) e retorna a lista de problemas.
"""

from __future__ import annotations

from app.importer.models import GedcomDocument
from app.services.stats import ImportIssue, detect_errors


class Validator:
    """Valida o documento neutra e retorna os problemas detectados."""

    def validate(self, doc: GedcomDocument) -> list[ImportIssue]:
        return detect_errors(doc)
