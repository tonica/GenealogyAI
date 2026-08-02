"""Normalitzacio de dates GEDCOM.

Les dates GEDCOM 5.5.1 tenen formats molt flexibles: parcials
("10 FEB 1890", "1890", "FEB 1890"), amb qualificadors ("ABT 1890",
"BEF 1900", "AFT JAN 1890") o intervals ("BET 1890 AND 1900"). Aquest
mòdul les descompon en un any i una data ISO (el millor possible) per
poder filtrar i calcular estadístiques.
"""

from __future__ import annotations

from dataclasses import dataclass

_MONTHS = {
    "JAN": 1,
    "FEB": 2,
    "MAR": 3,
    "APR": 4,
    "MAY": 5,
    "JUN": 6,
    "JUL": 7,
    "AUG": 8,
    "SEP": 9,
    "OCT": 10,
    "NOV": 11,
    "DEC": 12,
}

_QUALIFFIERS = {
    "ABT": "about",
    "ABOUT": "about",
    "BEF": "before",
    "BEFORE": "before",
    "AFT": "after",
    "AFTER": "after",
    "BET": "between",
    "BETWEEN": "between",
    "FROM": "from",
    "TO": "to",
    "EST": "estimated",
    "CIR": "estimated",
}

_KEYWORDS = frozenset(set(_QUALIFFIERS.keys()) | {"AND"})


@dataclass
class NormalizedDate:
    """Resultat de la normalitzacio d'una data GEDCOM."""

    original: str
    qualifier: str = "exact"
    year: int | None = None
    month: int | None = None
    day: int | None = None
    iso: str | None = None
    valid: bool = True
    reason: str = ""


def _first_qualifier(tokens: list[str]) -> str:
    for tok in tokens:
        up = tok.upper()
        if up in _QUALIFFIERS:
            return _QUALIFFIERS[up]
    return "exact"


def _clean_year_token(tok: str) -> str:
    return tok.strip(".'")


def _extract_tokens(original: str) -> tuple[str, list[str]]:
    """Retorna el qualificador i els tokens significatius."""
    tokens = original.replace(",", " ").split()
    qual = _first_qualifier(tokens)
    filtered = [
        tok for tok in tokens if tok.upper() not in _KEYWORDS and tok.upper() != "AND"
    ]
    return qual, filtered


def _build_iso(year: int | None, month: int | None, day: int | None) -> str | None:
    if year is None:
        return None
    mm = f"{month:02d}" if month else "01"
    dd = f"{day:02d}" if day else "01"
    return f"{year:04d}-{mm}-{dd}"


def normalize_date(text: str | None) -> NormalizedDate:
    """Converteix un text de data GEDCOM a `NormalizedDate`."""
    if text is None:
        return NormalizedDate("", valid=False, reason="sense valor")

    original = text.strip()
    if not original:
        return NormalizedDate(original, valid=False, reason="data buida")

    qual, filtered = _extract_tokens(original)

    year: int | None = None
    month: int | None = None
    day: int | None = None

    for tok in filtered:
        clean = _clean_year_token(tok)
        if clean.isdigit():
            val = int(clean)
            if val >= 1000:
                year = val
            elif 1 <= val <= 31:
                day = val
        elif len(tok.upper()) == 3 and tok.upper() in _MONTHS:
            month = _MONTHS[tok.upper()]

    nd = NormalizedDate(
        original=original,
        qualifier=qual,
        year=year,
        month=month,
        day=day,
        iso=_build_iso(year, month, day),
    )
    if year is None:
        nd.valid = False
        nd.reason = "format_de_data_no_reconegut"
    return nd
