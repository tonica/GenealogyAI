"""Pipeline d'importació orquestrada.

Encadena les etapes independentes (Validator, Normalizer, Resolver,
Importer) sobre una sessió, aplica els pragmes de commit/rollback i
reconstrueix l'índex de cerca final si està configurat.
"""

from __future__ import annotations

import time

from sqlalchemy.orm import Session

from app.importer.models import GedcomDocument
from app.repositories import FamilyRepository, PersonRepository, PlaceRepository
from app.services.import_pipeline.importer import Importer
from app.services.import_pipeline.normalizer import Normalizer
from app.services.import_pipeline.resolver import Resolver
from app.services.import_pipeline.response import ImportResult
from app.services.import_pipeline.validator import Validator


class ImportPipeline:
    """Encadena les etapes d'importació sobre una sessió SQLAlchemy."""

    def __init__(self, session: Session) -> None:
        self.session = session
        self.person_repo = PersonRepository(session)
        self.family_repo = FamilyRepository(session)
        self.place_repo = PlaceRepository(session)
        self.validator = Validator()
        self.normalizer = Normalizer()
        self.resolver = Resolver(session, self.person_repo, self.family_repo)
        self.importer = Importer(session)

    def run(self, doc: GedcomDocument) -> ImportResult:
        issues = self.validator.validate(doc)
        fields = self.normalizer.normalize_document(doc)
        resolved = self.resolver.resolve(doc, fields)

        started = time.perf_counter()
        result = self.importer.persist(doc, resolved, issues)
        self.session.commit()
        result.elapsed_ms = int((time.perf_counter() - started) * 1000)

        from app.core.config import get_settings

        if get_settings().import_.rebuild_search_index:
            from app.services.search import SearchIndexer

            indexer = SearchIndexer(self.session)
            indexer.rebuild()
            result.rebuilt_index = True

        return result
