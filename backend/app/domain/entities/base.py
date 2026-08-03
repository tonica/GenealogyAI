"""Utilitats base per a les entitats del domínio (sense dependències)."""

from __future__ import annotations

import re
import unicodedata


def slugify(value: str | None) -> str | None:
    """Converteix un text en un slug URL-friendly (ex. "Joan Miró" -> "joan-miro")."""
    if not value:
        return None
    text = unicodedata.normalize("NFKD", value)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text or None
