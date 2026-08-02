from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.event import Event
    from app.models.person import Person
    from app.models.source import Source


class Media(TimestampMixin, Base):
    """Recurs multimediatic (imatge, audio...) vinculat a una entitat."""

    __tablename__ = "media"
    __table_args__ = (
        Index("ix_media_person", "person_id"),
        Index("ix_media_event", "event_id"),
        Index("ix_media_source", "source_id"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    xref: Mapped[str] = mapped_column(String(255), index=True)
    file_path: Mapped[str] = mapped_column(String(1000), index=True)
    media_type: Mapped[Optional[str]] = mapped_column(
        String(50),
        comment="image | audio | video | document",
    )
    caption: Mapped[Optional[str]] = mapped_column(String(500))
    person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="SET NULL")
    )
    event_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("events.id", ondelete="SET NULL")
    )
    source_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("sources.id", ondelete="SET NULL")
    )

    # --- Relacions ---
    person: Mapped[Optional[Person]] = relationship(back_populates="media")
    event: Mapped[Optional[Event]] = relationship(back_populates="media")
    source: Mapped[Optional[Source]] = relationship(back_populates="media")

    def __repr__(self) -> str:
        return f"<Media id={self.id} path={self.file_path!r}>"
