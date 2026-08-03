"""Repositoris específics per als recursos principals.

API -> Service -> Repository -> SQLAlchemy.
"""

from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.orm import selectinload

from app.models import Event, Family, ParentChild, Person, Place
from app.repositories.base import BaseRepository


class PersonRepository(BaseRepository[Person]):
    """Repositori de dades per a `Person`."""

    model = Person

    def get_by_xref(self, xref: str) -> Person | None:
        return self.session.scalar(select(Person).where(Person.xref == xref))

    def get_by_uuid(self, uuid: str) -> Person | None:
        return self.session.scalar(select(Person).where(Person.uuid == uuid))

    def search(
        self,
        q: str | None = None,
        sex: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Person]:
        stmt = select(Person)
        if q:
            like = f"%{q}%"
            stmt = stmt.where(
                or_(Person.given_name.ilike(like), Person.surname.ilike(like))
            )
        if sex:
            stmt = stmt.where(Person.sex == sex)
        return list(
            self.session.scalars(
                stmt.order_by(Person.surname, Person.given_name)
                .limit(limit)
                .offset(offset)
            )
        )

    def get_with_detail(self, person_id: int) -> Person | None:
        stmt = (
            select(Person)
            .where(Person.id == person_id)
            .options(
                selectinload(Person.events).selectinload(Event.place),
                selectinload(Person.families_as_father),
                selectinload(Person.families_as_mother),
                selectinload(Person.child_links).selectinload(ParentChild.family),
            )
        )
        return self.session.scalar(stmt)

    def count(self) -> int:
        return self.session.scalar(select(func.count(Person.id))) or 0


class FamilyRepository(BaseRepository[Family]):
    """Repositori de dades per a `Family`."""

    model = Family

    def get_by_xref(self, xref: str) -> Family | None:
        return self.session.scalar(select(Family).where(Family.xref == xref))

    def _members_options(self):
        return (
            selectinload(Family.father),
            selectinload(Family.mother),
            selectinload(Family.parent_children).joinedload(ParentChild.child),
            selectinload(Family.events).selectinload(Event.place),
        )

    def list_with_members(self, limit: int = 50, offset: int = 0) -> list[Family]:
        stmt = (
            select(Family)
            .options(*self._members_options())
            .order_by(Family.id)
            .limit(limit)
            .offset(offset)
        )
        return list(self.session.scalars(stmt))

    def get_with_members(self, family_id: int) -> Family | None:
        stmt = (
            select(Family)
            .where(Family.id == family_id)
            .options(*self._members_options())
        )
        return self.session.scalar(stmt)

    def count(self) -> int:
        return self.session.scalar(select(func.count(Family.id))) or 0


class PlaceRepository(BaseRepository[Place]):
    """Repositori de dades per a `Place`."""

    model = Place

    def get_by_canonical_name(self, canonical: str) -> Place | None:
        return self.session.scalar(
            select(Place).where(Place.canonical_name == canonical)
        )

    def get_by_name(self, name: str) -> Place | None:
        return self.session.scalar(select(Place).where(Place.name == name))

    def list(
        self, q: str | None = None, limit: int = 100, offset: int = 0
    ) -> list[Place]:
        stmt = select(Place)
        if q:
            stmt = stmt.where(Place.name.ilike(f"%{q}%"))
        return list(
            self.session.scalars(stmt.order_by(Place.name).limit(limit).offset(offset))
        )

    def count(self) -> int:
        return self.session.scalar(select(func.count(Place.id))) or 0
