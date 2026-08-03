"""Import pipeline — stages encadenats.

Flux:
    GEDCOM Parser  ->  Validator  ->  Normalizer  ->  Resolver
        ->  Importer  ->  Repositories  ->  Database

`import_gedcom` és el punt d'entrada únic; a l'antic
`app.services.importer` es manté com a wrappaer per compatibilitat.

Cada etapa és una classe independent i testeable.
"""

from __future__ import annotations

from app.services.import_pipeline.response import ImportResult
from app.services.import_pipeline.pipeline import ImportPipeline

__all__ = [
    "ImportPipeline",
    "ImportResult",
    "import_gedcom",
]


def import_gedcom(session, doc) -> ImportResult:
    """Executa el pipeline complet. Keep main-compatible amb l'antic mòdul."""
    return ImportPipeline(session).run(doc)
