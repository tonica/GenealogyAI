"""Resultat neutre de l'importació, compatible amb l'antic `ImportResult`.

Es manté aquí perquè el pipeline el produeix; l'antic mòdul
`app.services.importer` reexporta/utilitza els mateixos camps.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.stats import ImportIssue, ImportStats


@dataclass
class ImportResult:
    """Resum de la importacio."""

    persons: int = 0
    families: int = 0
    sources: int = 0
    media: int = 0
    places: int = 0
    events: int = 0
    children: int = 0
    issues: list[ImportIssue] = field(default_factory=list)
    stats: ImportStats = field(default_factory=ImportStats)
    elapsed_ms: int = 0
    rebuilt_index: bool = False

    def to_dict(self) -> dict:
        return {
            "persons": self.persons,
            "families": self.families,
            "sources": self.sources,
            "media": self.media,
            "places": self.places,
            "events": self.events,
            "children": self.children,
            "issues": [iss.__dict__ for iss in self.issues],
            "stats": self.stats.to_dict(),
            "elapsed_ms": self.elapsed_ms,
            "rebuilt_index": self.rebuilt_index,
        }
