"""Capacitat de repositoris (Repository Pattern).

Un repositori encapsula l'accés a dades d'un recurs concret sobre la
sessió SQLAlchemy, de manera que els serveis (i repos per sobre) maneguin
abstraccions de col·lecció i no detalls de SQL.

L'API actual no canvia: els endpoints continuen rebent/emitint el mateix
format, només que ara l'accés a dades passa per aquesta capa enlloc de
fer `db.scalars(select(...))` directament al route.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

ModelT = TypeVar("ModelT")


class BaseRepository(Generic[ModelT]):
    """Repositori genée de lectura/escriptura per a un model SQLAlchemy."""

    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def all(self) -> list[ModelT]:
        return list(self.session.scalars(select(self.model)))

    def add(self, instance: ModelT) -> ModelT:
        self.session.add(instance)
        return instance

    def add_all(self, instances: list[ModelT]) -> list[ModelT]:
        if instances:
            self.session.add_all(instances)
        return instances

    def delete(self, instance: ModelT) -> None:
        self.session.delete(instance)

    def flush(self) -> None:
        """Força la sincronització de la sessió amb la DB (assigna IDs)."""
        self.session.flush()
