"""Value object `DateValue`.

Representa una data amb la precisió i les metadades que necessita la
genealogia, sense dependre del parser GEDCOM. Permet comparar i ordenar
dates aproximades de manera determinista i prepara el camp per a intervals.
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
        original: text original del GEDCOM (per traçabilitat).
        iso: representació ISO "YYYY-MM-DD" si és prou precisa.
        year/month/day: components numèrics (None si no es coneixen).
        precision: nivell de precisió de la data.
        qualifier: "exact" | "about" | "before" | "after" | "between" ...
    """

    original: str | None = None
    iso: str | None = None
    year: int | None = None
    month: int | None = None
    day: int | None = None
    precision: DatePrecision = DatePrecision.UNKNOWN
    qualifier: str = "exact"

    # -------------------------------------------------------------- tooling
    @property
    def valid(self) -> bool:
        return self.year is not None or self.iso is not None

    @property
    def as_date(self) -> date | None:
        """Retorna un `datetime.date` si hi ha components suficients."""
        if self.iso:
            try:
                return date.fromisoformat(self.iso)
            except ValueError:
                pass
        if self.year is None:
            return None
        return date(self.year, self.month or 1, self.day or 1)

    # Un valor numèric ordenable: l'any com a base (amb 4 dígits).
    def sort_key(self) -> int:
        if self.year is None:
            return 0
        return self.year

    def __lt__(self, other: "DateValue") -> bool:
        return self.sort_key() < other.sort_key()

    def __le__(self, other: "DateValue") -> bool:
        return self.sort_key() <= other.sort_key()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, DateValue):
            return NotImplemented
        return (
            self.iso == other.iso
            and self.year == other.year
            and self.precision == other.precision
        )

    def __hash__(self) -> int:
        return hash((self.iso, self.year, self.precision))

    @classmethod
    def from_iso(cls, iso: str | None) -> "DateValue":
        """Crea un `DateValue` des d'una cadena ISO (deixa-ho preparat)."""
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
            original=iso,
            iso=iso if precision == DatePrecision.DAY else None,
            year=year,
            month=month,
            day=day,
            precision=precision,
        )
