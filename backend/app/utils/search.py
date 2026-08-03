"""Utils per a la preparació de camps de cerca (slug, soundex, metaphone).

Només es prepara la infraestructura: els algorithms de fonetica es
proporcionen com a serveis separats (`app.services.search`) i de moment es
retornen valors estables i deterministes.
"""

from __future__ import annotations

import re
import unicodedata

_from_slug_chars = re.compile(r"[^a-z0-9]+")


def slugify(text: str | None, max_length: int = 120) -> str | None:
    """Converteix text en un slug URL-friendly (lowercase, accents trets)."""
    if text is None:
        return None
    text = unicodedata.normalize("NFKD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.lower()
    text = _from_slug_chars.sub("-", text).strip("-")
    return text[:max_length] or None


def build_search_name(given_name: str | None, surname: str | None) -> str:
    """Concatena nom i cognoms per a la cerca full-text."""
    parts = [p for p in (given_name, surname) if p]
    return " ".join(parts).strip()
