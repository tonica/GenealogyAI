from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.parent_child import ParentChild
    from app.models.person import Person


class Family(TimestampMixin, Base):
    """Unit familiar (parella + fills)."""

    __tablename__ = "families"
    __table_args__ = (
        UniqueConstraint("xref", name="uq_families_xref"),
        Index("ix_families_father", "father_id"),
        Index("ix_families_mother", "mother_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    xref: Mapped[Optional[str]] = mapped_column(String(255))
    father_id: Mapped[Optional[int]] = mapped_column(ForeignKey("persons.id"))
    mother_id: Mapped[Optional[int]] = mapped_column(ForeignKey("persons.id"))
    marriage_date: Mapped[Optional[str]] = mapped_column(String(100))
    marriage_place: Mapped[Optional[str]] = mapped_column(String(255))

    # --- Relacions ---
    father: Mapped[Optional[Person]] = relationship(
        "Person",
        foreign_keys=[father_id],
        backref="families_as_father",
    )
    mother: Mapped[Optional[Person]] = relationship(
        "Person",
        foreign_keys=[mother_id],
        backref="families_as_mother",
    )
    parent_children: Mapped[list[ParentChild]] = relationship(
        back_populates="family",
        cascade="all, delete-orphan",
    )
    children: Mapped[list[Person]] = relationship(
        secondary="parent_children",
        primaryjoin="Family.id == ParentChild.family_id",
        secondaryjoin="ParentChild.child_id == Person.id",
        viewonly=True,
        order_by="ParentChild.sibling_order",
    )
    events: Mapped[list[Event]] = relationship(
        back_populates="family",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Family id={self.id} xref={self.xref!r}>"
