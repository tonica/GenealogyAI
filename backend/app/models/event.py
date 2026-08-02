from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.family import Family
    from app.models.media import Media
    from app.models.place import Place
    from app.models.person import Person
    from app.models.source import Source


class Event(TimestampMixin, Base):
    """Esdeveniment vital associat a una persona, familia o lloc."""

    __tablename__ = "events"
    __table_args__ = (
        Index("ix_events_person", "person_id"),
        Index("ix_events_family", "family_id"),
        Index("ix_events_place", "place_id"),
        Index("ix_events_type", "event_type"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    event_type: Mapped[str] = mapped_column(
        String(100),
        comment="birth | marriage | death | cencer | ...",
    )
    date_text: Mapped[Optional[str]] = mapped_column(String(100))
    # Campos normalitzats del text anterior (per filtrar i estadistiques).
    date_iso: Mapped[Optional[str]] = mapped_column(String(10), index=True)
    date_year: Mapped[Optional[int]] = mapped_column(Integer, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)
    person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL")
    )
    family_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("families.id", ondelete="SET NULL")
    )
    place_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("places.id", ondelete="SET NULL")
    )

    # --- Relacions ---
    person: Mapped[Optional[Person]] = relationship(back_populates="events")
    family: Mapped[Optional[Family]] = relationship(back_populates="events")
    place: Mapped[Optional[Place]] = relationship(back_populates="events")
    media: Mapped[list[Media]] = relationship(
        back_populates="event",
        cascade="all, delete-orphan",
    )
    sources: Mapped[list[Source]] = relationship(
        secondary="event_sources",
        back_populates="events",
    )

    def __repr__(self) -> str:
        return f"<Event id={self.id} type={self.event_type!r}>"
