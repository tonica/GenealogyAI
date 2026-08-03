"""Value object `DateValue`.

Representa una data genealògica amb tota la informació que el domini
necessita: text original, components normalitzats, precisió, modificador
GEDCOM i suport per a intervals. Permet comparar, ordenar, verificar
contenció i solapament de manera determinista i sense depen del parser.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from enum import Enum


class DatePrecision(Enum):
    """Nivell de precisió d'una data."""

    UNKNOWN = 0
    YEAR = 1
    MONTH = 2
    DAY = 3


@dataclass(frozen=True)
class DateValue:
    """Data normalitzada immutable.

    Atributs:
        original_text: text tal com apareix al GEDCOM (traçabilitat).
        iso: representació ISO "YYYY-MM-DD" de l'inici (si és precisa).
        year/month/day: components numèrics de l'inici (None si no es coneixen).
        precision: nivell de precisió de la data.
        modifier: qualificador GEDCOM ("exact", "about", "before", ...).
        normalized_start: ISO de l'inici del període (o None).
        normalized_end: ISO del final del període per a intervals.
    """

    original_text: str | None = None
    iso: str | None = None
    year: int | None = None
    month: int | None = None
    day: int | None = None
    precision: DatePrecision = DatePrecision.UNKNOWN
    modifier: str = "exact"
    normalized_start: str | None = None
    normalized_end: str | None = None

    # ------------------------------------------------------- compatibilitat
    @property
    def original(self) -> str | None:
        """Alias de `original_text` (retrocompatibilitat)."""
        return self.original_text

    @property
    def qualifier(self) -> str:
        """Alias de `modifier` (retrocompatibilitat)."""
        return self.modifier

    @property
    def valid(self) -> bool:
        return self.year is not None or self.iso is not None

    @property
    def as_date(self) -> date | None:
        """Retorna un `datetime.date` de l'inici si hi ha components suficients."""
        if self.iso:
            try:
                return date.fromisoformat(self.iso)
            except ValueError:
                pass
        if self.year is None:
            return None
        return date(self.year, self.month or 1, self.day or 1)

    # ---------------------------------------------------------- sortable
    def _key(self, year: int | None, month: int | None, day: int | None) -> int:
        if year is None:
            return 0
        return year * 10000 + (month or 1) * 100 + (day or 1)

    @property
    def sortable_value(self) -> int:
        """Valor numèric ordenable (any*10000+mes*100+dia)."""
        return self._key(self.year, self.month, self.day)

    def sort_key(self) -> int:
        """Alias de `sortable_value` (retrocompatibilitat)."""
        return self.sortable_value

    @property
    def start_sort(self) -> int:
        return self.sortable_value

    @property
    def end_sort(self) -> int:
        """Final de l'interval (o inici si no és un interval)."""
        if self.normalized_end:
            parts = self.normalized_end.split("-")
            if len(parts) == 3:
                try:
                    y, m, d = (int(x) for x in parts)
                    return self._key(y, m, d)
                except ValueError:
                    pass
        return self.sortable_value

    def __lt__(self, other: "DateValue") -> bool:
        return self.sortable_value < other.sortable_value

    def __le__(self, other: "DateValue") -> bool:
        return self.sortable_value <= other.sortable_value

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DateValue):
            return NotImplemented
        return (
            self.iso == other.iso
            and self.year == other.year
            and self.precision == other.precision
            and self.modifier == other.modifier
        )

    def __hash__(self) -> int:
        return hash((self.iso, self.year, self.precision, self.modifier))

    # ---------------------------------------------------------- intel·ligència
    def is_exact(self) -> bool:
        """És una data exacta (modificador 'exact' i precisió de dia)."""
        return self.modifier == "exact" and self.precision == DatePrecision.DAY

    def is_range(self) -> bool:
        """És un interval (BET/FR. → té final normalitzat)."""
        return self.modifier in {"between", "from"} and self.normalized_end is not None

    def compare(self, other: "DateValue") -> int:
        """Comparació ordenada: -1, 0 o 1."""
        a, b = self.sortable_value, other.sortable_value
        return (a > b) - (a < b)

    def contains(self, other: "DateValue") -> bool:
        """`other` està dins del període d'aquesta data."""
        return self.start_sort <= other.start_sort and other.end_sort <= self.end_sort

    def overlaps(self, other: "DateValue") -> bool:
        """El període d'aquesta data es solapa amb el de `other`."""
        return self.start_sort <= other.end_sort and other.start_sort <= self.end_sort

    # -------------------------------------------------------------- factory
    @classmethod
    def from_iso(cls, iso: str | None) -> "DateValue":
        """Crea un `DateValue` des d'una cadena ISO."""
        if not iso:
            return cls()
        year_s = iso[:4]
        month_s = iso[5:7] if len(iso) >= 7 else None
        day_s = iso[8:10] if len(iso) >= 10 else None

        def _int(s: str | None) -> int | None:
            return int(s) if s and s.isdigit() else None

        year = _int(year_s)
        month = _int(month_s)
        day = _int(day_s)
        if year is None:
            return cls()
        precision = (
            DatePrecision.DAY
            if day
            else (DatePrecision.MONTH if month else DatePrecision.YEAR)
        )
        return cls(
            original_text=iso,
            iso=iso if precision == DatePrecision.DAY else None,
            year=year,
            month=month,
            day=day,
            precision=precision,
            normalized_start=iso if precision == DatePrecision.DAY else None,
            normalized_end=iso if precision == DatePrecision.DAY else None,
        )
