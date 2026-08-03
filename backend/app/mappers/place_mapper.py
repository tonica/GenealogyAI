"""Mapper bidireccional Place ORM <-> Place de domínio."""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.domain.entities import Place as DomainPlace

if TYPE_CHECKING:
    from app.models import Place as ORMPlace


class PlaceMapper:
    """Converteix entre el model ORM `Place` i l'entitat de domínio."""

    @staticmethod
    def to_domain(orm: "ORMPlace") -> DomainPlace:
        return DomainPlace(
            id=orm.id,
            uuid=orm.uuid,
            name=orm.name,
            display_name=orm.display_name,
            canonical_name=orm.canonical_name,
            country=orm.country,
            region=orm.region,
            province=orm.province,
            municipality=orm.municipality,
            latitude=orm.latitude,
            longitude=orm.longitude,
            geohash=orm.geohash,
            slug=orm.slug,
        )

    @staticmethod
    def from_orm(orm: "ORMPlace") -> DomainPlace:
        return PlaceMapper.to_domain(orm)

    @staticmethod
    def to_orm(domain: DomainPlace, orm: "ORMPlace | None" = None) -> "ORMPlace":
        from app.models import Place as ORPlace

        target = orm or ORPlace()
        target.name = domain.name
        target.display_name = domain.display_name
        target.canonical_name = domain.canonical_name
        target.country = domain.country
        target.region = domain.region
        target.province = domain.province
        target.municipality = domain.municipality
        target.latitude = domain.latitude
        target.longitude = domain.longitude
        target.geohash = domain.geohash
        target.slug = domain.slug
        return target
