"""Entitat de domínio `Place` (independent de la persistència)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.domain.value_objects import PlaceName


@dataclass
class Place:
    """Localitat normalitzada, amb jerarquia administrativa i geografia."""

    id: int | None = None
    uuid: str | None = None

    name: str = ""
    display_name: Optional[str] = None
    canonical_name: Optional[str] = None

    country: Optional[str] = None
    region: Optional[str] = None
    province: Optional[str] = None
    municipality: Optional[str] = None

    latitude: Optional[float] = None
    longitude: Optional[float] = None
    geohash: Optional[str] = None
    slug: Optional[str] = None

    @property
    def name_value(self) -> PlaceName:
        return PlaceName(
            name=self.display_name or self.name,
            country=self.country,
            region=self.region,
            province=self.province,
            municipality=self.municipality,
        )
