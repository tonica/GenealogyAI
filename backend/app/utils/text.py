"""Normalitzacio de text per a llocs, cognoms i noms.

S'usa per a desduplicar (clau canònica), netejar i presentar (valor
normalitzat per guardar).
"""

from __future__ import annotations

import re

_MULTI_SPACES = re.compile(r"\s+")
_TRAILING_COMMA = re.compile(r"\s*,\s*$")
_DIACRITICS_MAP = str.maketrans(
    "àáâäãåèéêëìíîïòóôöùúûüçñ",
    "aaaaaaeeeeiiiioooouuuucn",
)
_PUNCTUATION = re.compile(r"[’'·.\-]")


def _strip_spaces(text: str) -> str:
    text = _MULTI_SPACES.sub(" ", text)
    text = _TRAILING_COMMA.sub("", text)
    return text.strip()


def normalize_place(name: str | None) -> str | None:
    """Normalitza un nom de lloc per a desduplicacio i emmagatzematge."""
    if name is None:
        return None
    cleaned = _strip_spaces(name)
    if not cleaned:
        return None
    # Elimina accents per a la clau de desduplicacio, mantenint l'original text.
    key = cleaned.translate(_DIACRITICS_MAP).casefold()
    return key or None


def collapse_to_title_case(text: str) -> str:
    return " ".join(
        part.capitalize() if part[:1].isalpha() else part for part in text.split()
    )


def normalize_surname(surname: str | None) -> str | None:
    """Títul a cada token del cognom (DN de/la/los conservant-lo).

    Retorna el cognom 'compact' (sense articles) i la forma títul.
    """
    if surname is None:
        return None
    stem = _PUNCTUATION.sub(" ", surname)
    tokens = [t for t in _MULTI_SPACES.sub(" ", stem).split() if t]
    if not tokens:
        return None
    return " ".join(t.capitalize() for t in tokens)


def surname_key(surname: str | None) -> str:
    """Clau canonica per desduplicar cognoms."""
    if surname is None:
        return ""
    return _strip_spaces(surname).casefold()


def given_name_key(given: str | None) -> str:
    if given is None:
        return ""
    return _strip_spaces(given).casefold()
