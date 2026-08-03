from __future__ import annotations

from typing import Optional

from sqlalchemy import Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base
from app.models.mixins import TimestampMixin, UUIDMixin


class AuditLog(UUIDMixin, TimestampMixin, Base):
    """Registre d'auditoria d'accions sobre entitats.

    Es deixa preparada per quan es necessiti, per exemple, registrar
    canvis (edició, eliminació, imports). En aquest sprint encara no
    s'utilitza des de cap servei; només existeix el model.
    """

    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("ix_audit_logs_entity", "entity_type", "entity_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_user", "user"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    entity_type: Mapped[str] = mapped_column(
        String(50), comment="person | family | place | event | ..."
    )
    entity_id: Mapped[str] = mapped_column(
        String(255), comment="UUID o id enter de la entitat afectada"
    )
    action: Mapped[str] = mapped_column(
        String(50), comment="create | update | delete | import | ..."
    )
    user: Mapped[Optional[str]] = mapped_column(String(255))
    payload_json: Mapped[Optional[str]] = mapped_column(
        Text, comment="Canvis o metadades de l'accio (JSON serialitzat)"
    )

    def __repr__(self) -> str:
        return f"<AuditLog id={self.id} action={self.action!r}>"
