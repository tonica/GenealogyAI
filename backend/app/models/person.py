from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.media import Media
    from app.models.parent_child import ParentChild
    from app.models.source import Source
    from app.models.suggestion import Suggestion


class Person(TimestampMixin, Base):
    """Individu d'un arbre genealogic."""

    __tablename__ = "persons"
    __table_args__ = (
        UniqueConstraint("xref", name="uq_persons_xref"),
        Index("ix_persons_surname_given_name", "surname", "given_name"),
        Index("ix_persons_sex", "sex"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    xref: Mapped[str] = mapped_column(
        String(255), comment="Identificador '@I1@' dins el GEDCOM"
    )
    given_name: Mapped[Optional[str]] = mapped_column(String(255))
    surname: Mapped[Optional[str]] = mapped_column(String(255))
    prefix: Mapped[Optional[str]] = mapped_column(String(50))
    suffix: Mapped[Optional[str]] = mapped_column(String(50))
    sex: Mapped[Optional[str]] = mapped_column(String(1), comment="M | F | U")
    birth_date: Mapped[Optional[str]] = mapped_column(String(100))
    death_date: Mapped[Optional[str]] = mapped_column(String(100))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    # --- Relacions ---
    events: Mapped[list[Event]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )
    parent_links: Mapped[list[ParentChild]] = relationship(
        back_populates="parent",
        foreign_keys="ParentChild.parent_id",
        cascade="all, delete-orphan",
    )
    child_links: Mapped[list[ParentChild]] = relationship(
        back_populates="child",
        foreign_keys="ParentChild.child_id",
        cascade="all, delete-orphan",
    )
    sources: Mapped[list[Source]] = relationship(
        secondary="person_sources",
        back_populates="persons",
    )
    media: Mapped[list[Media]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )
    suggestions: Mapped[list[Suggestion]] = relationship(
        back_populates="person",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Person id={self.id} xref={self.xref!r}>"
