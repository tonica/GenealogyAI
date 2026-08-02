"""Tests de normalitzacio de dates."""

import pytest

from app.utils.dates import normalize_date


def test_full_gedcom_date():
    nd = normalize_date("10 FEB 1890")
    assert nd.year == 1890
    assert nd.month == 2
    assert nd.day == 10
    assert nd.iso == "1890-02-10"
    assert nd.valid


def test_year_only():
    nd = normalize_date("1850")
    assert nd.year == 1850
    assert nd.iso == "1850-01-01"
    assert nd.day is None


def test_month_and_year():
    nd = normalize_date("MAR 1700")
    assert nd.month == 3
    assert nd.year == 1700
    assert nd.iso == "1700-03-01"


def test_about_qualifier():
    nd = normalize_date("ABT 1805")
    assert nd.qualifier == "about"
    assert nd.year == 1805


def test_before_after():
    before = normalize_date("BEF JAN 1800")
    assert before.qualifier == "before"
    assert before.year == 1800
    after = normalize_date("AFT 5 APR 1856")
    assert after.qualifier == "after"
    assert after.year == 1856


def test_should_ignore_and_keyword():
    nd = normalize_date("BET 1800 AND 1820")
    assert nd.qualifier == "between"
    assert nd.year == 1820


def test_invalid_date():
    nd = normalize_date("great-grandmother")
    assert not nd.valid
    assert nd.year is None


def test_none_and_empty():
    assert not normalize_date(None).valid
    assert not normalize_date("").valid


@pytest.mark.parametrize(
    "text,expected",
    [
        ("8 MAY 1800", 1800),
        ("JUL 1800", 1800),
        ("EST 1999", 1999),
        ("CAL 1500", 1500),
    ],
)
def test_parametrized_years(text, expected):
    assert normalize_date(text).year == expected
