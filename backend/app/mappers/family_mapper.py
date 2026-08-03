"""Mapper bidireccional Family ORM <-> Family de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.entities import Family as DomainFamily

if TYPE_CHECKING:
    from app.models import Family as ORMFamily


class FamilyMapper:
    """Converteix entre el model ORM `Family` i l'entitat de domínio."""

    @staticmethod
    def to_domain(orm: "ORMFamily") -> DomainFamily:
        return DomainFamily(
            id=orm.id,
            uuid=orm.uuid,
            xref=orm.xref,
            father_id=orm.father_id,
            mother_id=orm.mother_id,
            marriage_date=orm.marriage_date,
            marriage_place=orm.marriage_place,
            event_ids=[e.id for e in orm.events] if orm.events else [],
            child_ids=(
                [pc.child_id for pc in orm.parent_children]
                if orm.parent_children
                else []
            ),
        )

    @staticmethod
    def from_orm(orm: "ORMFamily") -> DomainFamily:
        return FamilyMapper.to_domain(orm)

    @staticmethod
    def to_orm(domain: DomainFamily, orm: "ORMFamily | None" = None) -> "ORMFamily":
        from app.models import Family as ORMFamily

        target = orm or ORMFamily()
        target.xref = domain.xref
        target.father_id = domain.father_id
        target.mother_id = domain.mother_id
        target.marriage_date = domain.marriage_date
        target.marriage_place = domain.marriage_place
        return target
