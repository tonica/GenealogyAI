"""Servei d'importació (punt d'entrada públic).

Compatibilitat: mantením la mateixa funció `import_gedcom(session, doc)`
que usava l'API i els tests, però ara delega al pipeline d'importació
orquestrat (Validator -> Normalizer -> Resolver -> Importer -> Repository).
"""

from __future__ import annotations

from app.services.import_pipeline import ImportResult, import_gedcom

__all__ = ["ImportResult", "import_gedcom"]
