from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from sqlalchemy import Float, Index, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.models.event import Event


class Place(UUIDMixin, TimestampMixin, Base):
    """Localitat normalitzada reutilitzable entre causa/esdeveniments.

    `display_name` es el nom tal com apareix a la interfície; els camps
    administratius (country, region, province, municipality) i geogràfics
    (latitude, longitude, geohash) queden preparats per a la futura
    geocodificació, que no s'implementa en aquest sprint.
    """

    __tablename__ = "places"
    __table_args__ = (
        UniqueConstraint("name", name="uq_places_name"),
        Index("ix_places_canonical_name", "canonical_name"),
        Index("ix_places_slug", "slug"),
        Index("ix_places_geohash", "geohash"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    # Nom original / llegible i clau canònica per desduplicar.
    name: Mapped[str] = mapped_column(String(255), index=True)
    display_name: Mapped[Optional[str]] = mapped_column(String(255))
    canonical_name: Mapped[Optional[str]] = mapped_column(String(255))

    # Jerarquia administrativa (preparada per geocodificació futura).
    country: Mapped[Optional[str]] = mapped_column(String(120))
    region: Mapped[Optional[str]] = mapped_column(String(120))
    province: Mapped[Optional[str]] = mapped_column(String(120))
    municipality: Mapped[Optional[str]] = mapped_column(String(120))

    # Coordenades i geohash (preparats; la geocodificació vindrà en un sprint
    # posterior).
    latitude: Mapped[Optional[float]] = mapped_column(Float)
    longitude: Mapped[Optional[float]] = mapped_column(Float)
    geohash: Mapped[Optional[str]] = mapped_column(String(12))

    slug: Mapped[Optional[str]] = mapped_column(String(120))

    # --- Relacions ---
    events: Mapped[list["Event"]] = relationship(
        back_populates="place",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Place id={self.id} name={self.name!r}>"
