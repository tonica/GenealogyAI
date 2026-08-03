"""Mapper bidireccional Event ORM <-> Event de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.entities import Event as DomainEvent
from app.domain.value_objects import DateValue

if TYPE_CHECKING:
    from app.models import Event as ORMEvent


class EventMapper:
    """Converteix entre el model ORM `Event` i l'entitat de domínio."""

    @staticmethod
    def to_domain(orm: "ORMEvent") -> DomainEvent:
        dv: DateValue
        if orm.date_iso:
            dv = DateValue.from_iso(orm.date_iso)
            dv = DateValue(
                original_text=orm.date_text or orm.date_iso,
                iso=dv.iso,
                year=dv.year,
                month=dv.month,
                day=dv.day,
                precision=dv.precision,
                normalized_start=dv.normalized_start,
                normalized_end=dv.normalized_end,
            )
        else:
            dv = DateValue(original_text=orm.date_text, year=orm.date_year)
        return DomainEvent(
            id=orm.id,
            uuid=orm.uuid,
            event_type=orm.event_type,
            date_text=orm.date_text,
            date_value=dv,
            date_iso=orm.date_iso,
            date_year=orm.date_year,
            description=orm.description,
            person_id=orm.person_id,
            family_id=orm.family_id,
            place_id=orm.place_id,
        )

    @staticmethod
    def from_orm(orm: "ORMEvent") -> DomainEvent:
        return EventMapper.to_domain(orm)

    @staticmethod
    def to_orm(domain: DomainEvent, orm: "ORMEvent | None" = None) -> "ORMEvent":
        from app.models import Event as ORMEvent

        target = orm or ORMEvent()
        target.event_type = domain.event_type
        target.date_text = domain.date_text
        target.date_iso = domain.date_iso
        target.date_year = domain.date_year
        target.description = domain.description
        target.person_id = domain.person_id
        target.family_id = domain.family_id
        target.place_id = domain.place_id
        return target
