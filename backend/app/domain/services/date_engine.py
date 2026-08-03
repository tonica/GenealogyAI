"""DateEngine: converteix text GEDCOM en `DateValue`.

El domini mai treballa amb strings de dates: el `DateEngine` és l'únic
punt que tradueix el text GEDCOM a un `DateValue` estructurat.
"""

from __future__ import annotations

import re

from app.domain.value_objects import DatePrecision, DateValue

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

# Modificadors de data GEDCOM 5.5.1.
_MODIFIERS = {
    "ABT": "about",
    "ABOUT": "about",
    "AFT": "after",
    "AFTER": "after",
    "BEF": "before",
    "BEFORE": "before",
    "BET": "between",
    "BETWEEN": "between",
    "FROM": "from",
    "TO": "to",
    "EST": "estimated",
    "CAL": "calculated",
    "INT": "interpreted",
    "PHRASE": "interpreted",
}

_AND = frozenset({"AND"})
_YEAR_RE = re.compile(r"^(?:(\d{1,2})[./-])?(\d{1,2})[./-]?(\d{4})$|^(\d{4})$")
_ISO_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})$")


class DateEngine:
    """Parseja i construeix `DateValue` des de text de data GEDCOM."""

    def parse(self, text: str | None) -> DateValue:
        """Tradueix un text de data GEDCOM a un `DateValue`."""
        if not text:
            return DateValue()

        original = text.strip()
        if not original:
            return DateValue()

        # Els formats ISO directes (p. ex. "1893-04-20").
        iso_match = _ISO_RE.match(original)
        if iso_match:
            return self._from_iso_components(original, *iso_match.groups())

        tokens = original.replace(",", " ").split()
        modifier = "exact"

        # Detecta "BET X AND Y" i "FROM X TO Y" (intervals).
        if len(tokens) >= 4 and tokens[0].upper() in ("BET", "BETWEEN", "FROM"):
            start, end = self._split_interval(tokens)
            if start is not None and end is not None:
                return self._make_interval(
                    original,
                    modifier=_MODIFIERS.get(tokens[0].upper(), tokens[0].lower()),
                    start=start,
                    end=end,
                )

        # Modificador simple ("ABT 1880", "AFT JAN 1880", ...).
        if tokens[0].upper() in _MODIFIERS and tokens[0].upper() not in _AND:
            modifier = _MODIFIERS[tokens[0].upper()]
            tokens = tokens[1:]

        return self._make_single(original, modifier, tokens)

    # ------------------------------------------------------------------
    def _split_interval(
        self, tokens: list[str]
    ) -> tuple[list[str] | None, list[str] | None]:
        """Separa els tokens d'un interval en (inici, final)."""
        upper = [t.upper() for t in tokens]
        sep = -1
        for i, tok in enumerate(upper):
            if tok in ("AND", "TO") and i > 0:
                sep = i
                break
        if sep == -1 or sep == len(tokens) - 1:
            return None, None
        return tokens[1:sep], tokens[sep + 1 :]

    def _make_interval(
        self,
        original: str,
        modifier: str,
        start: list[str],
        end: list[str],
    ) -> DateValue:
        start_dv = self._parse_date_tokens(start)
        end_dv = self._parse_date_tokens(end)
        start_iso = start_dv.iso or self._build_iso_from_dv(start_dv)
        end_iso = end_dv.iso or self._build_iso_from_dv(end_dv)
        return DateValue(
            original_text=original,
            iso=start_iso,
            year=start_dv.year,
            month=start_dv.month,
            day=start_dv.day,
            precision=start_dv.precision,
            modifier=modifier,
            normalized_start=start_iso,
            normalized_end=end_iso,
        )

    def _make_single(
        self, original: str, modifier: str, tokens: list[str]
    ) -> DateValue:
        parsed = self._parse_date_tokens(tokens)
        return DateValue(
            original_text=original,
            iso=parsed.iso,
            year=parsed.year,
            month=parsed.month,
            day=parsed.day,
            precision=parsed.precision,
            modifier=modifier,
            normalized_start=parsed.iso,
            normalized_end=parsed.iso,
        )

    def _parse_date_tokens(self, tokens: list[str]) -> DateValue:
        """Extreu day/month/year d'una llista de tokens."""
        year: int | None = None
        month: int | None = None
        day: int | None = None

        for tok in tokens:
            up = tok.upper()
            if up in _MONTHS:
                month = _MONTHS[up]
                continue
            clean = tok.strip(".'")
            if clean.isdigit():
                val = int(clean)
                if val >= 1000:
                    year = val
                elif 1 <= val <= 31:
                    day = val
            else:
                # Formats complets "12/10/1880" o "12.10.1880".
                m = _YEAR_RE.match(clean)
                if m:
                    year = int(m.group(4) or m.group(3))
                    if m.group(1):
                        day = int(m.group(1))
                        month = int(m.group(2))

        if year is None:
            return DateValue(precision=DatePrecision.UNKNOWN)

        precision = (
            DatePrecision.DAY
            if day and month
            else (DatePrecision.MONTH if month else DatePrecision.YEAR)
        )
        iso = self._build_iso(year, month, day)
        return DateValue(
            iso=iso if precision == DatePrecision.DAY else None,
            year=year,
            month=month,
            day=day,
            precision=precision,
            normalized_start=iso if precision == DatePrecision.DAY else None,
            normalized_end=iso if precision == DatePrecision.DAY else None,
        )

    @staticmethod
    def _from_iso_components(original: str, y: str, m: str, d: str) -> DateValue:
        return DateValue(
            original_text=original,
            iso=original,
            year=int(y),
            month=int(m),
            day=int(d),
            precision=DatePrecision.DAY,
            normalized_start=original,
            normalized_end=original,
        )

    @staticmethod
    def _build_iso(year: int, month: int | None, day: int | None) -> str:
        mm = f"{month:02d}" if month else "01"
        dd = f"{day:02d}" if day else "01"
        return f"{year:04d}-{mm}-{dd}"

    @staticmethod
    def _build_iso_from_dv(dv: DateValue) -> str | None:
        if dv.year is None:
            return None
        return DateEngine._build_iso(dv.year, dv.month, dv.day)
