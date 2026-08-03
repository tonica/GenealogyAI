"""Tests del motor de dates (DateEngine) i DateValue ampliat."""

from __future__ import annotations

from app.domain.services.date_engine import DateEngine
from app.domain.value_objects import DatePrecision, DateValue


class TestDateEngine:
    def setup_method(self):
        self.engine = DateEngine()

    def test_year_only(self):
        dv = self.engine.parse("1880")
        assert dv.year == 1880
        assert dv.precision == DatePrecision.YEAR
        assert dv.modifier == "exact"

    def test_month_name(self):
        dv = self.engine.parse("JAN 1880")
        assert dv.year == 1880
        assert dv.month == 1
        assert dv.precision == DatePrecision.MONTH

    def test_full_date(self):
        dv = self.engine.parse("12 JAN 1880")
        assert dv.year == 1880
        assert dv.month == 1
        assert dv.day == 12
        assert dv.precision == DatePrecision.DAY
        assert dv.is_exact()

    def test_about(self):
        dv = self.engine.parse("ABT 1880")
        assert dv.year == 1880
        assert dv.modifier == "about"

    def test_before(self):
        dv = self.engine.parse("BEF 1900")
        assert dv.year == 1900
        assert dv.modifier == "before"

    def test_after(self):
        dv = self.engine.parse("AFT 1850")
        assert dv.year == 1850
        assert dv.modifier == "after"

    def test_between_interval(self):
        dv = self.engine.parse("BET 1880 AND 1900")
        assert dv.modifier == "between"
        assert dv.normalized_start == "1880-01-01"
        assert dv.normalized_end == "1900-01-01"
        assert dv.is_range()

    def test_from_to_interval(self):
        dv = self.engine.parse("FROM 1800 TO 1810")
        assert dv.modifier == "from"
        assert dv.normalized_start == "1800-01-01"
        assert dv.normalized_end == "1810-01-01"

    def test_estimated(self):
        dv = self.engine.parse("EST 1770")
        assert dv.year == 1770
        assert dv.modifier == "estimated"

    def test_calculated(self):
        dv = self.engine.parse("CAL 1960")
        assert dv.year == 1960
        assert dv.modifier == "calculated"

    def test_interpreted(self):
        dv = self.engine.parse("INT 1920")
        assert dv.year == 1920
        assert dv.modifier == "interpreted"

    def test_iso_direct(self):
        dv = self.engine.parse("1893-04-20")
        assert dv.year == 1893
        assert dv.day == 20
        assert dv.iso == "1893-04-20"

    def test_unknown(self):
        dv = self.engine.parse("")
        assert dv is None or not getattr(dv, "valid", False)

    def test_unknown_garbage(self):
        dv = self.engine.parse("no date here")
        assert dv is None or not getattr(dv, "valid", False)


class TestDateValueExtended:
    def test_sortable_value(self):
        a = DateValue(year=1890, precision=DatePrecision.YEAR)
        b = DateValue(year=1900, precision=DatePrecision.YEAR)
        assert a.sortable_value < b.sortable_value
        assert a.start_sort == a.sortable_value

    def test_end_sort_for_interval(self):
        dv = DateValue(
            year=1880,
            normalized_start="1880-01-01",
            normalized_end="1900-01-01",
            modifier="between",
            precision=DatePrecision.YEAR,
        )
        assert dv.end_sort > dv.sortable_value

    def test_compare(self):
        a = DateValue(year=1880, precision=DatePrecision.YEAR)
        b = DateValue(year=1890, precision=DatePrecision.YEAR)
        assert a.compare(b) == -1
        assert b.compare(a) == 1
        assert a.compare(a) == 0

    def test_contains(self):
        outer = DateValue(
            normalized_start="1880-01-01",
            normalized_end="1900-01-01",
            modifier="between",
        )
        inner = DateValue(year=1890, precision=DatePrecision.YEAR)
        assert outer.contains(inner)
        assert not inner.contains(outer)

    def test_overlaps(self):
        a = DateValue(
            normalized_start="1880-01-01",
            normalized_end="1900-01-01",
            modifier="between",
        )
        b = DateValue(year=1885, precision=DatePrecision.YEAR)
        assert a.overlaps(b)
        assert b.overlaps(a)

    def test_not_overlap(self):
        a = DateValue(
            normalized_start="1880-01-01",
            normalized_end="1900-01-01",
            modifier="between",
        )
        b = DateValue(year=1950, precision=DatePrecision.YEAR)
        assert not a.overlaps(b)

    def test_original_and_qualifier_aliases(self):
        dv = DateValue(original_text="ABT 1880", modifier="about")
        assert dv.original == "ABT 1880"
        assert dv.qualifier == "about"

    def test_aliases_backward_compat(self):
        dv = DateValue(year=1900)
        assert dv.sort_key() == dv.sortable_value

    def test_le_comparison(self):
        a = DateValue(year=1880, precision=DatePrecision.YEAR)
        b = DateValue(year=1880, precision=DatePrecision.YEAR)
        assert a <= b
