"""Serveis de domínio: pura lògica que treballa amb entitats (sense I/O).

No accedeixen a SQLAlchemy ni a cap base de dades; operen únicament sobre
objectes del domínio.
"""

from app.domain.services.date_engine import DateEngine
from app.domain.services.duplicate_detector import (
    DuplicateCandidate,
    DuplicateDetector,
    DuplicateGroup,
)
from app.domain.services.duplicate_rules import DuplicateRule, RuleResult
from app.domain.services.name_resolver import NameResolver, NameSuggestion
from app.domain.services.place_resolver import PlaceResolver, PlaceSuggestion
from app.domain.services.quality_engine import (
    PersonQuality,
    QualityEngine,
    QualityFactor,
    QualityReport,
)
from app.domain.services.quality_report import (
    DataQualityReport,
    DataQualityReportGenerator,
    QualityFinding,
)
from app.domain.services.research_tasks import (
    ResearchTaskGenerator,
    ResearchTaskSuggestion,
)
from app.domain.services.statistics_engine import DomainStats, StatisticsEngine

__all__ = [
    "DataQualityReport",
    "DataQualityReportGenerator",
    "DateEngine",
    "DomainStats",
    "DuplicateCandidate",
    "DuplicateDetector",
    "DuplicateGroup",
    "DuplicateRule",
    "NameResolver",
    "NameSuggestion",
    "PersonQuality",
    "PlaceResolver",
    "PlaceSuggestion",
    "QualityEngine",
    "QualityFactor",
    "QualityFinding",
    "QualityReport",
    "ResearchTaskGenerator",
    "ResearchTaskSuggestion",
    "RuleResult",
    "StatisticsEngine",
]
