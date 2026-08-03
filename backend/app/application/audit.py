"""Constants de raó per a esdeveniments d'auditoria."""

from __future__ import annotations

from enum import Enum


class AuditReason(str, Enum):
    """Raó d'una acció d'auditoria (camp `reason` d'AuditLog)."""

    GEDCOM_IMPORT = "GEDCOM_IMPORT"
    MANUAL_EDIT = "MANUAL_EDIT"
    MERGE = "MERGE"
    AI_SUGGESTION = "AI_SUGGESTION"
    NORMALIZATION = "NORMALIZATION"


class AuditAction(str, Enum):
    """Accions d'auditoria suportades."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    IMPORT = "import"


__all__ = ["AuditAction", "AuditReason"]
