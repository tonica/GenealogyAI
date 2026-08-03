"""Mapper bidireccional Person ORM <-> Person de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.entities import Person as DomainPerson

if TYPE_CHECKING:
    from app.models import Person as ORMPerson


class PersonMapper:
    """Converteix entre el model ORM `Person` i l'entitat de domínio."""

    @staticmethod
    def to_domain(orm: "ORMPerson") -> DomainPerson:
        return DomainPerson(
            id=orm.id,
            uuid=orm.uuid,
            xref=orm.xref,
            given_name=orm.given_name,
            surname=orm.surname,
            prefix=orm.prefix,
            suffix=orm.suffix,
            sex=orm.sex,
            birth_date=orm.birth_date,
            death_date=orm.death_date,
            notes=orm.notes,
            search_name=orm.search_name,
            slug=orm.slug,
            soundex=orm.soundex,
            metaphone=orm.metaphone,
            event_ids=[e.id for e in orm.events] if orm.events else [],
        )

    @staticmethod
    def from_orm(orm: "ORMPerson") -> DomainPerson:
        return PersonMapper.to_domain(orm)

    @staticmethod
    def to_orm(domain: DomainPerson, orm: "ORMPerson | None" = None) -> "ORMPerson":
        """Converteix de domínio a ORM.

        Reutilitza una instància ORM (`orm`) per no perdre la identitat a
        la sessió (relacions, id); en cas contrario en crea una de nova.
        """
        from app.models import Person as ORMPerson

        target = orm or ORMPerson()
        target.xref = domain.xref
        target.given_name = domain.given_name
        target.surname = domain.surname
        target.prefix = domain.prefix
        target.suffix = domain.suffix
        target.sex = domain.sex
        target.birth_date = domain.birth_date
        target.death_date = domain.death_date
        target.notes = domain.notes
        target.search_name = domain.search_name
        target.slug = domain.slug
        target.soundex = domain.soundex
        target.metaphone = domain.metaphone
        return target
