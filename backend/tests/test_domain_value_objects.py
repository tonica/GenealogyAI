"""Tests de value objects del domínio (sense cap infraestructura).

No es crea cap SQLite aquí; només objectes Python purs.
"""

from __future__ import annotations


from app.domain.value_objects import DatePrecision, DateValue, PersonName, PlaceName


class TestDateValue:
    def test_from_iso_day(self):
        d = DateValue.from_iso("1893-04-20")
        assert d.year == 1893
        assert d.month == 4
        assert d.day == 20
        assert d.precision == DatePrecision.DAY
        assert d.as_date is not None
        assert d.as_date.year == 1893

    def test_from_iso_year_only(self):
        d = DateValue.from_iso("1900")
        assert d.year == 1900
        assert d.precision == DatePrecision.YEAR
        assert d.month is None

    def test_from_iso_empty(self):
        d = DateValue.from_iso(None)
        assert not d.valid
        assert d.year is None

    def test_comparison_by_sort_key(self):
        a = DateValue(year=1890, precision=DatePrecision.YEAR)
        b = DateValue(year=1900, precision=DatePrecision.YEAR)
        assert a < b
        assert b > a
        assert b.sort_key() > a.sort_key()

    def test_equality(self):
        a = DateValue(year=1900, precision=DatePrecision.YEAR)
        b = DateValue(year=1900, precision=DatePrecision.YEAR)
        assert a == b
        assert hash(a) == hash(b)


class TestPersonName:
    def test_full_name(self):
        n = PersonName(given="Joan", middle="X", surnames="Miró")
        assert n.full_name == "Joan X Miró"

    def test_slug_generated(self):
        n = PersonName(given="Joan", surnames="Miró")
        assert n.slug == "joan-miro"

    def test_empty(self):
        n = PersonName()
        assert n.full_name == ""

    def test_from_given_surname(self):
        n = PersonName.from_given_surname("Anna", "Puig")
        assert n.given == "Anna"
        assert n.surnames == "Puig"


class TestPlaceName:
    def test_display_and_canonical(self):
        p = PlaceName(name="Barcelona", country="ES")
        assert p.display == "Barcelona"
        assert p.canonical == "barcelona"
        assert p.slug == "barcelona"

    def test_hierarchy_fields(self):
        p = PlaceName(name="Pobla", province="BCN")
        assert p.province == "BCN"
