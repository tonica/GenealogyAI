"""Mappers: conversió ORM (SQLAlchemy) <-> Domain (pures).

Cap servei ha de convertir manualment objectes entre la capa de cultura i
el domínio; tot passa per aquests mappers bidireccionals.
"""

from app.mappers.event_mapper import EventMapper
from app.mappers.family_mapper import FamilyMapper
from app.mappers.person_mapper import PersonMapper
from app.mappers.place_mapper import PlaceMapper

__all__ = ["EventMapper", "FamilyMapper", "PersonMapper", "PlaceMapper"]
