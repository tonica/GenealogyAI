"""Serveis d'aplicació (use cases).

CAP layer que coordina repositoris, serveis de domínio i UnitOfWork per
complir un cas d'ús concret. No conté lògica de negoci; només orquestra.
"""

from app.application.services.generate_statistics import GenerateStatisticsUseCase
from app.application.services.get_person import GetPersonUseCase
from app.application.services.import_gedcom import ImportGedcomUseCase
from app.application.services.merge_persons import MergePersonsUseCase

__all__ = [
    "GenerateStatisticsUseCase",
    "GetPersonUseCase",
    "ImportGedcomUseCase",
    "MergePersonsUseCase",
]
