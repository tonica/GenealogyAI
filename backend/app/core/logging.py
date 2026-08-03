"""Configuració del logging estructurat.

Tota la sortida de logs passa per aquest mòdul:
  - `get_logger(name)` retorna un logger fill del logger arrel.
  - `setup_logging()` s'ha de cridar un cop a l'arrencada de l'aplicació
    (main/entrypoints) per configurar handlers i nivells segons Settings.

No s'ha d'usar `print()` en cap servei: es fa servir `logging` sempre.
"""

from __future__ import annotations

import json
import logging
import logging.config
import sys
from typing import Any

from app.core.config import get_settings


class _JsonFormatter(logging.Formatter):
    """Formata cada registre com una sola línia JSON estructurada."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "ts": self.formatTime(record, "%Y-%m-%dT%H:%M:%S"),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        # Afegeix camps extra passats via extra={} (per exemple metrics).
        for key in ("duration_ms", "persons", "families", "entity_type"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def setup_logging() -> None:
    """Configura els handlers i formats de logging segons "logging" settings."""
    cfg = get_settings().logging
    level = getattr(logging, cfg.level.upper(), logging.INFO)

    formatter: logging.Formatter
    if cfg.format == "json":
        formatter = _JsonFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s: %(message)s"
        )

    handlers: list[logging.Handler] = []
    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(formatter)
    handlers.append(console)

    if cfg.file:
        fh = logging.FileHandler(cfg.file)
        fh.setFormatter(formatter)
        handlers.append(fh)

    logging.basicConfig(level=level, handlers=handlers, force=True)

    # Silenceja logs verbosos de llibreries que no interessen.
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Retorna un logger child del nom "." aplicacio per a un mòdul."""
    return logging.getLogger(f"genealogyai.{name}")


def log_import_summary(logger: logging.Logger, metrics: dict[str, Any]) -> None:
    """Registra un resum d'importació amb el format configurat.

    S'usa un registre amb atributes extres (persons, families...) perquè
    el formatejador JSON els pugui capturar com a camps estructurats.
    """
    logger.info(
        "import-complete persons=%s families=%s sources=%s media=%s "
        "places=%s events=%s issues=%s time_ms=%s",
        metrics.get("persons", 0),
        metrics.get("families", 0),
        metrics.get("sources", 0),
        metrics.get("media", 0),
        metrics.get("places", 0),
        metrics.get("events", 0),
        metrics.get("issues", 0),
        metrics.get("time_ms", 0),
    )
