from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Index, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.associations import event_sources, person_sources
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.media import Media
    from app.models.person import Person


class Source(UUIDMixin, TimestampMixin, Base):
    """Font o cita genealogica que avala persons i esdeveniments."""

    __tablename__ = "sources"
    __table_args__ = (
        UniqueConstraint("title", name="uq_sources_title"),
        Index("ix_sources_url", "url"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    xref: Mapped[str] = mapped_column(String(255), index=True)
    title: Mapped[str] = mapped_column(String(500))
    author: Mapped[Optional[str]] = mapped_column(String(255))
    publication: Mapped[Optional[str]] = mapped_column(String(500))
    url: Mapped[Optional[str]] = mapped_column(String(1000))
    citation: Mapped[Optional[str]] = mapped_column(Text)

    # --- Relacions ---
    persons: Mapped[list[Person]] = relationship(
        secondary=person_sources,
        back_populates="sources",
    )
    events: Mapped[list[Event]] = relationship(
        secondary=event_sources,
        back_populates="sources",
    )
    media: Mapped[list[Media]] = relationship(
        back_populates="source",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Source id={self.id} title={self.title!r}>"
