from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.person import Person


class Suggestion(TimestampMixin, Base):
    """Sugerencia (humana o generada per IA) per avançar en la recerca."""

    __tablename__ = "suggestions"
    __table_args__ = (
        Index("ix_suggestions_person", "person_id"),
        Index("ix_suggestions_status", "status"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    person_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("persons.id", ondelete="CASCADE")
    )
    suggestion_type: Mapped[str] = mapped_column(
        String(50),
        comment="hint | record_match | ai_generated | todo",
    )
    title: Mapped[str] = mapped_column(String(300))
    body: Mapped[Optional[str]] = mapped_column(Text)
    confidence: Mapped[Optional[float]] = mapped_column(Float)
    status: Mapped[str] = mapped_column(
        String(20),
        default="open",
        server_default="open",
        comment="open | accepted | dismissed | done",
    )

    # --- Relacions ---
    person: Mapped[Optional[Person]] = relationship(back_populates="suggestions")

    def __repr__(self) -> str:
        return f"<Suggestion id={self.id} type={self.suggestion_type!r}>"
