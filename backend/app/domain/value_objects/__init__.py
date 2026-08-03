"""Value objects del domínio.

Conventions:
  - Són immutables (frozen dataclasses / @property).
  - No depenen de cap infraestructura (SQLAlchemy, Pydantic, FastAPI).
Cada mòdul es documenta i exposa els seus objectes via `__all__`.
"""

from app.domain.value_objects.date_value import DateValue, DatePrecision
from app.domain.value_objects.person_name import PersonName
from app.domain.value_objects.place_name import PlaceName

__all__ = [
    "DatePrecision",
    "DateValue",
    "PersonName",
    "PlaceName",
]
