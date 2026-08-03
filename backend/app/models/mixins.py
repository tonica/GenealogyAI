from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Afegeix marques de creacio i modificacio a un model."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Afegeix un identificador públic `uuid` (v4) a una entitat.

    L'ID enter segueix sent la Primary Key interna; el UUID serveix per
    exposar l'entitat a l'API i per a sincronitzacio futura entre
    dispositius o instancies, sense revelar els IDs seqüencials interns.
    """

    uuid: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        unique=True,
        index=True,
        default=lambda: str(uuid4()),
        comment="Identificador públic (UUID v4) per API i sincronització",
    )
