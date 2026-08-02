from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin

if TYPE_CHECKING:
    from app.models.event import Event


class Place(TimestampMixin, Base):
    """Localitat normalitzada reutilitzable entre causa/esdeveniments."""

    __tablename__ = "places"
    __table_args__ = (UniqueConstraint("name", name="uq_places_name"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)

    # --- Relacions ---
    events: Mapped[list["Event"]] = relationship(
        back_populates="place",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Place id={self.id} name={self.name!r}>"
