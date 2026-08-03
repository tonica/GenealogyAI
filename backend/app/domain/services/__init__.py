"""Serveis de domínio: pura lógica que treballa amb entitats (sense I/O).

No accedeixen a SQLAlchemy ni a cap base de dades; operen únicament sobre
objectes del domínio.
"""

from app.domain.services.duplicate_detector import DuplicateDetector, DuplicateGroup
from app.domain.services.quality_engine import QualityEngine, QualityReport
from app.domain.services.statistics_engine import StatisticsEngine, DomainStats

__all__ = [
    "DomainStats",
    "DuplicateDetector",
    "DuplicateGroup",
    "QualityEngine",
    "QualityReport",
    "StatisticsEngine",
]
