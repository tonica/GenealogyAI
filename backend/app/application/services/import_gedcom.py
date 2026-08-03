"""Cas d'ús: importar un document GEDCOM.

Coordina el pipeline d'importació existent i el UnitOfWork per assegurar
una transacció única (commit al final). Manté el resultat de la capa web.
"""

from __future__ import annotations

from typing import Any

from app.application.unit_of_work import AbstractUnitOfWork
from app.services.import_pipeline import ImportResult, import_gedcom


class ImportGedcomUseCase:
    """Envolta la importació per assegurar una transacció única."""

    def __init__(self, uow: AbstractUnitOfWork) -> None:
        self.uow = uow

    def execute(self, doc: Any, rebuild_search_index: bool = True) -> ImportResult:
        # El pipeline treballa sobre la mateixa sessió del UoW.
        result = import_gedcom(self.uow._session, doc)
        self.uow.commit()
        return result
