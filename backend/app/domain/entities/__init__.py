"""Entitats del domínio.

Les entitats del domínio són objectes Python purs, sense cap dependència
de la infraestructura (SQLAlchemy, Pydantic, FastAPI). Representen només
la lógica de negoci i són l'única cosa que els serveis de domínio coneixen.
"""

from app.domain.entities.event import Event
from app.domain.entities.family import Family
from app.domain.entities.media import Media
from app.domain.entities.person import Person
from app.domain.entities.place import Place
from app.domain.entities.research_task import ResearchTask
from app.domain.entities.source import Source
from app.domain.entities.suggestion import Suggestion

__all__ = [
    "Event",
    "Family",
    "Media",
    "Person",
    "Place",
    "ResearchTask",
    "Source",
    "Suggestion",
]
